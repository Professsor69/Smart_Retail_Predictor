import streamlit as st
import pandas as pd
import numpy as np

# Page config
st.set_page_config(page_title="Smart Retail Predictor", layout="wide")

# Header
st.title("🛒 Smart Retail Predictor")
st.markdown("---")

# Layout: 3 Columns for quick stats
col1, col2, col3 = st.columns(3)
col1.metric("Current Stock", "1,200 units", "-5%")
col2.metric("Predicted Sales (24h)", "450 units", "+12%")
col3.metric("AI Confidence", "92%", "High")

# Main Dashboard area
st.subheader("📈 Demand Forecast")
# Create some fake data for the graph
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Actual Sales', 'Predicted Demand', 'Inventory Level']
)
st.line_chart(chart_data)

st.success("🤖 AI Insight: Weekend sales are expected to spike. Suggesting a 5% increase in Beverage stock.")
