import streamlit as st
import pandas as pd
import time
from datetime import datetime
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Data Ingestion", page_icon="📥", layout="wide")

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
    .sub-text { color: #94a3b8; font-size: 16px; }
    
    /* Make standard text readable on dark background */
    [data-testid="stMarkdownContainer"] p { color: #e2e8f0; }
    div[data-testid="stInfo"] { background-color: #1e293b; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# 3. SECURITY CHECK
if not st.session_state.get('authenticated'):
    st.warning("🔒 Please log in from the main page to upload data.")
    st.stop()

st.markdown("<div class='main-header'>📥 Data Ingestion Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Upload your comprehensive retail dataset. Our system validates, cleans, and securely stores it in your isolated database environment.</div><br>", unsafe_allow_html=True)

# 4. EXPANDED TEMPLATE DOWNLOAD
# 4. EXPANDED TEMPLATE DOWNLOAD
st.info("💡 **Format Requirement:** Your file must exactly match these column names: `Date`, `Order_ID`, `Product_Name`, `Category`, `Quantity`, `Unit_Price`, `Discount`, `Region`")

# --- ADVANCED DEMO DATA GENERATOR ---
# Generates 30 days of realistic sales data for 3 products so the AI can train!
import random
from datetime import datetime, timedelta

demo_data = []
start_date = datetime(2026, 1, 1)

for i in range(30):
    current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
    # Product 1: Consistent fast-seller
    demo_data.append([current_date, f'ORD-10{i}', 'Wireless Mouse', 'Electronics', random.randint(15, 35), 25.99, 0.0, 'North'])
    # Product 2: Highly variable seller
    demo_data.append([current_date, f'ORD-20{i}', 'Mechanical Keyboard', 'Electronics', random.randint(2, 12), 89.50, 5.0, 'West'])
    # Product 3: Premium, low volume
    demo_data.append([current_date, f'ORD-30{i}', 'Gaming Monitor', 'Electronics', random.randint(0, 5), 299.99, 15.0, 'South'])

template_df = pd.DataFrame(demo_data, columns=['Date', 'Order_ID', 'Product_Name', 'Category', 'Quantity', 'Unit_Price', 'Discount', 'Region'])

st.download_button(
    label="📄 Download 30-Day Demo Dataset",
    data=template_df.to_csv(index=False).encode('utf-8'),
    file_name='Smart_Retail_AI_Demo_Data.csv',
    mime='text/csv',
    type="primary"
)
# 5. THE FILE UPLOADER
uploaded_file = st.file_uploader("Drag and drop your dataset here", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        df.columns = df.columns.str.strip()
        
        required_columns = ['Date', 'Order_ID', 'Product_Name', 'Category', 'Quantity', 'Unit_Price', 'Discount', 'Region']
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Invalid format! Missing required columns. Please use the template.")
            st.stop()

        st.write("🔍 **Data Preview:**")
        st.dataframe(df.head(10), width='stretch')

        # 6. DATABASE INJECTION
        if st.button("🚀 INJECT TO DATABASE", type="primary", use_container_width=True):
            with st.spinner("Processing and securing your data..."):
                conn = get_db_connection()
                cursor = conn.cursor()
                
                current_user = st.session_state['user_name']
                cursor.execute("SELECT id FROM Customer WHERE Name = %s", (current_user,))
                user_record = cursor.fetchone()
                
                if not user_record:
                    st.error("Authentication Error. Please log in again.")
                    st.stop()
                    
                user_id = user_record[0]
                batch_id = f"BATCH_{int(time.time())}"
                
                data_to_insert = []
                for index, row in df.iterrows():
                    try:
                        sql_date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                        data_to_insert.append((
                            user_id, str(row['Order_ID']), str(row['Product_Name']), 
                            str(row['Category']), int(row['Quantity']), float(row['Unit_Price']), 
                            float(row['Discount']), str(row['Region']), sql_date, batch_id
                        ))
                    except Exception as e:
                        continue
                
                sql = """INSERT INTO Sales_Data 
                         (user_id, order_id, product_name, category, quantity_sold, unit_price, discount, region, sale_date, upload_batch) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                cursor.executemany(sql, data_to_insert)
                conn.commit()
                conn.close()
                
                st.success(f"✅ Success! {len(data_to_insert)} records have been securely injected into your database.")
                st.balloons()

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")