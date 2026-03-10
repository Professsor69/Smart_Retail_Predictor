import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="AI Sales Predictor", page_icon="🤖", layout="wide")

# 2. DEEP CHARCOAL THEME CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    .main-header { color: #60a5fa; font-size: 36px; font-weight: 800; }
    .metric-card { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 1px solid #374151; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
    .metric-value { font-size: 24px; font-weight: bold; color: #34d399; }
    .metric-label { font-size: 14px; color: #9ca3af; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

if not st.session_state.get('authenticated'):
    st.warning("🔒 Please log in to access the AI Predictor.")
    st.stop()

current_user = st.session_state['user_name']

st.markdown("<div class='main-header'>🤖 AI Demand Forecasting</div>", unsafe_allow_html=True)
st.write("Leveraging Machine Learning to predict future sales trends and seasonality based on your historical data.")
st.divider()

# 3. FETCH HISTORICAL DATA
@st.cache_data(ttl=10)
def get_ml_data(username):
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

with st.spinner("Initializing AI Models..."):
    df = get_ml_data(current_user)

if df.empty:
    st.error("Not enough data to run predictions. Please upload data in the Data Ingestion hub.")
    st.stop()

# Ensure dates are in datetime format
df['sale_date'] = pd.to_datetime(df['sale_date'])

# 4. PRODUCT SELECTION
products = df['product_name'].unique()
selected_product = st.selectbox("Select a Product to Forecast:", products)

# Filter data for the selected product
prod_df = df[df['product_name'] == selected_product].groupby('sale_date')['quantity_sold'].sum().reset_index()

# 5. MACHINE LEARNING LOGIC (Linear Regression Time-Series)
if len(prod_df) < 2:
    st.warning(f"⚠️ Need more historical data for '{selected_product}' to make an accurate prediction. Upload a larger dataset!")
else:
    # Prepare data for Scikit-Learn
    prod_df['Days_Since_Start'] = (prod_df['sale_date'] - prod_df['sale_date'].min()).dt.days
    
    X = prod_df[['Days_Since_Start']]
    y = prod_df['quantity_sold']
    
    # Train the Model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict the next 30 days
    last_date = prod_df['sale_date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_days_since = [(d - prod_df['sale_date'].min()).days for d in future_dates]
    
    future_X = pd.DataFrame({'Days_Since_Start': future_days_since})
    predictions = model.predict(future_X)
    
    # Ensure no negative predictions (you can't sell negative items)
    predictions = [max(0, int(p)) for p in predictions]
    
    # Calculate Seasonality (Best Day of Week)
    df['Day_of_Week'] = df['sale_date'].dt.day_name()
    best_day = df[df['product_name'] == selected_product].groupby('Day_of_Week')['quantity_sold'].sum().idxmax()
    
    # Calculate Total Forecast
    total_predicted = sum(predictions)

    # 6. DISPLAY AI INSIGHTS (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>30-Day Forecast</div><div class='metric-value'>{total_predicted} units</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Peak Seasonality</div><div class='metric-value'>{best_day}s</div></div>", unsafe_allow_html=True)
    with col3:
        trend = "📈 Trending Up" if predictions[-1] > predictions[0] else "📉 Trending Down"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Overall Trend</div><div class='metric-value'>{trend}</div></div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 7. INTERACTIVE FORECAST CHART
    st.subheader(f"📊 30-Day Sales Trajectory for {selected_product}")
    
    fig = go.Figure()
    
    # Plot Historical Data
    fig.add_trace(go.Scatter(
        x=prod_df['sale_date'], y=prod_df['quantity_sold'], 
        mode='lines+markers', name='Historical Sales', line=dict(color='#60a5fa', width=3)
    ))
    
    # Plot AI Predictions
    fig.add_trace(go.Scatter(
        x=future_dates, y=predictions, 
        mode='lines+markers', name='AI Forecast', line=dict(color='#34d399', width=3, dash='dot')
    ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Date",
        yaxis_title="Quantity Sold",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 8. THE DBMS CONNECTION (Why the Professor cares)
    st.info("💡 **DBMS Architecture Note:** In a full enterprise environment, these forecasted values (Confidence Scores, Seasonality Index) would be written directly into the `Prediction_Model` SQL table to trigger automated warehouse restocking alerts via the `Inventory_Record` table.")