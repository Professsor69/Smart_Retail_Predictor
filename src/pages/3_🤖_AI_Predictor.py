import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Sales Predictor", page_icon="🤖", layout="wide")

# 2. PREMIUM THEME
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --bg-void: #03040a;
        --surface-1: rgba(255,255,255,0.03);
        --surface-2: rgba(255,255,255,0.06);
        --border: rgba(255,255,255,0.08);
        --border-bright: rgba(255,255,255,0.14);
        --accent-primary: #7c6dfa;
        --accent-secondary: #38e8c5;
        --accent-gold: #f97316;
        --text-primary: #f0f0f8;
        --text-secondary: #8b8b9e;
        --glow-purple: rgba(124,109,250,0.35);
        --glow-teal: rgba(56,232,197,0.25);
    }

    html, body, .stApp {
        background-color: var(--bg-void) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,109,250,0.14) 0%, transparent 60%),
            radial-gradient(ellipse 40% 30% at 90% 100%, rgba(56,232,197,0.07) 0%, transparent 60%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none'%3E%3Cg fill='%23ffffff' fill-opacity='0.012'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(3,4,10,0.92) !important;
        border-right: 1px solid var(--border-bright) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(124,109,250,0.12) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a:hover span { color: var(--text-primary) !important; }

    footer { display: none !important; }

    .block-container {
        padding: 4.5rem 2.5rem 2rem 2.5rem !important;
        max-width: 1200px !important;
    }

    /* ── PAGE HEADER ── */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid var(--border);
    }
    .page-header-left { display: flex; align-items: center; gap: 14px; }
    .page-icon {
        width: 48px; height: 48px;
        background: linear-gradient(135deg, #a78bfa, var(--accent-primary));
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 20px rgba(167,139,250,0.4);
        flex-shrink: 0;
    }
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.8px;
        margin: 0;
    }
    .page-subtitle { font-size: 13px; color: var(--text-secondary); margin: 2px 0 0 0; }
    .user-badge {
        display: flex; align-items: center; gap: 10px;
        background: var(--surface-2); border: 1px solid var(--border-bright);
        border-radius: 40px; padding: 8px 16px; font-size: 13px; color: var(--text-secondary);
    }
    .user-badge strong { color: var(--text-primary); }

    /* ── METRIC CARDS ── */
    .metric-card {
        background: var(--surface-1);
        border: 1px solid var(--border-bright);
        border-radius: 20px;
        padding: 24px 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        opacity: 0.7;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(124,109,250,0.1);
    }
    .metric-icon { font-size: 22px; margin-bottom: 12px; display: block; }
    .metric-label {
        font-size: 11px; font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 28px; font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -1px; line-height: 1;
    }
    .metric-value.accent-teal { color: var(--accent-secondary); }
    .metric-value.accent-gold { color: var(--accent-gold); }

    /* ── SELECTBOX ── */
    [data-baseweb="select"] > div {
        background: var(--surface-1) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    [data-baseweb="select"] > div:hover { border-color: var(--accent-primary) !important; }
    [data-baseweb="select"] span { color: var(--text-primary) !important; }

    /* ── SECTION ── */
    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 16px; font-weight: 700;
        color: var(--text-primary); letter-spacing: -0.3px; margin-bottom: 4px;
    }
    .section-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; }

    /* ── ARCHITECT NOTE ── */
    .arch-note {
        background: rgba(124,109,250,0.06);
        border: 1px solid rgba(124,109,250,0.2);
        border-radius: 14px;
        padding: 16px 20px;
        display: flex; gap: 12px; align-items: flex-start;
        margin-top: 1rem;
    }
    .arch-note-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
    .arch-note-text { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
    .arch-note-text strong { color: var(--text-primary); }

    /* ── ALERTS ── */
    [data-testid="stSuccess"] {
        background: rgba(56,232,197,0.06) !important;
        border: 1px solid rgba(56,232,197,0.3) !important;
        border-radius: 12px !important;
    }
    [data-testid="stError"] {
        background: rgba(249,112,96,0.06) !important;
        border: 1px solid rgba(249,112,96,0.3) !important;
        border-radius: 12px !important;
    }
    [data-testid="stInfo"] {
        background: rgba(124,109,250,0.06) !important;
        border: 1px solid rgba(124,109,250,0.25) !important;
        border-radius: 12px !important;
    }
    [data-testid="stWarning"] {
        background: rgba(251,191,36,0.06) !important;
        border: 1px solid rgba(251,191,36,0.25) !important;
        border-radius: 12px !important;
    }

    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
    p, label, li { color: var(--text-secondary) !important; font-family: 'DM Sans', sans-serif !important; }
    h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: var(--text-primary) !important; }
    
    /* Force Material Icons to retain their original font-family avoiding global override */
    span[class*="material-symbols"], span[class*="icon"], i, .material-icons {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. SECURITY CHECK
if not st.session_state.get('authenticated'):
    st.warning("🔒 Please log in to access the AI Predictor.")
    st.stop()

current_user = st.session_state['user_name']

# 4. PAGE HEADER
st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon">🤖</div>
            <div>
                <div class="page-title">AI Demand Forecasting</div>
                <div class="page-subtitle">Machine learning trained from historical dataset modeling</div>
            </div>
        </div>
        <div class="user-badge">👤 &nbsp;<strong>{{current_user}}</strong></div>
    </div>
""", unsafe_allow_html=True)

# 5. FETCH DATA (USER & KAGGLE MODELING)
@st.cache_data(ttl=10)
def get_user_data(username):
    conn = get_db_connection()
    query = """
        SELECT s.sale_date, s.product_name, s.quantity_sold, s.category
        FROM Sales_Data s
        INNER JOIN Customer c ON s.user_id = c.id
        WHERE c.Name = %s
        ORDER BY s.sale_date ASC
    """
    df = pd.read_sql(query, conn, params=(username,))
    conn.close()
    return df

@st.cache_data(ttl=3600)
def get_kaggle_model_data():
    try:
        df = pd.read_csv("Smart_Retail_Ready_Superstore.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()

with st.spinner("Initializing ML Models and Connecting Data..."):
    user_df = get_user_data(current_user)
    kaggle_df = get_kaggle_model_data()

if user_df.empty:
    st.error("Not enough data to run predictions. Please upload data in the Data Ingestion Hub first.")
    st.stop()

user_df['sale_date'] = pd.to_datetime(user_df['sale_date'])

if not kaggle_df.empty:
    kaggle_df['Date'] = pd.to_datetime(kaggle_df['Date'])

# 6. PRODUCT SELECTION
st.markdown('<div class="section-label">🎯 Select a Product to Forecast</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Choose a product from your DBMS dataset. The AI will use external data to train the model, predicting onto your SQL data.</div>', unsafe_allow_html=True)

products = user_df['product_name'].unique()
selected_product = st.selectbox("Product", products, label_visibility="collapsed")

user_prod_df = user_df[user_df['product_name'] == selected_product].groupby('sale_date')['quantity_sold'].sum().reset_index()

st.markdown("<hr>", unsafe_allow_html=True)

# 7. MACHINE LEARNING LOGIC
if len(user_prod_df) < 2:
    st.warning(f"⚠️ Need more historical data in the database for **{selected_product}** to start predicting.")
else:
    # Look for Kaggle Training Data for the ML Model
    if not kaggle_df.empty and selected_product in kaggle_df['Product_Name'].values:
        train_df = kaggle_df[kaggle_df['Product_Name'] == selected_product].groupby('Date')['Quantity'].sum().reset_index()
        train_date_col = 'Date'
        train_qty_col = 'Quantity'
        model_source = "Kaggle Dataset"
    else:
        # Fallback to User Data for training if product isn't in Kaggle Data
        train_df = user_prod_df.copy()
        train_date_col = 'sale_date'
        train_qty_col = 'quantity_sold'
        model_source = "User Database"

    origin_date = train_df[train_date_col].min()
    train_df['Days_Since_Start'] = (train_df[train_date_col] - origin_date).dt.days

    X = train_df[['Days_Since_Start']]
    y = train_df[train_qty_col]

    # Train Model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future based on User's max date
    last_user_date = user_prod_df['sale_date'].max()
    future_dates = [last_user_date + timedelta(days=i) for i in range(1, 31)]
    future_days_since = [(d - origin_date).days for d in future_dates]

    future_X = pd.DataFrame({'Days_Since_Start': future_days_since})
    predictions = model.predict(future_X)
    predictions = [max(0, int(round(p))) for p in predictions]

    user_df['Day_of_Week'] = user_df['sale_date'].dt.day_name()
    best_day = user_df[user_df['product_name'] == selected_product].groupby('Day_of_Week')['quantity_sold'].sum().idxmax()

    total_predicted = sum(predictions)
    trend = "📈 Trending Up" if predictions[-1] > predictions[0] else "📉 Trending Down"

    # 8. KPI CARDS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">📦</span>
                <div class="metric-label">30-Day Forecast</div>
                <div class="metric-value accent-teal">{total_predicted:,} units</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">🎓</span>
                <div class="metric-label">Trained From</div>
                <div class="metric-value" style="font-size:20px;">{model_source}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <span class="metric-icon">📊</span>
                <div class="metric-label">Overall Trend</div>
                <div class="metric-value accent-gold" style="font-size:18px;">{trend}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 9. FORECAST CHART
    st.markdown(f'<div class="section-label">📈 30-Day Sales Trajectory — {selected_product}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Your SQL actuals (solid) vs. AI-generated forecast trained on external data (dashed)</div>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=user_prod_df['sale_date'], y=user_prod_df['quantity_sold'],
        mode='lines+markers', name='Your DB Sales',
        line=dict(color='#7c6dfa', width=3),
        marker=dict(size=6, color='#7c6dfa', line=dict(color='rgba(124,109,250,0.3)', width=4)),
    ))

    fig.add_trace(go.Scatter(
        x=future_dates, y=predictions,
        mode='lines+markers', name='AI Forecast',
        line=dict(color='#38e8c5', width=3, dash='dot'),
        marker=dict(size=6, color='#38e8c5', line=dict(color='rgba(56,232,197,0.3)', width=4)),
        fill='tozeroy',
        fillcolor='rgba(56,232,197,0.04)',
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Date",
        yaxis_title="Quantity Sold",
        hovermode="x unified",
        font=dict(family='DM Sans', color='#8b8b9e'),
        legend=dict(
            orientation='h',
            yanchor='bottom', y=1.02,
            xanchor='right', x=1,
            font=dict(color='#8b8b9e'),
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.06)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.06)'),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)

    # 10. ARCHITECTURE NOTE
    st.markdown("""
        <div class="arch-note">
            <div class="arch-note-icon">💡</div>
            <div class="arch-note-text">
                <strong>DBMS Architecture Note:</strong> In a full enterprise environment, these forecasted values 
                (Confidence Scores, Seasonality Index) would be written directly into the <code>Prediction_Model</code> 
                SQL table to trigger automated warehouse restocking alerts via the <code>Inventory_Record</code> table.
            </div>
        </div>
    """, unsafe_allow_html=True)