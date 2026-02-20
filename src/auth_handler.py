import streamlit as st
from streamlit_google_auth import Authenticate

def setup_google_auth():
    # This initializes the Google Authenticator cleanly using the JSON file
    authenticator = Authenticate(
        secret_credentials_path='google_credentials.json',
        cookie_name='smart_retail_auth',
        cookie_key='this_is_a_super_secret_key',
        redirect_uri='http://localhost:8501/',
    )
    return authenticator

def check_login_status(authenticator):
    # This catches the user when they return from the Google popup
    authenticator.check_authentification()
    
    if st.session_state.get('connected'):
        st.session_state['authenticated'] = True
        # Extracts their real name from Google
        st.session_state['user_name'] = st.session_state.get('user_info', {}).get('name', 'Google User')
        st.switch_page("pages/1_Dashboard.py")