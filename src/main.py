import streamlit as st
import time
from db_connection import get_db_connection
from streamlit_google_auth import Authenticate

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Smart Retail Predictor", page_icon="🛒", layout="wide")

# 2. INITIALIZE GOOGLE AUTH
try:
    authenticator = Authenticate(
        secret_credentials_path='google_credentials.json',
        cookie_name='smart_retail_auth',
        cookie_key='this_is_a_super_secret_key',
        redirect_uri='http://localhost:8501/',
    )
    
    # Catch the user if they successfully logged in via Google
    authenticator.check_authentification()
    if st.session_state.get('connected'):
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = st.session_state.get('user_info', {}).get('name', 'Google User')
        st.switch_page("pages/1_Dashboard.py")
except Exception as e:
    st.error(f"Google Auth Setup Error. Check if google_credentials.json is in the correct folder! Error: {e}")

# 3. COMPACT CSS
st.markdown("""
    <style>
    #MainMenu, footer, header, [data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none !important;}
    
    .stApp {
        background: linear-gradient(135deg, #a8cbf3 0%, #ffffff 50%, #a8cbf3 100%);
        overflow: hidden; 
    }
    
    .block-container {
        padding-top: 3vh !important; 
        padding-bottom: 0vh !important;
        max-width: 950px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #d3d3d3 !important; 
        border-radius: 15px !important;
        box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.08) !important; 
        padding: 20px !important; 
    }
    
    .main-title { text-align: center; font-size: 34px; font-weight: 800; margin-bottom: 10px; color: #1e1e1e;}
    
    .center-text { 
        text-align: center !important; 
        color: #1A365D !important; 
        font-size: 32px !important; 
        margin-top: 0 !important; 
        margin-bottom: 5px !important;
        display: block !important;
    }
    
    .sub-text { text-align: center; color: #4b8bbe; font-size: 16px; margin-bottom: 15px; }
    .or-text { text-align: center; color: #a0a0a0; font-size: 12px; margin: 15px 0px 10px 0px; }
    
    .stTextInput > label > div > p { color: #333333 !important; font-size: 14px !important;}
    [data-baseweb="input"] > div { background-color: #f9f9f9 !important; border: 1px solid #eee !important; min-height: 40px !important;}
    [data-baseweb="input"] input { color: #000000 !important; padding: 8px !important;}
    </style>
    """, unsafe_allow_html=True)

# 4. SESSION STATE
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login'

def switch_mode(mode):
    st.session_state['auth_mode'] = mode

# --- THE TITLE ---
st.markdown("<div class='main-title'>🛒 Smart Retail Predictor</div>", unsafe_allow_html=True)

# 5. THE COMPACT FLOATING CARD
with st.container(border=True):
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.image("https://img.freepik.com/free-vector/mobile-login-concept-illustration_114360-83.jpg", use_container_width=True)

    with right_col:
        st.markdown("<h1 class='center-text'>Welcome!</h1>", unsafe_allow_html=True)
        
        # ------------------- LOGIN MODE -------------------
        if st.session_state['auth_mode'] == 'login':
            st.markdown("<div class='sub-text'>Sign in to your Account</div>", unsafe_allow_html=True)
            
            user_input = st.text_input("Username", placeholder="e.g. Kush")
            pass_input = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<div style='text-align: right; font-size: 12px; color: #4b8bbe; margin-bottom: 10px; cursor: pointer;'>Forgot Password?</div>", unsafe_allow_html=True)
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("SIGN IN", type="primary", use_container_width=True):
                    with st.spinner("Authenticating..."):
                        time.sleep(0.5)
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM Customer WHERE Name = %s AND Contact_Info = %s", (user_input, pass_input))
                            result = cursor.fetchone()
                            conn.close()

                            if result:
                                st.session_state['authenticated'] = True
                                st.session_state['user_name'] = user_input 
                                st.switch_page("pages/1_Dashboard.py")
                            else:
                                st.error("❌ Invalid Credentials.")
                        except Exception as e:
                            st.error(f"Database Error: {e}")
            with btn_col2:
                st.button("SIGN UP", on_click=switch_mode, args=('signup',), use_container_width=True)

        # ------------------- SIGN UP MODE -------------------
        else:
            st.markdown("<div class='sub-text'>Create your Account</div>", unsafe_allow_html=True)
            
            new_user = st.text_input("Choose Username", placeholder="e.g. Kush")
            new_pass = st.text_input("Choose Password", type="password", placeholder="••••••••")
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.button("BACK TO LOGIN", on_click=switch_mode, args=('login',), use_container_width=True)
            with btn_col2:
                if st.button("CREATE ACCOUNT", type="primary", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO Customer (Name, Contact_Info) VALUES (%s, %s)", (new_user, new_pass))
                            conn.commit()
                            conn.close()
                            st.success("✅ Account created!")
                            time.sleep(1)
                            st.session_state['auth_mode'] = 'login'
                            st.rerun()
                        except Exception:
                            st.error("❌ Username may exist.")
                    else:
                        st.warning("Fill all fields.")
# --- UPDATED GOOGLE-ONLY SECTION ---
        st.markdown("<div class='or-text'>OR CONTINUE WITH</div>", unsafe_allow_html=True)
        
        # Widen the center column massively so the button has room to stretch horizontally
        pad_left, google_col, pad_right = st.columns([0.2, 3, 0.2])
        
        with google_col:
            try:
                authenticator.login()
            except Exception:
                st.error("Setup incomplete")