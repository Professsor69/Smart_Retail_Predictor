import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from db_connection import get_db_connection

# --- PAGE CONFIG ---
st.set_page_config(page_title="Performance Monitor", page_icon="📈", layout="wide")

# --- THE GATEKEEPER ---
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    st.warning("Please login on the Home page first.")
    st.stop() 

# --- HEADER ---
st.title("Retail Trends & Performance Monitor")
st.markdown(f"**Logged in as:** `{st.session_state.get('user_name', 'Admin')}`")

# --- DATA FETCHING (Real + Mock Data for UI flex) ---
try:
    # 1. Fetch REAL data for the metrics
    conn = get_db_connection()
    df_real = pd.read_sql("SELECT Name, Category, Selling_Price FROM Product", conn)
    conn.close()
    real_product_count = len(df_real)
except Exception:
    df_real = pd.DataFrame()
    real_product_count = 0

# 2. Generate 8,500 rows of FAKE data so the charts look exactly like your screenshot
np.random.seed(42)
n_records = 8523
df_sim = pd.DataFrame({
    'Item_Weight': np.random.uniform(5, 20, n_records),
    'Item_Visibility': np.random.uniform(0.01, 0.3, n_records),
    'Item_MRP': np.random.normal(140, 40, n_records),
    'Outlet_Size': np.random.choice(['Small', 'Medium', 'High'], n_records),
    'Outlet_Type': np.random.choice(['Supermarket Type1', 'Supermarket Type2', 'Grocery Store', 'Supermarket Type3'], n_records),
    'Item_Outlet_Sales': np.random.normal(2181, 1000, n_records)
})
df_sim['Item_Outlet_Sales'] = df_sim['Item_Outlet_Sales'].abs() # No negative sales

# --- TABS LAYOUT (Just like the screenshot) ---
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Advanced Insights", "Sales Prediction Tool", "Export Report"])

with tab1:
    # --- METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Sales", f"${df_sim['Item_Outlet_Sales'].mean():,.2f}")
    col2.metric("Products (Real DB)", real_product_count)
    col3.metric("Outlets", "10")
    col4.metric("Total Records", f"{n_records}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Real Database Preview Toggle
    if st.checkbox("Show Real Dataset Preview"):
        st.dataframe(df_real, use_container_width=True, hide_index=True)

    # --- ROW 1: HISTOGRAM & BOX PLOT ---
    st.subheader("Basic Sales Insights")
    c1, c2 = st.columns(2)
    
    with c1:
        # Density / Histogram Plot
        fig_hist = px.histogram(df_sim, x="Item_MRP", marginal="box", title="Distribution of Item MRP", color_discrete_sequence=['#3498db'])
        fig_hist.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c2:
        # Box Plot
        fig_box = px.box(df_sim, x="Outlet_Size", y="Item_Outlet_Sales", color="Outlet_Size", title="Sales Distribution by Outlet Size")
        fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_box, use_container_width=True)

    # --- ROW 2: VIOLIN PLOT & HEATMAP ---
    c3, c4 = st.columns(2)
    
    with c3:
        # Violin Plot
        fig_violin = px.violin(df_sim, x="Outlet_Type", y="Item_Outlet_Sales", color="Outlet_Type", box=True, title="Sales Distribution by Outlet Type")
        fig_violin.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_violin, use_container_width=True)
        
    with c4:
        # Correlation Heatmap
        corr = df_sim[['Item_Weight', 'Item_Visibility', 'Item_MRP', 'Item_Outlet_Sales']].corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', title="Correlation Matrix of Numerical Features")
        fig_corr.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_corr, use_container_width=True)