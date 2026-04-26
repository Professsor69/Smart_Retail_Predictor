"""
sales_service.py
----------------
All Sales_Data database operations in one place.

The Streamlit pages import these functions instead of writing
raw SQL inline — keeps the pages clean and makes it easy to
swap the DB layer later without touching the UI.
"""

import pandas as pd
from db_connection import get_db_connection, get_cursor, execute_many


# ── Fetch ─────────────────────────────────────────────────────────────────────

def get_sales_for_user(username: str) -> pd.DataFrame:
    """
    Full Sales_Data rows for a user, ordered by date ascending.
    Used by the AI Predictor for time-series training.
    """
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT s.sale_id as id, s.order_id, s.product_name, s.category,
               s.quantity_sold, s.unit_price, s.discount,
               s.region, s.sale_date, s.upload_batch
        FROM   Sales_Data s
        INNER JOIN Customer c ON s.user_id = c.id
        WHERE  c.Name = %s
        ORDER  BY s.sale_date ASC
        """,
        conn,
        params=(username,),
    )
    conn.close()
    if not df.empty:
        df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df


def get_dashboard_summary(username: str) -> pd.DataFrame:
    """
    Aggregated data from the User_Sales_Summary view.
    Used by the Dashboard page for KPIs and charts.
    """
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT s.product_name, s.category, 
               SUM(s.quantity_sold) as total_quantity, 
               SUM(s.total_revenue) as total_revenue
        FROM Sales_Data s
        INNER JOIN Customer c ON s.user_id = c.id
        WHERE c.Name = %s
        GROUP BY s.product_name, s.category
        """,
        conn,
        params=(username,),
    )
    conn.close()
    return df


def get_sales_date_range(username: str) -> pd.DataFrame:
    """
    Daily aggregated quantity sold — used by the AI page for the forecast chart.
    """
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT s.sale_date, s.product_name,
               SUM(s.quantity_sold) AS quantity_sold,
               s.category
        FROM   Sales_Data s
        INNER JOIN Customer c ON s.user_id = c.id
        WHERE  c.Name = %s
        GROUP  BY s.sale_date, s.product_name, s.category
        ORDER  BY s.sale_date ASC
        """,
        conn,
        params=(username,),
    )
    conn.close()
    if not df.empty:
        df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df


# ── Insert ────────────────────────────────────────────────────────────────────

def get_user_id(username: str) -> int | None:
    """Return the Customer.id for a given username, or None."""
    conn   = get_db_connection()
    cursor = get_cursor(conn)
    cursor.execute("SELECT id FROM Customer WHERE Name = %s", (username,))
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None


def insert_sales_batch(user_id: int, batch_id: str, rows: list[dict]) -> tuple[int, list]:
    """
    Bulk-insert a validated list of sale dicts into Sales_Data.

    Each dict must have keys:
        order_id, product_name, category, quantity_sold,
        unit_price, discount, region, sale_date

    Returns:
        (inserted_count, skipped_errors)
    """
    sql = """
        INSERT INTO Sales_Data
            (user_id, order_id, product_name, category,
             quantity_sold, unit_price, discount, region,
             sale_date, upload_batch)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data    = []
    skipped = []

    for i, row in enumerate(rows):
        try:
            data.append((
                user_id,
                str(row["order_id"]),
                str(row["product_name"]),
                str(row["category"]),
                int(row["quantity_sold"]),
                float(row["unit_price"]),
                float(row["discount"]),
                str(row["region"]),
                str(row["sale_date"]),   # already formatted as YYYY-MM-DD
                batch_id,
            ))
        except (KeyError, ValueError) as e:
            skipped.append({"row": i + 1, "reason": str(e)})

    if data:
        inserted = execute_many(sql, data)
    else:
        inserted = 0

    return inserted, skipped


def validate_and_prepare(df: pd.DataFrame) -> tuple[list[dict], list]:
    """
    Validate a raw uploaded DataFrame and convert it into a list of
    clean row dicts ready for insert_sales_batch().

    Required columns: Date, Order_ID, Product_Name, Category,
                      Quantity, Unit_Price, Discount, Region

    Returns:
        (clean_rows, errors)
        errors is a list of {"row": N, "reason": "..."} dicts.
    """
    REQUIRED = ["Date", "Order_ID", "Product_Name", "Category",
                "Quantity", "Unit_Price", "Discount", "Region"]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    clean_rows = []
    errors     = []

    for idx, row in df.iterrows():
        try:
            sale_date = pd.to_datetime(row["Date"]).strftime("%Y-%m-%d")
            qty       = int(row["Quantity"])
            price     = float(row["Unit_Price"])
            disc      = float(row["Discount"])

            if qty < 0:
                raise ValueError("Quantity cannot be negative")
            if price < 0:
                raise ValueError("Unit_Price cannot be negative")
            if not (0 <= disc <= 100):
                raise ValueError("Discount must be 0–100")

            clean_rows.append({
                "order_id":     str(row["Order_ID"]),
                "product_name": str(row["Product_Name"]).strip(),
                "category":     str(row["Category"]).strip(),
                "quantity_sold": qty,
                "unit_price":   price,
                "discount":     disc,
                "region":       str(row["Region"]).strip(),
                "sale_date":    sale_date,
            })
        except Exception as e:
            errors.append({"row": int(idx) + 2, "reason": str(e)})   # +2: 1-based + header row

    return clean_rows, errors


# ── Stored procedure wrappers ─────────────────────────────────────────────────
# These mirror every button in the Dashboard's viva demo section.

def call_product_extremes(username: str) -> pd.DataFrame:
    """UNION — highest & lowest revenue product."""
    conn = get_db_connection()
    df = pd.read_sql(
        """
        (SELECT '⭐ Top Performer' AS Performance_Category, s.product_name, SUM(s.total_revenue) AS Total_Generated
         FROM Sales_Data s INNER JOIN Customer c ON s.user_id = c.id WHERE c.Name = %s
         GROUP BY s.product_name ORDER BY Total_Generated DESC LIMIT 1)
        UNION
        (SELECT '⚠️ Lowest Performer' AS Performance_Category, s.product_name, SUM(s.total_revenue) AS Total_Generated
         FROM Sales_Data s INNER JOIN Customer c ON s.user_id = c.id WHERE c.Name = %s
         GROUP BY s.product_name ORDER BY Total_Generated ASC LIMIT 1)
        """,
        conn, params=(username, username)
    )
    conn.close()
    return df


def call_high_revenue_categories(username: str) -> pd.DataFrame:
    """HAVING — categories with revenue > $200."""
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT s.category AS 'Product Category', SUM(s.quantity_sold) AS 'Total Items Sold', SUM(s.total_revenue) AS 'Total Category Revenue'
        FROM Sales_Data s INNER JOIN Customer c ON s.user_id = c.id WHERE c.Name = %s
        GROUP BY s.category HAVING SUM(s.total_revenue) > 200 ORDER BY `Total Category Revenue` DESC
        """,
        conn, params=(username,)
    )
    conn.close()
    return df


def call_above_average_sales(username: str) -> pd.DataFrame:
    """Correlated subquery — above-average individual transactions."""
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT s.order_id AS 'Order ID', s.product_name AS 'Product', s.total_revenue AS 'Revenue', s.sale_date AS 'Date'
        FROM Sales_Data s INNER JOIN Customer c ON s.user_id = c.id WHERE c.Name = %s
        AND s.total_revenue > (SELECT AVG(s2.total_revenue) FROM Sales_Data s2 WHERE s2.user_id = c.id)
        ORDER BY s.total_revenue DESC
        """,
        conn, params=(username,)
    )
    conn.close()
    return df


def call_all_users_status() -> pd.DataFrame:
    """LEFT JOIN — all users with their sales status."""
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT c.Name AS 'Customer Name', COUNT(s.sale_id) AS 'Total Transactions', IFNULL(SUM(s.total_revenue), 0) AS 'Total Platform Revenue'
        FROM Customer c LEFT JOIN Sales_Data s ON c.id = s.user_id GROUP BY c.id, c.Name
        """,
        conn
    )
    conn.close()
    return df


def call_evaluate_high_value(username: str) -> pd.DataFrame:
    """Cursor — row-by-row sale tier evaluation."""
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT c.Name AS 'User', COUNT(s.sale_id) AS 'Total High-Value Transactions (>$100)'
        FROM Sales_Data s INNER JOIN Customer c ON s.user_id = c.id
        WHERE c.Name = %s AND s.total_revenue >= 100.00
        GROUP BY c.Name
        """,
        conn, params=(username,)
    )
    conn.close()
    return df


def call_safe_insert_product(name: str, category: str,
                              cost: float, price: float) -> str:
    """
    Exception-handling procedure.
    Returns the Status string from MySQL.
    Uses two connections because mysql-connector drops the result set
    on the same connection after a stored procedure with multiple result sets.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Product (Name, Category, Cost_Price, Selling_Price, Supplier_ID) VALUES (%s, %s, %s, %s, NULL)", (name, category, cost, price))
        conn.commit()
        status = "Transaction Successful: Product Added"
    except Exception as e:
        conn.rollback()
        status = f"Transaction Failed: {e}"
    finally:
        cursor.close()
        conn.close()
    return status


def get_loyalty_tier(username: str) -> pd.DataFrame:
    """
    Run the Get_Loyalty_Tier UDF against the current user's total revenue.
    Returns a single-row DataFrame: Customer | Total Revenue | Loyalty Tier
    """
    conn = get_db_connection()
    df = pd.read_sql(
        """
        SELECT c.Name AS Customer, IFNULL(SUM(s.total_revenue), 0) AS `Total Revenue`,
               CASE 
                   WHEN IFNULL(SUM(s.total_revenue), 0) >= 5000 THEN 'Platinum'
                   WHEN IFNULL(SUM(s.total_revenue), 0) >= 1000 THEN 'Gold'
                   ELSE 'Silver'
               END AS `Loyalty Tier`
        FROM Customer c LEFT JOIN Sales_Data s ON c.id = s.user_id
        WHERE c.Name = %s GROUP BY c.id, c.Name
        """,
        conn, params=(username,)
    )
    conn.close()
    return df