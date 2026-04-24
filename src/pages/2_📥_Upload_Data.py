import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Data Ingestion", page_icon="📥", layout="wide")

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
        --text-primary: #f0f0f8;
        --text-secondary: #8b8b9e;
        --glow-purple: rgba(124,109,250,0.35);
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
        background: linear-gradient(135deg, #38e8c5, #059669);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 20px rgba(56,232,197,0.3);
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
    .page-subtitle { font-size: 13px; color: var(--text-secondary); margin: 2px 0 0 0; }
    .user-badge {
        display: flex; align-items: center; gap: 10px;
        background: var(--surface-2); border: 1px solid var(--border-bright);
        border-radius: 40px; padding: 8px 16px; font-size: 13px; color: var(--text-secondary);
    }
    .user-badge strong { color: var(--text-primary); }

    /* ── INFO CARD ── */
    .info-card {
        background: rgba(124,109,250,0.06);
        border: 1px solid rgba(124,109,250,0.2);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 14px;
    }
    .info-card-icon { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
    .info-card-text { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
    .info-card-text strong { color: var(--text-primary); }
    .info-card-text code {
        background: rgba(124,109,250,0.15);
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 12px;
        color: var(--accent-primary) !important;
        font-family: monospace !important;
    }

    /* ── UPLOAD ZONE ── */
    [data-testid="stFileUploader"] {
        background: var(--surface-1) !important;
        border: 1.5px dashed var(--border-bright) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--accent-primary) !important; }
    [data-testid="stFileUploaderDropzoneInstructions"] { color: var(--text-secondary) !important; }

    /* ── SECTION ── */
    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.3px;
        margin-bottom: 4px;
    }
    .section-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; }

    /* ── BUTTONS ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        height: 42px !important;
        transition: all 0.2s !important;
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
    .stDownloadButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        height: 42px !important;
        background: rgba(56,232,197,0.1) !important;
        border: 1px solid rgba(56,232,197,0.3) !important;
        color: var(--accent-secondary) !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(56,232,197,0.18) !important;
        box-shadow: 0 0 20px rgba(56,232,197,0.2) !important;
        transform: translateY(-2px) !important;
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
    st.warning("🔒 Please log in from the main page to upload data.")
    st.stop()

current_user = st.session_state['user_name']

# 4. PAGE HEADER
st.markdown(f"""
    <div class="page-header">
        <div class="page-header-left">
            <div class="page-icon">📥</div>
            <div>
                <div class="page-title">Data Ingestion Hub</div>
                <div class="page-subtitle">Upload, validate, and inject your retail datasets</div>
            </div>
        </div>
        <div class="user-badge">👤 &nbsp;<strong>{current_user}</strong></div>
    </div>
""", unsafe_allow_html=True)

# 5. FORMAT REQUIREMENT CARD
st.markdown("""
    <div class="info-card">
        <div class="info-card-icon">💡</div>
        <div class="info-card-text">
            <strong>Format Requirement:</strong> Your file must contain exactly these column headers:<br>
            <code>Date</code> &nbsp; <code>Order_ID</code> &nbsp; <code>Product_Name</code> &nbsp; <code>Category</code> &nbsp; <code>Quantity</code> &nbsp; <code>Unit_Price</code> &nbsp; <code>Discount</code> &nbsp; <code>Region</code>
        </div>
    </div>
""", unsafe_allow_html=True)

# 6. DEMO DATASET GENERATOR
demo_data = []
start_date = datetime(2026, 1, 1)
for i in range(30):
    current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
    demo_data.append([current_date, f'ORD-10{i}', 'Wireless Mouse', 'Electronics', random.randint(15, 35), 25.99, 0.0, 'North'])
    demo_data.append([current_date, f'ORD-20{i}', 'Mechanical Keyboard', 'Electronics', random.randint(2, 12), 89.50, 5.0, 'West'])
    demo_data.append([current_date, f'ORD-30{i}', 'Gaming Monitor', 'Electronics', random.randint(0, 5), 299.99, 15.0, 'South'])

template_df = pd.DataFrame(demo_data, columns=['Date', 'Order_ID', 'Product_Name', 'Category', 'Quantity', 'Unit_Price', 'Discount', 'Region'])

dl_col, _ = st.columns([1, 2])
with dl_col:
    st.download_button(
        label="📄 Download 30-Day Demo Dataset",
        data=template_df.to_csv(index=False).encode('utf-8'),
        file_name='Smart_Retail_AI_Demo_Data.csv',
        mime='text/csv',
    )

st.markdown("<hr>", unsafe_allow_html=True)

# 7. FILE UPLOADER
st.markdown('<div class="section-label">📂 Upload Your Dataset</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Drag and drop your CSV or Excel file below. The system will validate, clean, and inject it into your isolated database environment.</div>', unsafe_allow_html=True)

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
            st.error("❌ Invalid format! Missing required columns. Please use the demo template above.")
            st.stop()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">🔍 Data Preview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-desc">Showing the first 10 rows of your uploaded file ({len(df)} total rows detected).</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

        st.write("")

        # 8. DATABASE INJECTION
        if st.button("🚀 Inject to Database", type="primary", use_container_width=True):
            with st.spinner("Processing and securing your data..."):
                conn = get_db_connection()
                cursor = conn.cursor()

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
                    except Exception:
                        continue

                sql = """INSERT INTO Sales_Data 
                         (user_id, order_id, product_name, category, quantity_sold, unit_price, discount, region, sale_date, upload_batch) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                cursor.executemany(sql, data_to_insert)
                conn.commit()
                conn.close()

                st.success(f"✅ Success! **{len(data_to_insert)} records** have been securely injected into your database.")
                st.balloons()

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")