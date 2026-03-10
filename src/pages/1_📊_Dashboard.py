import streamlit as st
import pandas as pd
import plotly.express as px
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# 2. MIDNIGHT SLATE THEME CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }
    .main-header { color: #f8fafc; font-size: 36px; font-weight: 800; }
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #38bdf8; }
    .metric-label { font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stMarkdownContainer"] p { color: #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURITY CHECK
if not st.session_state.get('authenticated'):
    st.warning("🔒 Please log in from the main page to view your dashboard.")
    st.stop()

current_user = st.session_state['user_name']

st.markdown(f"<div class='main-header'>📊 Welcome, {current_user}!</div>", unsafe_allow_html=True)
st.markdown("Here is the predictive analytics overview based on your uploaded sales data.")
st.divider()

# 4. FETCH DATA FROM THE MYSQL VIEW
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

# 5. HANDLE EMPTY DATA
if df.empty:
    st.info("👋 **No data found.** It looks like you haven't uploaded any sales data yet.")
    st.write("Head over to the **Upload Data** page to ingest your first Excel dataset!")
    st.stop() 

# 6. CALCULATE KPIs
total_revenue = df['total_revenue'].sum()
total_items = df['total_quantity'].sum()
top_category = df.groupby('category')['total_revenue'].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Revenue</div><div class='metric-value'>${total_revenue:,.2f}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Items Sold</div><div class='metric-value'>{total_items:,}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Top Category</div><div class='metric-value'>{top_category}</div></div>", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# 7. INTERACTIVE CHARTS (Forced into Dark Mode)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🏆 Top Products by Revenue")
    top_products = df.sort_values(by='total_revenue', ascending=False).head(5)
    fig_bar = px.bar(top_products, x='product_name', y='total_revenue', color='product_name', text_auto='.2s', template='plotly_dark')
    fig_bar.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.subheader("📦 Revenue Distribution by Category")
    cat_revenue = df.groupby('category')['total_revenue'].sum().reset_index()
    fig_pie = px.pie(cat_revenue, names='category', values='total_revenue', hole=0.4, template='plotly_dark')
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# 8. RAW AGGREGATED DATA
st.subheader("📄 Aggregated Sales Report")
st.write("This table is powered by your `User_Sales_Summary` MySQL View, grouping your raw data efficiently.")
st.dataframe(df, use_container_width=True)  
# --- ADD THIS TO THE VERY BOTTOM OF YOUR 1_📊_Dashboard.py FILE ---

st.divider()

# 9. ADVANCED DATABASE DEMO SECTION (For your Professor)
st.subheader("⚙️ Advanced Database Operations (Demo)")
st.write("These tools demonstrate advanced SQL Stored Procedures executing live against your dataset.")

# Create two columns for our Demo buttons
demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    st.markdown("**(Review Req: Sets / UNION)**")
    if st.button("🔍 Run Product Extremes", type="primary", use_container_width=True):
        with st.spinner("Executing Stored Procedure..."):
            try:
                conn = get_db_connection()
                # FIXED: Explicitly calling from smart_retail_db
                df_extremes = pd.read_sql("CALL smart_retail_db.Get_Product_Extremes(%s)", conn, params=(current_user,))
                conn.close()
                st.success("Successfully executed Set Operator (UNION) in MySQL!")
                st.dataframe(df_extremes, use_container_width=True)
            except Exception as e:
                st.error(f"Error running procedure: {e}")

with demo_col2:
    st.markdown("**(Review Req: Cursors)**")
    if st.button("💎 Evaluate High-Value Sales (>$100)", type="primary", use_container_width=True):
        with st.spinner("Executing Row-by-Row Cursor..."):
            try:
                conn = get_db_connection()
                # FIXED: Explicitly calling from smart_retail_db
                df_cursor = pd.read_sql("CALL smart_retail_db.Evaluate_High_Value_Sales(%s)", conn, params=(current_user,))
                conn.close()
                st.success("Successfully executed Cursor row-by-row logic in MySQL!")
                st.dataframe(df_cursor, use_container_width=True)
            except Exception as e:
                st.error(f"Error running procedure: {e}")