import streamlit as st
import time
from db_connection import get_db_connection

# 1. PAGE CONFIGURATION 
st.set_page_config(page_title="Retail OS | Login", page_icon="🛒", layout="wide")

# 2. CUSTOM CSS (This hides the sidebar, headers, and footers entirely on this page)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Hides the sidebar */
    [data-testid="stSidebar"] {display: none;}
    /* Hides the little arrow button that opens the sidebar */
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# 3. SPLIT SCREEN LAYOUT
col1, col2, col3 = st.columns([1.2, 0.1, 1]) 

with col1:
    # FIXED: Changed use_column_width to use_container_width to remove the yellow warning
    st.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=800&q=80", use_container_width=True)

with col3:
    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.title("🛒 Smart Retail OS")
    st.markdown("### Secure Administrator Access")
    st.caption("Powered by Advanced Demand Forecasting Models")
    
    with st.form("login_gate", border=True):
        user_input = st.text_input("Username", placeholder="e.g., Kush")
        pass_input = st.text_input("Password", type="password", placeholder="••••••••")
        
        submit_button = st.form_submit_button("Secure Login 🔒", use_container_width=True)

        if submit_button:
            with st.spinner("Authenticating with secure database..."):
                time.sleep(1) 
                
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    query = "SELECT * FROM Customer WHERE Name = %s AND Contact_Info = %s"
                    cursor.execute(query, (user_input, pass_input))
                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        st.session_state['authenticated'] = True
                        st.session_state['user_name'] = user_input 
                        st.success(f"Access Granted! Redirecting {user_input}...")
                        time.sleep(0.5) 
                        
                        st.switch_page("pages/1_Dashboard.py")
                    else:
                        st.error("❌ Invalid Credentials. Security breach logged.")
                except Exception as e:
                    st.error(f"System Offline: {e}")