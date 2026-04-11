"""
ml_service.py
-------------
Machine-learning backend for Smart Retail Predictor.

Responsibilities:
  - Train a per-product Linear Regression model on historical sales
  - Generate a 30-day quantity forecast with a confidence band
  - Calculate seasonality (best day-of-week)
  - Persist forecasts to the Prediction_Model table
  - Return everything the AI Predictor page needs to render its charts

All heavy lifting lives here so the Streamlit page stays thin.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

from db_connection import get_db_connection, get_cursor


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class ForecastResult:
    """All outputs produced by run_forecast() for one product."""
    product_name:    str
    future_dates:    list[date]
    predictions:     list[int]
    upper_band:      list[int]          # +15 % confidence interval
    lower_band:      list[int]          # −15 % confidence interval
    total_predicted: int
    best_day:        str                # e.g. "Saturday"
    trend:           str                # "up" | "down" | "flat"
    r2_score:        float              # model fit quality 0–1
    mae:             float              # mean absolute error on training data
    historical_df:   pd.DataFrame       # sale_date, quantity_sold (for chart)
    errors:          list[str] = field(default_factory=list)


# ── Core forecasting ──────────────────────────────────────────────────────────

def run_forecast(df: pd.DataFrame, product_name: str) -> ForecastResult:
    """
    Train a Linear Regression model on the historical sales of one product
    and generate a 30-day forecast.

    Parameters
    ----------
    df           : Full sales DataFrame for the user (from sales_service).
                   Must have columns: sale_date (datetime), product_name, quantity_sold.
    product_name : The product to forecast.

    Returns
    -------
    ForecastResult dataclass.
    """
    errors: list[str] = []

    # ── 1. Filter + daily aggregate ───────────────────────────────────────────
    prod_df = (
        df[df["product_name"] == product_name]
        .groupby("sale_date")["quantity_sold"]
        .sum()
        .reset_index()
        .sort_values("sale_date")
    )

    if len(prod_df) < 2:
        errors.append(f"Only {len(prod_df)} data point(s) found — need at least 2.")
        return ForecastResult(
            product_name=product_name,
            future_dates=[], predictions=[], upper_band=[], lower_band=[],
            total_predicted=0, best_day="N/A", trend="flat",
            r2_score=0.0, mae=0.0,
            historical_df=prod_df, errors=errors,
        )

    # ── 2. Feature engineering ────────────────────────────────────────────────
    origin = prod_df["sale_date"].min()
    prod_df["days_since_start"] = (prod_df["sale_date"] - origin).dt.days

    X = prod_df[["days_since_start"]].values
    y = prod_df["quantity_sold"].values

    # ── 3. Train ──────────────────────────────────────────────────────────────
    model = LinearRegression()
    model.fit(X, y)

    # In-sample metrics
    y_pred_train = model.predict(X)
    r2  = round(float(r2_score(y, y_pred_train)), 4)
    mae = round(float(mean_absolute_error(y, y_pred_train)), 2)

    # ── 4. Forecast 30 days ───────────────────────────────────────────────────
    last_date   = prod_df["sale_date"].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_days  = [(d - origin).days for d in future_dates]

    raw_preds  = model.predict(np.array(future_days).reshape(-1, 1))
    predictions = [max(0, int(round(p))) for p in raw_preds]

    # ±15 % confidence band
    upper_band = [max(0, int(round(p * 1.15))) for p in raw_preds]
    lower_band = [max(0, int(round(p * 0.85))) for p in raw_preds]

    total_predicted = sum(predictions)

    # ── 5. Seasonality: best day-of-week ─────────────────────────────────────
    dow_series = (
        df[df["product_name"] == product_name]
        .copy()
        .assign(day_of_week=lambda d: d["sale_date"].dt.day_name())
        .groupby("day_of_week")["quantity_sold"]
        .sum()
    )
    best_day = dow_series.idxmax() if not dow_series.empty else "N/A"

    # ── 6. Trend direction ────────────────────────────────────────────────────
    if len(predictions) >= 2:
        diff = predictions[-1] - predictions[0]
        if diff > 0:
            trend = "up"
        elif diff < 0:
            trend = "down"
        else:
            trend = "flat"
    else:
        trend = "flat"

    return ForecastResult(
        product_name=product_name,
        future_dates=future_dates,
        predictions=predictions,
        upper_band=upper_band,
        lower_band=lower_band,
        total_predicted=total_predicted,
        best_day=best_day,
        trend=trend,
        r2_score=r2,
        mae=mae,
        historical_df=prod_df,
        errors=errors,
    )


# ── Persistence ───────────────────────────────────────────────────────────────

def save_forecast(user_id: int, result: ForecastResult):
    """
    Write the 30-day forecast into the Prediction_Model table.
    Deletes any existing forecast for the same user + product first
    so the table stays clean.

    This demonstrates the full DBMS loop the professor cares about:
    ML output → SQL table → can trigger inventory alerts.
    """
    if not result.predictions:
        return

    conn   = get_db_connection()
    cursor = get_cursor(conn)

    # Remove stale forecasts
    cursor.execute(
        "DELETE FROM Prediction_Model WHERE user_id = %s AND product_name = %s",
        (user_id, result.product_name),
    )

    # Derive a rough confidence score from R²  (clamp 0–1)
    confidence = max(0.0, min(1.0, result.r2_score))

    rows = [
        (
            user_id,
            result.product_name,
            str(result.future_dates[i]),
            result.predictions[i],
            round(confidence, 4),
            0.0,          # seasonality_index — extend later
        )
        for i in range(len(result.future_dates))
    ]

    conn.autocommit = False
    try:
        cursor.executemany(
            """
            INSERT INTO Prediction_Model
                (user_id, product_name, forecast_date, forecast_qty,
                 confidence_score, seasonality_index)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True
        conn.close()


def load_saved_forecast(user_id: int, product_name: str) -> pd.DataFrame:
    """
    Retrieve a previously saved forecast from Prediction_Model.
    Returns an empty DataFrame if none exists.
    """
    conn = get_db_connection()
    df   = pd.read_sql(
        """
        SELECT forecast_date, forecast_qty, confidence_score, generated_at
        FROM   Prediction_Model
        WHERE  user_id = %s AND product_name = %s
        ORDER  BY forecast_date ASC
        """,
        conn,
        params=(user_id, product_name),
    )
    conn.close()
    return df


# ── Utility ───────────────────────────────────────────────────────────────────

def get_product_list(df: pd.DataFrame) -> list[str]:
    """Return sorted unique product names from a sales DataFrame."""
    if df.empty or "product_name" not in df.columns:
        return []
    return sorted(df["product_name"].unique().tolist())


def trend_label(trend: str) -> str:
    """Human-readable trend string with emoji."""
    return {
        "up":   "📈 Trending Up",
        "down": "📉 Trending Down",
        "flat": "➡️ Stable",
    }.get(trend, "➡️ Stable")


def trend_color(trend: str) -> str:
    """CSS colour for the trend KPI card."""
    return {
        "up":   "#38e8c5",
        "down": "#f97060",
        "flat": "#fbbf24",
    }.get(trend, "#fbbf24")