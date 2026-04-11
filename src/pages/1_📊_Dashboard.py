import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# 2. PREMIUM THEME (matches main.py)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --bg-void: #03040a;
        --surface-1: rgba(255,255,255,0.03);
        --surface-2: rgba(255,255,255,0.06);
        --surface-3: rgba(255,255,255,0.09);
        --border: rgba(255,255,255,0.08);
        --border-bright: rgba(255,255,255,0.14);
        --accent-primary: #7c6dfa;
        --accent-secondary: #38e8c5;
        --accent-warn: #f97316;
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

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: rgba(3,4,10,0.92) !important;
        border-right: 1px solid var(--border-bright) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] * { color: var(--text-secondary) !important; font-family: 'DM Sans', sans-serif !important; }
    [data-testid="stSidebarNav"] a span { color: var(--text-secondary) !important; }
    [data-testid="stSidebarNav"] a:hover span,
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(124,109,250,0.12) !important;
        border-radius: 10px !important;
    }

    /* Hide default chrome */
    footer { display: none !important; }

    /* ── MAIN CONTENT PADDING ── */
    .block-container {
        padding: 4.5rem 2.5rem 2rem 2.5rem !important;
        max-width: 1400px !important;
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
        background: linear-gradient(135deg, var(--accent-primary), #5b4fd4);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 20px var(--glow-purple);
        flex-shrink: 0;
    }
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.8px;
        line-height: 1.1;
        margin: 0;
    }
    .page-subtitle {
        font-size: 13px;
        color: var(--text-secondary);
        margin: 2px 0 0 0;
    }
    .user-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        background: var(--surface-2);
        border: 1px solid var(--border-bright);
        border-radius: 40px;
        padding: 8px 16px;
        font-size: 13px;
        color: var(--text-secondary);
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
    .metric-icon {
        font-size: 22px;
        margin-bottom: 12px;
        display: block;
    }
    .metric-label {
        font-size: 11px;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 30px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -1px;
        line-height: 1;
    }
    .metric-value.accent { color: var(--accent-secondary); }

    /* ── SECTION HEADERS ── */
    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.3px;
        margin-bottom: 4px;
    }
    .section-desc {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 16px;
    }

    /* ── CHART CONTAINER ── */
    .chart-wrap {
        background: var(--surface-1);
        border: 1px solid var(--border-bright);
        border-radius: 20px;
        padding: 20px;
    }

    /* ── DEMO SECTION CARDS ── */
    .demo-label {
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        color: var(--accent-primary);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        background: rgba(124,109,250,0.1);
        border: 1px solid rgba(124,109,250,0.25);
        border-radius: 6px;
        padding: 3px 10px;
        margin-bottom: 6px;
    }
    .demo-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        margin-bottom: 12px;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        height: 42px !important;
        transition: all 0.2s !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #5b4fd4 100%) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 4px 16px var(--glow-purple) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 28px rgba(124,109,250,0.55) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-bright) !important;
        color: var(--text-primary) !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(124,109,250,0.1) !important;
        border-color: rgba(124,109,250,0.4) !important;
        box-shadow: 0 0 16px var(--glow-purple) !important;
    }

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

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
    .stDataFrame { border: 1px solid var(--border-bright) !important; border-radius: 14px !important; }

    /* ── DIVIDER ── */
    hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

    /* General text */
    p, span, label, li { color: var(--text-secondary) !important; font-family: 'DM Sans', sans-serif !important; }
    h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: var(--text-primary) !important; }
    </style>
""", unsafe_allow_html=True)

# 3. SECURITY CHECK
if not st.session_state.get('authenticated'):
    st.warning("🔒 Please log in from the main page to view your dashboard.")
    st.stop()

current_user = st.session_state['user_name']

# 4. PAGE HEADER
st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon">📊</div>
            <div>
                <div class="page-title">Analytics Dashboard</div>
                <div class="page-subtitle">Real-time overview of your retail performance</div>
            </div>
        </div>
        <div class="user-badge">👤 &nbsp;<strong>{current_user}</strong></div>
    </div>
""", unsafe_allow_html=True)

# 5. FETCH DATA FROM THE MYSQL VIEW
@st.cache_data(ttl=60)
def load_dashboard_data(username):
    conn = get_db_connection()
    query = """
        SELECT product_name, category, total_quantity, total_revenue 
        FROM User_Sales_Summary 
        WHERE user_name = %s
    """
    df = pd.read_sql(query, conn, params=(username,))
    conn.close()
    return df

with st.spinner("Fetching your data from the database..."):
    df = load_dashboard_data(current_user)

# 6. HANDLE EMPTY DATA
if df.empty:
    st.info("👋 **No data found.** It looks like you haven't uploaded any sales data yet.")
    st.write("Head over to the **Upload Data** page to ingest your first dataset!")
    st.stop()

# 7. CALCULATE KPIs
total_revenue = df['total_revenue'].sum()
total_items = df['total_quantity'].sum()
top_category = df.groupby('category')['total_revenue'].sum().idxmax()
num_products = df['product_name'].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">💰</span>
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value accent">${total_revenue:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">📦</span>
            <div class="metric-label">Items Sold</div>
            <div class="metric-value">{total_items:,}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🏆</span>
            <div class="metric-label">Top Category</div>
            <div class="metric-value" style="font-size:20px;">{top_category}</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="metric-card">
            <span class="metric-icon">🛍️</span>
            <div class="metric-label">Unique Products</div>
            <div class="metric-value">{num_products}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# 8. INTERACTIVE CHARTS
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="section-label">🏆 Top Products by Revenue</div><div class="section-desc">Your five highest-performing SKUs</div>', unsafe_allow_html=True)
    top_products = df.sort_values(by='total_revenue', ascending=False).head(5)
    fig_bar = px.bar(
        top_products, x='product_name', y='total_revenue',
        color='total_revenue',
        color_continuous_scale=[[0, '#5b4fd4'], [0.5, '#7c6dfa'], [1, '#38e8c5']],
        text_auto='.2s', template='plotly_dark'
    )
    fig_bar.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family='DM Sans', color='#8b8b9e'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickfont=dict(size=11)),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
    )
    fig_bar.update_traces(marker_line_width=0, textfont_size=11)
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.markdown('<div class="section-label">📦 Revenue by Category</div><div class="section-desc">Distribution across all product categories</div>', unsafe_allow_html=True)
    cat_revenue = df.groupby('category')['total_revenue'].sum().reset_index()
    fig_pie = px.pie(
        cat_revenue, names='category', values='total_revenue',
        hole=0.55, template='plotly_dark',
        color_discrete_sequence=['#7c6dfa', '#38e8c5', '#f97316', '#60a5fa', '#a78bfa', '#34d399']
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family='DM Sans', color='#8b8b9e'),
        legend=dict(font=dict(color='#8b8b9e')),
    )
    fig_pie.update_traces(textfont_color='#f0f0f8')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 9. RAW AGGREGATED DATA
st.markdown('<div class="section-label">📄 Aggregated Sales Report</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Powered by the <code>User_Sales_Summary</code> MySQL view — groups and aggregates your raw data in real-time.</div>', unsafe_allow_html=True)
st.dataframe(df, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 10. ADVANCED DATABASE DEMO SECTION
st.markdown("""
    <div class="section-label">⚙️ Advanced Database Operations Demo</div>
    <div class="section-desc">Click these buttons during your Viva to execute the complex SQL requirements live.</div>
""", unsafe_allow_html=True)

st.write("")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.markdown('<div class="demo-label">Criteria 1</div><div class="demo-title">Set Operations / UNION</div>', unsafe_allow_html=True)
    if st.button("🔍 Run Product Extremes", type="primary", use_container_width=True):
        with st.spinner("Executing Stored Procedure..."):
            try:
                conn = get_db_connection()
                df_extremes = pd.read_sql("CALL smart_retail_db.Get_Product_Extremes(%s)", conn, params=(current_user,))
                conn.close()
                st.dataframe(df_extremes, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

with row1_col2:
    st.markdown('<div class="demo-label">Criteria 3</div><div class="demo-title">Cursors — Row-by-row evaluation</div>', unsafe_allow_html=True)
    if st.button("💎 Evaluate High-Value Sales", type="primary", use_container_width=True):
        with st.spinner("Executing Row-by-Row Cursor..."):
            try:
                conn = get_db_connection()
                df_cursor = pd.read_sql("CALL smart_retail_db.Evaluate_High_Value_Sales(%s)", conn, params=(current_user,))
                conn.close()
                st.dataframe(df_cursor, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.write("")
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.markdown('<div class="demo-label">Criteria 1</div><div class="demo-title">Aggregates with HAVING clause</div>', unsafe_allow_html=True)
    if st.button("📊 High Revenue Categories (>$200)", type="primary", use_container_width=True):
        with st.spinner("Filtering Aggregates..."):
            try:
                conn = get_db_connection()
                df_having = pd.read_sql("CALL smart_retail_db.Get_High_Revenue_Categories(%s)", conn, params=(current_user,))
                conn.close()
                st.dataframe(df_having, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

with row2_col2:
    st.markdown('<div class="demo-label">Criteria 2</div><div class="demo-title">Nested / Correlated Subqueries</div>', unsafe_allow_html=True)
    if st.button("📈 Above Average Transactions", type="primary", use_container_width=True):
        with st.spinner("Running Correlated Subquery..."):
            try:
                conn = get_db_connection()
                df_sub = pd.read_sql("CALL smart_retail_db.Get_Above_Average_Sales(%s)", conn, params=(current_user,))
                conn.close()
                st.dataframe(df_sub, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.write("")
row3_col1, row3_col2 = st.columns(2)
with row3_col1:
    st.markdown('<div class="demo-label">Criteria 2</div><div class="demo-title">Multiple Joins / LEFT JOIN</div>', unsafe_allow_html=True)
    if st.button("👥 All Users Platform Status", type="primary", use_container_width=True):
        with st.spinner("Joining Tables..."):
            try:
                conn = get_db_connection()
                df_join = pd.read_sql("CALL smart_retail_db.Get_All_Users_Sales_Status()", conn)
                conn.close()
                st.dataframe(df_join, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

with row3_col2:
    st.markdown('<div class="demo-label">Criteria 3</div><div class="demo-title">Functions & Exception Handling</div>', unsafe_allow_html=True)
    if st.button("🛡️ Test Secure Insert & User Function", type="primary", use_container_width=True):
        with st.spinner("Testing Logic..."):
            try:
                conn1 = get_db_connection()
                df_ex = pd.read_sql("CALL smart_retail_db.Safe_Insert_Product('Demo Item', 'Misc', 10.00, 20.00)", conn1)
                conn1.close()

                conn2 = get_db_connection()
                query = """
                    SELECT %s AS Customer, 
                    IFNULL(SUM(total_revenue), 0) AS 'Total Revenue', 
                    smart_retail_db.Get_Loyalty_Tier(IFNULL(SUM(total_revenue), 0)) AS 'Loyalty Tier' 
                    FROM Sales_Data s 
                    INNER JOIN Customer c ON s.user_id = c.id 
                    WHERE c.Name = %s
                """
                df_func = pd.read_sql(query, conn2, params=(current_user, current_user))
                conn2.close()

                st.success(f"Transaction Status: {df_ex.iloc[0]['Status']}")
                st.dataframe(df_func, use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")