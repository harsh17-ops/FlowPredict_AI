import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import os

# ── Environment Variables ──────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── Page config — MUST be first ───────────────────────────
st.set_page_config(
    page_title="FlowPredict AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Users DB ───────────────────────────────────────────────
USERS = {
    "admin@flowpredict.ai":    {"password": "admin123",  "role": "Admin",    "company": "FlowPredict Industries"},
    "manager@acmecorp.com":    {"password": "acme2024",  "role": "Manager",  "company": "ACME Manufacturing"},
    "operator@steelworks.com": {"password": "steel2024", "role": "Operator", "company": "SteelWorks Ltd"},
}

# ── Session state ──────────────────────────────────────────
for key, val in {
    "logged_in":  False,
    "user_email": "",
    "user_info":  {},
    "page":       "landing",
    "prediction": None,
    "history":    [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS — Applied once at top
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #080f1a !important;
    color: #e2e8f0 !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* All text inputs */
.stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
.stTextInput label {
    color: rgba(255,255,255,0.7) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}
.stTextInput input:focus {
    border-color: #0077b6 !important;
    box-shadow: 0 0 0 2px rgba(0,119,182,0.25) !important;
}

/* All select boxes */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
}
.stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 13px !important; }

/* Number inputs */
.stNumberInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
}
.stNumberInput label { color: rgba(255,255,255,0.7) !important; font-size: 13px !important; }

/* Sliders */
.stSlider label { color: rgba(255,255,255,0.7) !important; font-size: 13px !important; }
.stSlider [data-baseweb="slider"] { margin-top: 4px !important; }
[data-baseweb="slider"] [data-testid="stThumbValue"] { color: #00b4d8 !important; font-weight: 600 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0077b6, #023e8a) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(0,119,182,0.35) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0090d4, #0353a4) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,119,182,0.5) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Dataframes */
.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(0,119,182,0.1) !important;
    border: 1px solid rgba(0,119,182,0.25) !important;
    border-radius: 14px !important;
    padding: 20px !important;
}
[data-testid="metric-container"] label {
    color: rgba(255,255,255,0.55) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #00b4d8 !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a1628; }
::-webkit-scrollbar-thumb { background: #0077b6; border-radius: 3px; }

/* Remove white backgrounds from containers */
.stContainer, div[data-testid="stVerticalBlock"] > div {
    background: transparent !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #0077b6 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HELPER — card HTML
# ══════════════════════════════════════════════════════════
def card(content, padding="24px", bg="rgba(255,255,255,0.04)",
         border="rgba(255,255,255,0.09)", radius="16px", extra=""):
    st.markdown(
        f'<div style="background:{bg};border:1px solid {border};'
        f'border-radius:{radius};padding:{padding};{extra}">{content}</div>',
        unsafe_allow_html=True
    )

def page_header(icon, title, subtitle):
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#080f1a,#0d1f35);
        padding:32px 48px 28px;border-bottom:1px solid rgba(255,255,255,0.07);">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
          <span style="font-size:26px;">{icon}</span>
          <h2 style="color:white;font-size:22px;font-weight:800;margin:0;letter-spacing:-0.5px;">{title}</h2>
        </div>
        <p style="color:rgba(255,255,255,0.4);font-size:13px;margin:0;padding-left:38px;">{subtitle}</p>
        </div>""",
        unsafe_allow_html=True
    )

def section_title(text, color="#00b4d8"):
    st.markdown(
        f'<p style="color:{color};font-size:12px;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:1.2px;margin:0 0 12px;">{text}</p>',
        unsafe_allow_html=True
    )

def sp(h=8):
    st.markdown(f'<div style="height:{h}px"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════
def landing_page():
    # NAV
    st.markdown("""
    <div style="background:#080f1a;padding:18px 56px;
    border-bottom:1px solid rgba(255,255,255,0.07);
    display:flex;justify-content:space-between;align-items:center;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:24px;">⚙️</span>
        <span style="font-size:20px;font-weight:800;color:#00b4d8;letter-spacing:-0.5px;">FlowPredict AI</span>
      </div>
      <div style="display:flex;gap:36px;">
        <span style="color:rgba(255,255,255,0.55);font-size:14px;font-weight:500;cursor:pointer;">Features</span>
        <span style="color:rgba(255,255,255,0.55);font-size:14px;font-weight:500;cursor:pointer;">How It Works</span>
        <span style="color:rgba(255,255,255,0.55);font-size:14px;font-weight:500;cursor:pointer;">About</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # HERO BADGE
    st.markdown("""
    <div style="text-align:center;padding:64px 40px 16px;">
      <div style="display:inline-block;background:rgba(0,180,216,0.1);
      border:1px solid rgba(0,180,216,0.3);border-radius:50px;
      padding:7px 20px;font-size:12px;color:#00b4d8;font-weight:600;
      letter-spacing:0.5px;margin-bottom:28px;">
        🏭 &nbsp; AI-Powered Manufacturing Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    # HERO HEADLINE
    st.markdown("""
    <div style="text-align:center;padding:0 40px;">
      <h1 style="font-size:58px;font-weight:800;color:white;
      line-height:1.08;margin:0 0 22px;letter-spacing:-2px;">
        Predict. Optimize.<br/>
        <span style="background:linear-gradient(90deg,#0077b6,#00b4d8,#48cae4);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          Manufacture Smarter.
        </span>
      </h1>
      <p style="font-size:17px;color:rgba(255,255,255,0.55);
      max-width:580px;margin:0 auto 48px;line-height:1.75;">
        FlowPredict AI uses Gradient Boosting ML to forecast manufacturing
        output in real-time — helping you maximize efficiency and hit targets.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # STATS ROW
    s1, s2, s3, s4 = st.columns(4)
    stat_style = "text-align:center;padding:24px 10px;"
    num_style  = "font-size:38px;font-weight:800;color:#00b4d8;"
    lbl_style  = "font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;font-weight:500;text-transform:uppercase;letter-spacing:0.8px;"

    with s1:
        st.markdown(f'<div style="{stat_style}"><div style="{num_style}">91%</div>'
                    f'<div style="{lbl_style}">Model Accuracy</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div style="{stat_style}"><div style="{num_style}">1000+</div>'
                    f'<div style="{lbl_style}">Training Samples</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div style="{stat_style}"><div style="{num_style}">17</div>'
                    f'<div style="{lbl_style}">Input Features</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div style="{stat_style}"><div style="{num_style}">5</div>'
                    f'<div style="{lbl_style}">ML Models Tested</div></div>', unsafe_allow_html=True)

    sp(16)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 40px;"/>', unsafe_allow_html=True)
    sp(40)

    # FEATURE CARDS
    st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.35);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:28px;">CORE FEATURES</p>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("🤖", "ML Regression",       "Gradient Boosting model trained on 1000 real manufacturing samples for precise output forecasting."),
        ("⚡", "Real-Time Prediction", "Instant predictions via FastAPI — results delivered in under 100ms through a clean REST API."),
        ("🎙️", "Voice Assistant",      "Ask FlowPredict AI anything using your voice — powered by Vapi AI voice agent integration."),
        ("📊", "Analytics Dashboard",  "Track prediction history, spot trends, and monitor output performance with interactive charts."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
            border-radius:16px;padding:28px 22px;height:180px;transition:border-color 0.2s;"
            onmouseover="this.style.borderColor='rgba(0,119,182,0.5)'"
            onmouseout="this.style.borderColor='rgba(255,255,255,0.08)'">
              <div style="font-size:28px;margin-bottom:14px;">{icon}</div>
              <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">{title}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    sp(48)

    # CTA BUTTON
    _, c, _ = st.columns([1.5, 1, 1.5])
    with c:
        if st.button("🚀  Get Started — Login"):
            st.session_state.page = "login"
            st.rerun()

    sp(32)
    st.markdown('<p style="text-align:center;color:rgba(255,255,255,0.2);font-size:12px;">FlowPredict AI  ·  Capstone Project  ·  Gradient Boosting Regression</p>', unsafe_allow_html=True)
    sp(20)


# ══════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════
def login_page():
    sp(60)
    _, center, _ = st.columns([1, 1.1, 1])
    with center:
        # Logo header
        st.markdown("""
        <div style="text-align:center;margin-bottom:32px;">
          <div style="font-size:44px;margin-bottom:12px;">⚙️</div>
          <h2 style="color:white;font-size:26px;font-weight:800;
          margin:0 0 6px;letter-spacing:-0.8px;">FlowPredict AI</h2>
          <p style="color:rgba(255,255,255,0.4);font-size:14px;margin:0;">
            Sign in to your company account
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Form card
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.1);
        border-radius:20px;padding:32px 32px 8px;">
        """, unsafe_allow_html=True)

        email    = st.text_input("📧  Company Email",    placeholder="you@company.com",  key="login_email")
        password = st.text_input("🔒  Password",         type="password",
                                  placeholder="Enter your password", key="login_pass")
        sp(8)

        if st.button("Sign In  →", key="signin_btn"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.session_state.user_info  = USERS[email]
                st.session_state.page       = "dashboard"
                st.rerun()
            else:
                st.error("❌  Invalid email or password. Check the demo accounts below.")

        st.markdown("</div>", unsafe_allow_html=True)
        sp(16)

        # Demo credentials
        st.markdown("""
        <div style="background:rgba(0,119,182,0.08);
        border:1px solid rgba(0,119,182,0.2);
        border-radius:12px;padding:16px 20px;">
          <p style="color:#00b4d8;font-size:12px;font-weight:700;
          text-transform:uppercase;letter-spacing:0.8px;margin:0 0 10px;">
            Demo Accounts
          </p>
          <p style="color:rgba(255,255,255,0.55);font-size:12px;
          margin:0;line-height:2;font-family:monospace;">
            admin@flowpredict.ai &nbsp;/&nbsp; admin123<br/>
            manager@acmecorp.com &nbsp;/&nbsp; acme2024<br/>
            operator@steelworks.com &nbsp;/&nbsp; steel2024
          </p>
        </div>
        """, unsafe_allow_html=True)

        sp(12)
        if st.button("←  Back to Home", key="back_home"):
            st.session_state.page = "landing"
            st.rerun()


# ══════════════════════════════════════════════════════════
#  NAVBAR
# ══════════════════════════════════════════════════════════
def navbar():
    user = st.session_state.user_info
    st.markdown(f"""
    <div style="background:#080f1a;padding:14px 40px;
    border-bottom:1px solid rgba(255,255,255,0.08);
    display:flex;justify-content:space-between;align-items:center;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:20px;">⚙️</span>
        <span style="color:#00b4d8;font-weight:800;font-size:17px;letter-spacing:-0.3px;">FlowPredict AI</span>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="background:rgba(0,119,182,0.15);border:1px solid rgba(0,119,182,0.3);
        border-radius:20px;padding:5px 14px;font-size:12px;color:#00b4d8;font-weight:600;">
          🏢 &nbsp;{user.get('company','Company')}
        </div>
        <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);
        border-radius:20px;padding:5px 14px;font-size:12px;color:rgba(255,255,255,0.65);font-weight:500;">
          👤 &nbsp;{user.get('role','User')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab bar
    pages     = ["🏠  Dashboard", "🔮  Predict", "📈  Analytics", "🎙️  Voice AI", "⚙️  Settings"]
    page_keys = ["dashboard", "predict", "analytics", "voice", "settings"]
    cols      = st.columns(5)
    for col, label, key in zip(cols, pages, page_keys):
        is_active = st.session_state.page == key
        with col:
            st.markdown(f"""
            <style>
            div[data-testid="column"]:nth-of-type({page_keys.index(key)+1}) .stButton > button {{
                background: {"linear-gradient(135deg,#0077b6,#023e8a)" if is_active else "transparent"} !important;
                border: {"none" if is_active else "none"} !important;
                border-bottom: {"3px solid #00b4d8" if is_active else "3px solid transparent"} !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                font-size: 13px !important;
                font-weight: {"700" if is_active else "500"} !important;
                color: {"white" if is_active else "rgba(255,255,255,0.45)"} !important;
                padding: 12px 8px !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            if st.button(label, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()


# ══════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════
def dashboard_page():
    navbar()
    user = st.session_state.user_info
    page_header("🏠", f"Good day, {user.get('role','User')} 👋",
                "Manufacturing Intelligence Dashboard — FlowPredict AI")

    st.markdown('<div style="padding:28px 48px;background:#080f1a;">', unsafe_allow_html=True)

    # KPI Row
    preds   = len(st.session_state.history)
    avg_out = round(sum(h['output'] for h in st.session_state.history) / preds, 1) if preds else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Model R² Score",      "91.0%")
    with k2: st.metric("RMSE",                "3.46 parts/hr")
    with k3: st.metric("Predictions Made",    preds)
    with k4: st.metric("Avg Output",          f"{avg_out} parts/hr")

    sp(24)

    col_l, col_r = st.columns([1, 1.6])

    with col_l:
        section_title("Quick Actions")
        if st.button("🔮  New Prediction", key="dash_predict"):
            st.session_state.page = "predict"
            st.rerun()
        sp(8)
        if st.button("🎙️  Ask Voice AI", key="dash_voice"):
            st.session_state.page = "voice"
            st.rerun()
        sp(8)
        if st.button("📈  View Analytics", key="dash_analytics"):
            st.session_state.page = "analytics"
            st.rerun()

    with col_r:
        section_title("Model Information")
        rows = [
            ("Algorithm",         "Gradient Boosting Regressor"),
            ("Training Samples",  "1,000 rows"),
            ("Features",          "17 manufacturing parameters"),
            ("Cross Validation",  "5-Fold KFold"),
            ("Target Variable",   "Parts Per Hour"),
            ("Best CV R²",        "0.8857 ± 0.0157"),
            ("Dataset Mean",      "29.3 parts/hr"),
            ("Dataset Range",     "5.0 – 68.6 parts/hr"),
        ]
        table_html = '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;overflow:hidden;">'
        for i, (k, v) in enumerate(rows):
            bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
            table_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
            padding:11px 20px;background:{bg};border-bottom:1px solid rgba(255,255,255,0.05);">
              <span style="color:rgba(255,255,255,0.45);font-size:12px;font-weight:500;">{k}</span>
              <span style="color:#00b4d8;font-size:13px;font-weight:600;">{v}</span>
            </div>"""
        table_html += "</div>"
        st.markdown(table_html, unsafe_allow_html=True)

    sp(24)

    # Model comparison mini chart
    section_title("Model Comparison (R² Score)")
    model_data = pd.DataFrame({
        "Model": ["Linear Reg", "Ridge Reg", "Random Forest", "XGBoost", "Gradient Boost"],
        "R2":    [0.8946,       0.8947,       0.8563,          0.8855,    0.9084],
    }).sort_values("R2")

    fig = go.Figure(go.Bar(
        x=model_data["R2"],
        y=model_data["Model"],
        orientation='h',
        marker=dict(
            color=["#1a3a5c","#1a3a5c","#1a3a5c","#1a3a5c","#00b4d8"],
            line=dict(color='rgba(0,0,0,0)', width=0)
        ),
        text=[f"{v:.4f}" for v in model_data["R2"]],
        textposition='outside',
        textfont=dict(color='white', size=11)
    ))
    fig.update_layout(
        height=240,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=60, t=10, b=10),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0.8, 0.95]),
        yaxis=dict(tickfont=dict(color='rgba(255,255,255,0.6)', size=12)),
        font=dict(color='white'),
        bargap=0.35
    )
    st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PREDICT PAGE
# ══════════════════════════════════════════════════════════
def predict_page():
    navbar()
    page_header("🔮", "Manufacturing Output Predictor",
                "Enter machine parameters to get an instant ML-powered prediction")

    st.markdown('<div style="padding:24px 48px 40px;background:#080f1a;">', unsafe_allow_html=True)

    # ── Section 1: Temperature & Pressure ──
    section_title("🌡️  Temperature & Pressure Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1: inj_temp  = st.slider("Injection Temp (°C)",     180.0, 300.0, 215.0, 0.5)
    with c2: inj_pres  = st.slider("Injection Pressure (bar)", 50.0, 200.0, 120.0, 0.5)
    with c3: amb_temp  = st.slider("Ambient Temp (°C)",        15.0,  45.0,  25.0, 0.5)
    with c4: temp_pres = st.slider("Temp/Pressure Ratio",       0.5,   5.0,   1.8, 0.1)

    sp(16)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);"/>', unsafe_allow_html=True)
    sp(16)

    # ── Section 2: Cycle & Time ──
    section_title("⏱️  Cycle & Time Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1: cycle_time   = st.slider("Cycle Time (sec)",        5.0,  60.0, 20.0, 0.5)
    with c2: cooling_time = st.slider("Cooling Time (sec)",       2.0,  30.0, 10.0, 0.5)
    with c3: total_cycle  = st.slider("Total Cycle Time (sec)",   8.0,  90.0, 30.0, 0.5)
    with c4: maint_hours  = st.number_input("Maintenance Hours",  0,   500,   50)

    sp(16)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);"/>', unsafe_allow_html=True)
    sp(16)

    # ── Section 3: Machine & Operator ──
    section_title("🏭  Machine & Operator Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        machine_age  = st.slider("Machine Age (yrs)",   0.0,  20.0,  5.0, 0.5)
        mat_visc     = st.slider("Material Viscosity",  50.0, 500.0, 200.0, 5.0)
    with c2:
        op_exp       = st.slider("Operator Experience", 0.0,  20.0,  5.0, 0.5)
        eff_score    = st.slider("Efficiency Score",    0.0, 100.0, 75.0, 1.0)
    with c3:
        machine_util = st.slider("Machine Utilization %", 0.0, 100.0, 80.0, 1.0)
    with c4:
        shift        = st.selectbox("Shift", [0, 1, 2],
                       format_func=lambda x: ["Morning","Afternoon","Night"][x])
        machine_type = st.selectbox("Machine Type", [0, 1, 2, 3],
                       format_func=lambda x: f"Type {x+1}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        mat_grade   = st.selectbox("Material Grade", [0, 1, 2],
                      format_func=lambda x: ["Grade A","Grade B","Grade C"][x])
    with c2:
        day_of_week = st.selectbox("Day of Week", list(range(7)),
                      format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])

    sp(24)

    # ── Predict Button ──
    _, bc, _ = st.columns([1.5, 1, 1.5])
    with bc:
        run = st.button("⚙️  Run Prediction  →", key="run_pred")

    if run:
        payload = {
            "Injection_Temperature":      inj_temp,
            "Injection_Pressure":         inj_pres,
            "Cycle_Time":                 cycle_time,
            "Cooling_Time":               cooling_time,
            "Material_Viscosity":         mat_visc,
            "Ambient_Temperature":        amb_temp,
            "Machine_Age":                machine_age,
            "Operator_Experience":        op_exp,
            "Maintenance_Hours":          float(maint_hours),
            "Shift":                      shift,
            "Machine_Type":               machine_type,
            "Material_Grade":             mat_grade,
            "Day_of_Week":                day_of_week,
            "Temperature_Pressure_Ratio": temp_pres,
            "Total_Cycle_Time":           total_cycle,
            "Efficiency_Score":           eff_score,
            "Machine_Utilization":        machine_util,
        }
        with st.spinner("Running ML prediction..."):
            time.sleep(0.4)
            try:
                res = requests.post(f"{BACKEND_URL}/predict",
                                    json=payload, timeout=5).json()
                st.session_state.prediction = res
                st.session_state.history.append({
                    "output": res["predicted_parts_per_hour"],
                    "status": res["status"]
                })
            except requests.exceptions.ConnectionError:
                st.error("❌  Backend not reachable — open a terminal and run:\n\n"
                         "`cd backend  &&  python -m uvicorn main:app --reload --port 8000`")
            except Exception as e:
                st.error(f"❌  Error: {e}")

    # ── Results ──
    if st.session_state.prediction:
        res       = st.session_state.prediction
        predicted = res["predicted_parts_per_hour"]
        status    = res["status"]
        mean_val  = 29.3
        diff      = round(predicted - mean_val, 1)
        pct       = round((predicted / 68.6) * 100, 1)

        sp(24)
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);"/>', unsafe_allow_html=True)
        sp(16)
        section_title("📊  Prediction Results")

        r1, r2, r3 = st.columns([1, 1.2, 1])

        with r1:
            clr = "#2d6a4f" if predicted >= 40 else ("#e65100" if predicted < 20 else "#0077b6")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{clr}cc,{clr}88);
            border:1px solid {clr};border-radius:18px;padding:32px 24px;text-align:center;">
              <div style="color:rgba(255,255,255,0.65);font-size:11px;font-weight:700;
              text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">
                Predicted Output
              </div>
              <div style="font-size:56px;font-weight:800;color:white;
              line-height:1;margin-bottom:6px;">{predicted}</div>
              <div style="color:rgba(255,255,255,0.55);font-size:14px;margin-bottom:20px;">
                parts / hour
              </div>
              <div style="background:rgba(0,0,0,0.25);border-radius:8px;
              padding:9px;font-size:14px;color:white;font-weight:700;">
                {status}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted,
                title={"text": "Parts Per Hour", "font": {"size": 13, "color": "white"}},
                number={"font": {"color": "white", "size": 38}, "suffix": ""},
                gauge={
                    "axis": {"range": [0, 70], "tickcolor": "rgba(255,255,255,0.3)",
                             "tickfont": {"color": "rgba(255,255,255,0.4)", "size": 10}},
                    "bar":  {"color": "#00b4d8", "thickness": 0.28},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  20], "color": "rgba(230,81,0,0.2)"},
                        {"range": [20, 40], "color": "rgba(0,119,182,0.2)"},
                        {"range": [40, 70], "color": "rgba(45,106,79,0.2)"},
                    ],
                    "threshold": {
                        "line": {"color": "#f77f00", "width": 2},
                        "thickness": 0.8,
                        "value": 29.3
                    }
                }
            ))
            fig.update_layout(
                height=230,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=0, l=20, r=20),
                font={"color": "white"}
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        with r3:
            arrow = "▲" if diff >= 0 else "▼"
            aclr  = "#4caf50" if diff >= 0 else "#f44336"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.09);
            border-radius:16px;padding:24px;height:230px;">
              <div style="color:rgba(255,255,255,0.35);font-size:11px;font-weight:700;
              text-transform:uppercase;letter-spacing:1px;margin-bottom:20px;">
                Performance Analysis
              </div>
              <div style="margin-bottom:18px;">
                <div style="color:rgba(255,255,255,0.4);font-size:11px;margin-bottom:4px;">
                  vs Dataset Average (29.3)
                </div>
                <div style="color:{aclr};font-size:22px;font-weight:700;">
                  {arrow} {abs(diff)} parts/hr
                </div>
              </div>
              <div style="margin-bottom:14px;">
                <div style="color:rgba(255,255,255,0.4);font-size:11px;margin-bottom:4px;">
                  Capacity Usage
                </div>
                <div style="color:#00b4d8;font-size:22px;font-weight:700;">{pct}%</div>
              </div>
              <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:6px;overflow:hidden;">
                <div style="background:linear-gradient(90deg,#0077b6,#00b4d8);
                height:100%;width:{min(pct,100)}%;border-radius:6px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Input summary
        sp(20)
        with st.expander("📋  View Input Summary"):
            st.dataframe(pd.DataFrame([{
                "Inj. Temp": inj_temp, "Inj. Pressure": inj_pres,
                "Cycle Time": cycle_time, "Cooling Time": cooling_time,
                "Ambient Temp": amb_temp, "Mat. Viscosity": mat_visc,
                "Machine Age": machine_age, "Op. Experience": op_exp,
                "Maintenance Hrs": maint_hours, "Efficiency": eff_score,
                "Utilization %": machine_util, "Shift": shift,
                "Machine Type": machine_type, "Material Grade": mat_grade,
                "Day": day_of_week,
            }]), width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ANALYTICS PAGE
# ══════════════════════════════════════════════════════════
def analytics_page():
    navbar()
    page_header("📈", "Analytics & Insights",
                "Prediction history, trends, and model performance overview")

    st.markdown('<div style="padding:28px 48px 40px;background:#080f1a;">', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
        border-radius:16px;padding:72px;text-align:center;margin-top:8px;">
          <div style="font-size:44px;margin-bottom:16px;">📊</div>
          <div style="color:rgba(255,255,255,0.45);font-size:16px;margin-bottom:6px;">No predictions yet</div>
          <div style="color:rgba(255,255,255,0.25);font-size:13px;">
            Head to the Predict page and run your first prediction
          </div>
        </div>
        """, unsafe_allow_html=True)
        sp(16)
        _, c, _ = st.columns([2, 1, 2])
        with c:
            if st.button("→  Go to Predictor"):
                st.session_state.page = "predict"
                st.rerun()
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df.index = hist_df.index + 1

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Predictions", len(hist_df))
        with m2: st.metric("Average Output",    f"{hist_df['output'].mean():.1f} parts/hr")
        with m3: st.metric("Highest Output",    f"{hist_df['output'].max():.1f} parts/hr")
        with m4: st.metric("Lowest Output",     f"{hist_df['output'].min():.1f} parts/hr")

        sp(24)
        c1, c2 = st.columns(2)

        with c1:
            section_title("Prediction History Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist_df.index, y=hist_df["output"],
                mode="lines+markers",
                line=dict(color="#00b4d8", width=2.5),
                marker=dict(color="#00b4d8", size=7, line=dict(color="white", width=1.5)),
                fill="tozeroy",
                fillcolor="rgba(0,180,216,0.08)"
            ))
            fig.add_hline(y=29.3, line_dash="dash",
                         line_color="rgba(255,165,0,0.5)",
                         annotation_text="Dataset Mean",
                         annotation_font_color="rgba(255,165,0,0.7)")
            fig.update_layout(
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(title="Prediction #", gridcolor="rgba(255,255,255,0.05)",
                          tickfont=dict(color="rgba(255,255,255,0.4)")),
                yaxis=dict(title="Parts/Hr", gridcolor="rgba(255,255,255,0.05)",
                          tickfont=dict(color="rgba(255,255,255,0.4)")),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        with c2:
            section_title("Output Status Distribution")
            counts = hist_df["status"].value_counts()
            clr_map = {
                "🟢 High Output":   "#2d6a4f",
                "🟡 Normal Output": "#0077b6",
                "🔴 Low Output":    "#c62828"
            }
            fig2 = go.Figure(go.Pie(
                labels=counts.index,
                values=counts.values,
                hole=0.55,
                marker=dict(colors=[clr_map.get(k, "#555") for k in counts.index],
                           line=dict(color="#080f1a", width=2)),
                textfont=dict(color="white", size=12),
            ))
            fig2.update_layout(
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(font=dict(color="rgba(255,255,255,0.6)", size=11),
                           bgcolor="rgba(0,0,0,0)"),
                showlegend=True
            )
            st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

        sp(8)
        section_title("Full Prediction Log")
        st.dataframe(hist_df, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  VOICE AI PAGE
# ══════════════════════════════════════════════════════════
def voice_page():
    navbar()
    page_header("🎙️", "Voice AI Assistant",
                "Ask FlowPredict AI anything using your voice — powered by Vapi")

    # ── Widget is securely served by the FastAPI Backend to fix WebRTC origin blocking ──
    st.markdown(f'<iframe src="{BACKEND_URL}/vapi" allow="microphone; autoplay; camera" width="100%" height="600" style="border:none;"></iframe>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  SETTINGS PAGE
# ══════════════════════════════════════════════════════════
def settings_page():
    navbar()
    page_header("⚙️", "Settings", "Account information and preferences")

    st.markdown('<div style="padding:28px 48px 40px;background:#080f1a;">', unsafe_allow_html=True)

    user = st.session_state.user_info
    _, col, _ = st.columns([1, 2, 1])

    with col:
        section_title("Account Information")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.09);
        border-radius:16px;padding:28px;margin-bottom:24px;">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;
          padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,0.07);">
            <div style="width:56px;height:56px;border-radius:50%;
            background:linear-gradient(135deg,#0077b6,#023e8a);
            display:flex;align-items:center;justify-content:center;
            font-size:22px;font-weight:800;color:white;">
              {user.get('role','U')[0]}
            </div>
            <div>
              <div style="color:white;font-size:16px;font-weight:700;">
                {user.get('role','User')}
              </div>
              <div style="color:rgba(255,255,255,0.45);font-size:13px;">
                {st.session_state.user_email}
              </div>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:14px;">
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);font-size:13px;">Company</span>
              <span style="color:#00b4d8;font-size:13px;font-weight:600;">
                {user.get('company','')}
              </span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);font-size:13px;">Role</span>
              <span style="color:#00b4d8;font-size:13px;font-weight:600;">
                {user.get('role','')}
              </span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);font-size:13px;">Predictions Made</span>
              <span style="color:#00b4d8;font-size:13px;font-weight:600;">
                {len(st.session_state.history)}
              </span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        section_title("App Information")
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.09);
        border-radius:16px;padding:22px 28px;margin-bottom:28px;">
          <div style="display:flex;flex-direction:column;gap:12px;font-size:13px;">
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);">Version</span>
              <span style="color:rgba(255,255,255,0.7);">1.0.0</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);">Backend</span>
              <span style="color:rgba(255,255,255,0.7);">FastAPI + Uvicorn</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);">ML Model</span>
              <span style="color:rgba(255,255,255,0.7);">Gradient Boosting Regressor</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
              <span style="color:rgba(255,255,255,0.4);">Project</span>
              <span style="color:rgba(255,255,255,0.7);">Capstone — Regression</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        div[data-testid="column"] .stButton > button[kind="secondary"],
        .logout-btn .stButton > button {
            background: linear-gradient(135deg,#7f1d1d,#991b1b) !important;
            box-shadow: 0 4px 14px rgba(127,29,29,0.4) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🚪  Sign Out", key="signout"):
            for k in ["logged_in","user_email","user_info","prediction","history"]:
                st.session_state[k] = False if k=="logged_in" else ({} if k=="user_info" else ([] if k=="history" else ""))
            st.session_state.page = "landing"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        landing_page()
else:
    p = st.session_state.page
    if   p == "predict":   predict_page()
    elif p == "analytics": analytics_page()
    elif p == "voice":     voice_page()
    elif p == "settings":  settings_page()
    else:                  dashboard_page()