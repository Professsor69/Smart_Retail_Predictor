import streamlit as st
import time
import auth_handler

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Smart Retail Predictor", page_icon="🛒", layout="wide")

# 2. INITIALIZE GOOGLE AUTH (Disabled)

# 3. PREMIUM THEME
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
        --glow-teal: rgba(56,232,197,0.25);
    }

    html, body, .stApp {
        background-color: var(--bg-void) !important;
        background-image:
            radial-gradient(ellipse 70% 60% at 50% -10%, rgba(124,109,250,0.18) 0%, transparent 65%),
            radial-gradient(ellipse 50% 40% at 90% 100%, rgba(56,232,197,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 40% 30% at 0% 80%, rgba(124,109,250,0.07) 0%, transparent 60%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none'%3E%3Cg fill='%23ffffff' fill-opacity='0.013'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* Hide all chrome */
    #MainMenu, footer, header,
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] { display: none !important; }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Override Streamlit vertical block so we can center */
    [data-testid="stVerticalBlock"] {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* ── CARD ── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,0.028) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 28px !important;
        box-shadow:
            0 0 0 1px rgba(124,109,250,0.08),
            0 32px 80px rgba(0,0,0,0.7),
            0 0 60px rgba(124,109,250,0.08) !important;
        padding: 0 !important;
        overflow: hidden;
        width: min(900px, 92vw) !important;
        backdrop-filter: blur(20px);
    }

    /* ── LEFT PANEL ── */
    .left-panel {
        background: linear-gradient(160deg, rgba(124,109,250,0.12) 0%, rgba(56,232,197,0.06) 100%);
        border-right: 1px solid var(--border);
        padding: 52px 40px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .brand-mark {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 40px;
    }
    .brand-icon {
        width: 40px; height: 40px;
        background: linear-gradient(135deg, var(--accent-primary), #5b4fd4);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 16px var(--glow-purple);
    }
    .brand-name {
        font-family: 'Syne', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary) !important;
        letter-spacing: -0.3px;
    }
    .panel-headline {
        font-family: 'Syne', sans-serif;
        font-size: 38px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -1.5px;
        line-height: 1.1;
        margin-bottom: 16px;
    }
    .panel-headline span {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .panel-desc {
        font-size: 14px;
        color: var(--text-secondary) !important;
        line-height: 1.7;
        margin-bottom: 36px;
    }
    .feature-list { display: flex; flex-direction: column; gap: 12px; }
    .feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 13px;
        color: var(--text-secondary) !important;
    }
    .feature-dot {
        width: 28px; height: 28px;
        background: var(--surface-2);
        border: 1px solid var(--border-bright);
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px;
        flex-shrink: 0;
    }

    /* ── RIGHT PANEL ── */
    .right-panel {
        padding: 52px 44px;
    }
    .form-eyebrow {
        font-size: 11px;
        font-weight: 500;
        color: var(--accent-primary) !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 8px;
    }
    .form-title {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: var(--text-primary) !important;
        letter-spacing: -0.8px;
        margin-bottom: 6px;
    }
    .form-sub {
        font-size: 13px;
        color: var(--text-secondary) !important;
        margin-bottom: 28px !important;
    }

    /* Inputs */
    .stTextInput label p {
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 6px !important;
    }
    [data-baseweb="input"] > div {
        background: var(--surface-1) !important;
        border: 1px solid var(--border-bright) !important;
        border-radius: 12px !important;
        min-height: 46px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    [data-baseweb="input"] > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(124,109,250,0.15) !important;
    }
    [data-baseweb="input"] input {
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
        padding: 0 14px !important;
    }
    [data-baseweb="input"] input::placeholder { color: var(--text-secondary) !important; opacity: 0.6; }

    /* Forgot password */
    .forgot-row {
        text-align: right;
        font-size: 12px;
        color: var(--accent-primary) !important;
        margin: -4px 0 20px 0;
        cursor: pointer;
        opacity: 0.8;
    }
    .forgot-row:hover { opacity: 1; }

    /* Buttons */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        height: 46px !important;
        transition: all 0.2s !important;
        letter-spacing: 0.5px !important;
    }
    /* Secondary */
    .stButton > button:not([kind="primary"]) {
        background: var(--surface-2) !important;
        border: 1px solid var(--border-bright) !important;
        color: var(--text-primary) !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(124,109,250,0.1) !important;
        border-color: rgba(124,109,250,0.4) !important;
        box-shadow: 0 0 16px var(--glow-purple) !important;
    }
    /* Primary */
    .stButton > button[kind="primary"],
    [data-testid="baseButton-primary"] button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #5b4fd4 100%) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 4px 20px var(--glow-purple) !important;
    }
    .stButton > button[kind="primary"]:hover,
    [data-testid="baseButton-primary"] button:hover {
        box-shadow: 0 8px 32px rgba(124,109,250,0.6) !important;
        transform: translateY(-2px) !important;
    }

    /* Divider */
    .or-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 24px 0;
    }
    .or-line { flex: 1; height: 1px; background: var(--border); }
    .or-text {
        font-size: 11px;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Alerts */
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
    [data-testid="stWarning"] {
        background: rgba(251,191,36,0.06) !important;
        border: 1px solid rgba(251,191,36,0.25) !important;
        border-radius: 12px !important;
    }
    .stSpinner > div { border-top-color: var(--accent-primary) !important; }

    p, span, label { color: var(--text-secondary) !important; font-family: 'DM Sans', sans-serif !important; }
    </style>
""", unsafe_allow_html=True)

# 4. SESSION STATE
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login'

def switch_mode(mode):
    st.session_state['auth_mode'] = mode

# 5. LAYOUT
with st.container(border=True):
    left_col, right_col = st.columns([1.1, 1])

    # ── LEFT PANEL ──
    with left_col:
        st.markdown("""
            <div class="left-panel">
                <div>
                    <div class="brand-mark">
                        <div class="brand-icon">🛒</div>
                        <span class="brand-name">Smart Retail</span>
                    </div>
                    <div class="panel-headline">
                        Your data,<br><span>intelligently</span><br>forecasted.
                    </div>
                    <p class="panel-desc">
                        Upload your sales data and let our AI-powered engine surface trends,
                        predict demand, and surface actionable insights — all in one place.
                    </p>
                    <div class="feature-list">
                        <div class="feature-item">
                            <div class="feature-dot">📊</div>
                            <span>Real-time analytics dashboard</span>
                        </div>
                        <div class="feature-item">
                            <div class="feature-dot">🤖</div>
                            <span>30-day ML demand forecasting</span>
                        </div>
                        <div class="feature-item">
                            <div class="feature-dot">⚡</div>
                            <span>Instant CSV & Excel ingestion</span>
                        </div>
                        <div class="feature-item">
                            <div class="feature-dot">🔒</div>
                            <span>Isolated per-user data environment</span>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ── RIGHT PANEL ──
    with right_col:
        is_login = st.session_state['auth_mode'] == 'login'

        if is_login:
            st.markdown("""
                <div class="form-eyebrow">Welcome back</div>
                <div class="form-title">Sign in</div>
                <p class="form-sub">Enter your credentials to access your workspace.</p>
            """, unsafe_allow_html=True)

            user_input = st.text_input("Username", placeholder="e.g. Kush")
            pass_input = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<div class='forgot-row'>Forgot password?</div>", unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Sign In", type="primary", use_container_width=True):
                    with st.spinner("Authenticating..."):
                        time.sleep(0.5)
                        ok, msg = auth_handler.login(user_input, pass_input)
                        if ok:
                            st.switch_page("pages/1_📊_Dashboard.py")
                        else:
                            st.error(msg)
            with btn_col2:
                st.button("Create Account", on_click=switch_mode, args=('signup',), use_container_width=True)

        else:
            st.markdown("""
                <div class="form-eyebrow">Get started</div>
                <div class="form-title">Create account</div>
                <p class="form-sub">Choose a username and password to get started.</p>
            """, unsafe_allow_html=True)

            new_user = st.text_input("Username", placeholder="e.g. Kush")
            new_pass = st.text_input("Password", type="password", placeholder="••••••••")

            st.write("")

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.button("← Back to Sign In", on_click=switch_mode, args=('login',), use_container_width=True)
            with btn_col2:
                if st.button("Create Account", type="primary", use_container_width=True):
                    with st.spinner("Creating account..."):
                        ok, msg = auth_handler.register(new_user, new_pass)
                        if ok:
                            st.success("Account created! Signing you in...")
                            time.sleep(1)
                            st.switch_page("pages/1_📊_Dashboard.py")
                        else:
                            st.warning(msg)

        # Google sign-in has been disabled