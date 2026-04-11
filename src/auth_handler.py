"""
auth_handler.py
---------------
Authentication backend for Smart Retail Predictor.

Handles:
  - Username / password login  (against the Customer table)
  - New account registration
  - Google OAuth via streamlit-google-auth
  - Session state management
  - Logout

All DB operations go through db_connection so there is ONE
place to change credentials or retry logic.
"""

import time
import os
import streamlit as st
from db_connection import get_db_connection, get_cursor

# Allow HTTP for local testing with Google Auth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

import json
import urllib.parse
import requests

# ── Constants ─────────────────────────────────────────────────────────────────
COOKIE_NAME = "smart_retail_auth"
COOKIE_KEY  = "this_is_a_super_secret_key_change_me_in_prod"
REDIRECT_URI = "http://localhost:8501/"
CREDENTIALS_PATH = "google_credentials.json"

# Session-state keys used throughout the app
SESSION_AUTHENTICATED = "authenticated"
SESSION_USERNAME      = "user_name"
SESSION_USER_ID       = "user_id"


# ── Internal helpers ──────────────────────────────────────────────────────────
def _set_session(user_id: int, username: str):
    """Mark the session as authenticated and store user identity."""
    st.session_state[SESSION_AUTHENTICATED] = True
    st.session_state[SESSION_USERNAME]      = username
    st.session_state[SESSION_USER_ID]       = user_id


def _clear_session():
    """Wipe all authentication keys from session state."""
    for key in (SESSION_AUTHENTICATED, SESSION_USERNAME, SESSION_USER_ID, "connected", "user_info"):
        st.session_state.pop(key, None)


# ── Core auth functions ───────────────────────────────────────────────────────
def is_authenticated() -> bool:
    """True if the current session has a valid login."""
    return bool(st.session_state.get(SESSION_AUTHENTICATED))


def get_current_user() -> str:
    """Return the logged-in username, or empty string."""
    return st.session_state.get(SESSION_USERNAME, "")


def get_current_user_id() -> int | None:
    """Return the logged-in user's DB id, or None."""
    return st.session_state.get(SESSION_USER_ID)


def login(username: str, password: str) -> tuple[bool, str]:
    """
    Validate credentials against the Customer table.

    Returns:
        (True,  "")            on success  — also sets session state
        (False, error_message) on failure
    """
    if not username or not password:
        return False, "Please enter both username and password."

    try:
        conn   = get_db_connection()
        cursor = get_cursor(conn)
        cursor.execute(
            "SELECT id, Name FROM Customer WHERE Name = %s AND Contact_Info = %s",
            (username.strip(), password),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            _set_session(user_id=row["id"], username=row["Name"])
            return True, ""
        return False, "Invalid username or password."

    except Exception as e:
        return False, f"Database error: {e}"


def register(username: str, password: str) -> tuple[bool, str]:
    """
    Create a new Customer record.

    Returns:
        (True,  "")            on success
        (False, error_message) on failure (e.g. duplicate username)
    """
    if not username or not password:
        return False, "Please fill in all fields."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    try:
        conn   = get_db_connection()
        cursor = get_cursor(conn)

        # Check for existing username first for a friendlier error
        cursor.execute("SELECT id FROM Customer WHERE Name = %s", (username.strip(),))
        if cursor.fetchone():
            conn.close()
            return False, "That username is already taken. Please choose another."

        cursor.execute(
            "INSERT INTO Customer (Name, Contact_Info) VALUES (%s, %s)",
            (username.strip(), password),
        )
        new_id = cursor.lastrowid
        conn.close()

        # Auto-login after registration
        _set_session(user_id=new_id, username=username.strip())
        return True, ""

    except Exception as e:
        return False, f"Registration failed: {e}"


def logout():
    """Clear session and rerun so the app returns to the login page."""
    _clear_session()
    st.rerun()


# ── Custom Google OAuth ───────────────────────────────────────────────────────
def get_google_config():
    try:
        with open(CREDENTIALS_PATH, "r") as f:
            return json.load(f).get("web", {})
    except Exception:
        return None

def setup_google_auth():
    return get_google_config()


def check_google_login(config, redirect_page: str = "pages/1_📊_Dashboard.py"):
    """
    Called on every page load.
    If 'code' is in url, exchange it and login.
    """
    if not config: return
    
    code = st.query_params.get("code")
    if not code: return

    # If already logged in, just clear the stale code param
    if is_authenticated():
        st.query_params.clear()
        return

    try:
        # 1. Exchange code for token
        res = requests.post(
            config.get("token_uri", "https://oauth2.googleapis.com/token"),
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
            }
        )
        res.raise_for_status()
        
        # 2. Fetch User Profile
        user_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {res.json()['access_token']}"}
        )
        user_res.raise_for_status()
        user_info = user_res.json()
        
        g_name   = user_info.get("name", "Google User").strip()
        g_email  = user_info.get("email", "")

        # 3. Upsert User in DB
        conn   = get_db_connection()
        cursor = get_cursor(conn)
        # The Customer table does not have an Email column, so check by Name or Contact_Info
        cursor.execute("SELECT id, Name FROM Customer WHERE Name = %s OR Contact_Info = %s", (g_name, g_email))
        row = cursor.fetchone()

        if row:
            user_id, username = row["id"], row["Name"]
        else:
            cursor.execute(
                "INSERT INTO Customer (Name, Contact_Info) VALUES (%s, %s)",
                (g_name, g_email),
            )
            user_id, username = cursor.lastrowid, g_name

        conn.close()
        _set_session(user_id=user_id, username=username)
        
        st.query_params.clear()
        st.switch_page(redirect_page)

    except Exception as e:
        if "400 Client Error" in str(e):
            st.query_params.clear() # Code was already consumed
        else:
            st.error(f"Google login error: {e}")


def render_google_button(config):
    """Render a custom HTML Google Login button"""
    if not config:
        st.caption("Google sign-in unavailable — `google_credentials.json` not found.")
        return

    params = {
        "client_id": config["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    auth_url = f"{config.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')}?{urllib.parse.urlencode(params)}"
    
    st.markdown(f'''
        <a href="{auth_url}" target="_self" style="
            display: flex; justify-content: center; align-items: center; gap: 10px;
            padding: 0.6rem 1rem; background-color: #ffffff; color: #1e1e1e;
            border-radius: 8px; text-decoration: none; font-weight: 600; width: 100%;
            border: 1px solid #d1d5db; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: background-color 0.2s;
        " onmouseover="this.style.backgroundColor='#f9fafb'" onmouseout="this.style.backgroundColor='#ffffff'">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg^{"{1}"}" width="20" height="20">
            Sign in with Google
        </a>
    '''.replace("^{1}", ""), unsafe_allow_html=True)



# ── Guard decorator / helper ──────────────────────────────────────────────────
def require_auth(redirect_to: str = None):
    """
    Call at the top of any protected page.
    Shows a warning and stops execution if the user is not logged in.

    Usage:
        from auth_handler import require_auth
        require_auth()
    """
    if not is_authenticated():
        st.warning("🔒 Please log in from the main page to continue.")
        if redirect_to:
            st.page_link(redirect_to, label="Go to Login →")
        st.stop()


# ── Module self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("auth_handler self-test")
    ok, msg = login("Kush", "Kushagra")
    print(f"Login test → ok={ok}, msg='{msg}'")
    ok2, msg2 = login("Kush", "wrong_password")
    print(f"Bad pass   → ok={ok2}, msg='{msg2}'")