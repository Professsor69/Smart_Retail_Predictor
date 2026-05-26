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

# ── Constants ─────────────────────────────────────────────────────────────────
COOKIE_NAME = "smart_retail_auth"
COOKIE_KEY  = "this_is_a_super_secret_key_change_me_in_prod"
REDIRECT_URI = "http://localhost:8501/"

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


# Google sign-in has been disabled



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