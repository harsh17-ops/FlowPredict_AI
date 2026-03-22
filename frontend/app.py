import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time

st.set_page_config(
    page_title="FlowPredict AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Demo company accounts ──────────────────────────────────
USERS = {
    "admin@flowpredict.ai":    {"password": "admin123",   "role": "Admin",    "company": "FlowPredict Industries"},
    "manager@acmecorp.com":    {"password": "acme2024",   "role": "Manager",  "company": "ACME Manufacturing"},
    "operator@steelworks.com": {"password": "steel2024",  "role": "Operator", "company": "SteelWorks Ltd"},
}

# ── Session state init ─────────────────────────────────────
if "logged_in"   not in st.session_state: st.session_state.logged_in   = False
if "user_email"  not in st.session_state: st.session_state.user_email  = ""
if "user_info"   not in st.session_state: st.session_state.user_info   = {}
if "page"        not in st.session_state: st.session_state.page        = "landing"
if "prediction"  not in st.session_state: st.session_state.prediction  = None
if "history"     not in st.session_state: st.session_state.history     = []

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  * { font-family: 'Inter', sans-serif !important; }

  /* Hide streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0a1628; }
  ::-webkit-scrollbar-thumb { background: #0077b6; border-radius: 3px; }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #0077b6, #023e8a) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    font-size: 15px !important; padding: 12px 32px !important;
    width: 100% !important; transition: all 0.3s !important;
    box-shadow: 0 4px 15px rgba(0,119,182,0.4) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,119,182,0.5) !important;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
  }

  /* Sliders */
  .stSlider > div > div > div > div {
    background: #0077b6 !important;
  }

  /* Metric */
  [data-testid="metric-container"] {
    background: rgba(0,119,182,0.1);
    border: 1px solid rgba(0,119,182,0.3);
    border-radius: 12px;
    padding: 16px;
  }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 1 — LANDING
# ══════════════════════════════════════════════════════════
def landing_page():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%);
                min-height: 100vh; padding: 0;">

      <!-- NAV -->
      <div style="display:flex; justify-content:space-between; align-items:center;
                  padding: 20px 60px; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:28px;">⚙️</span>
          <span style="font-size:22px; font-weight:800; color:#00b4d8;
                       letter-spacing:-0.5px;">FlowPredict AI</span>
        </div>
        <div style="display:flex; gap:32px; color:rgba(255,255,255,0.7);
                    font-size:14px; font-weight:500;">
          <span>Features</span>
          <span>How It Works</span>
          <span>About</span>
        </div>
      </div>

      <!-- HERO -->
      <div style="text-align:center; padding: 80px 60px 60px;">
        <div style="display:inline-block; background:rgba(0,180,216,0.1);
                    border:1px solid rgba(0,180,216,0.3); border-radius:50px;
                    padding:8px 20px; margin-bottom:24px; font-size:13px;
                    color:#00b4d8; font-weight:600;">
          🏭 AI-Powered Manufacturing Intelligence
        </div>

        <h1 style="font-size:62px; font-weight:800; color:white; line-height:1.1;
                   margin:0 0 20px; letter-spacing:-2px;">
          Predict. Optimize.<br/>
          <span style="background: linear-gradient(90deg, #0077b6, #00b4d8);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Manufacture Smarter.
          </span>
        </h1>

        <p style="font-size:18px; color:rgba(255,255,255,0.6); max-width:600px;
                  margin: 0 auto 40px; line-height:1.7;">
          FlowPredict AI uses machine learning to forecast manufacturing output in
          real-time — helping you maximize efficiency, reduce downtime, and
          outperform targets.
        </p>

        <!-- STATS ROW -->
        <div style="display:flex; justify-content:center; gap:48px; margin-bottom:48px;">
          <div style="text-align:center;">
            <div style="font-size:36px; font-weight:800; color:#00b4d8;">91%</div>
            <div style="font-size:13px; color:rgba(255,255,255,0.5);">Model Accuracy</div>
          </div>
          <div style="width:1px; background:rgba(255,255,255,0.1);"></div>
          <div style="text-align:center;">
            <div style="font-size:36px; font-weight:800; color:#00b4d8;">1000+</div>
            <div style="font-size:13px; color:rgba(255,255,255,0.5);">Training Samples</div>
          </div>
          <div style="width:1px; background:rgba(255,255,255,0.1);"></div>
          <div style="text-align:center;">
            <div style="font-size:36px; font-weight:800; color:#00b4d8;">17</div>
            <div style="font-size:13px; color:rgba(255,255,255,0.5);">Input Features</div>
          </div>
          <div style="width:1px; background:rgba(255,255,255,0.1);"></div>
          <div style="text-align:center;">
            <div style="font-size:36px; font-weight:800; color:#00b4d8;">5</div>
            <div style="font-size:13px; color:rgba(255,255,255,0.5);">ML Models Tested</div>
          </div>
        </div>
      </div>

      <!-- FEATURE CARDS -->
      <div style="display:flex; gap:24px; padding:0 60px 60px; justify-content:center;">
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; flex:1; max-width:260px;">
          <div style="font-size:32px; margin-bottom:12px;">🤖</div>
          <div style="font-size:16px; font-weight:700; color:white; margin-bottom:8px;">
            ML Regression
          </div>
          <div style="font-size:13px; color:rgba(255,255,255,0.5); line-height:1.6;">
            Gradient Boosting model trained on real manufacturing data for precise output prediction.
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; flex:1; max-width:260px;">
          <div style="font-size:32px; margin-bottom:12px;">⚡</div>
          <div style="font-size:16px; font-weight:700; color:white; margin-bottom:8px;">
            Real-Time Prediction
          </div>
          <div style="font-size:13px; color:rgba(255,255,255,0.5); line-height:1.6;">
            Instant predictions via FastAPI backend — results in under 100ms.
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; flex:1; max-width:260px;">
          <div style="font-size:32px; margin-bottom:12px;">🎙️</div>
          <div style="font-size:16px; font-weight:700; color:white; margin-bottom:8px;">
            Voice Assistant
          </div>
          <div style="font-size:13px; color:rgba(255,255,255,0.5); line-height:1.6;">
            Ask FlowPredict AI questions using your voice — powered by Vapi AI agent.
          </div>
        </div>
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; flex:1; max-width:260px;">
          <div style="font-size:32px; margin-bottom:12px;">📊</div>
          <div style="font-size:16px; font-weight:700; color:white; margin-bottom:8px;">
            Analytics Dashboard
          </div>
          <div style="font-size:13px; color:rgba(255,255,255,0.5); line-height:1.6;">
            Track prediction history, spot trends and monitor output performance over time.
          </div>
        </div>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🚀  Get Started — Login"):
            st.session_state.page = "login"
            st.rerun()


# ══════════════════════════════════════════════════════════
#  PAGE 2 — LOGIN
# ══════════════════════════════════════════════════════════
def login_page():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0a1628, #0d2137);
                min-height:100vh; display:flex; align-items:center;
                justify-content:center; padding:40px;">
      <div style="text-align:center; margin-bottom:32px;">
        <div style="font-size:48px;">⚙️</div>
        <h2 style="color:white; font-size:28px; font-weight:800;
                   margin:8px 0 4px; letter-spacing:-1px;">FlowPredict AI</h2>
        <p style="color:rgba(255,255,255,0.5); font-size:14px;">
          Sign in to your company account
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.1);
                    border-radius:20px; padding:36px; margin-top:-80px;">
          <h3 style="color:white; font-weight:700; margin:0 0 24px;
                     font-size:20px;">Welcome Back</h3>
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("📧  Company Email", placeholder="you@company.com")
        password = st.text_input("🔒  Password", type="password", placeholder="Enter password")

        st.markdown("<br/>", unsafe_allow_html=True)

        if st.button("Sign In →"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.session_state.user_info  = USERS[email]
                st.session_state.page       = "dashboard"
                st.success(f"✅ Welcome, {USERS[email]['company']}!")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

        st.markdown("""
        <div style="margin-top:20px; padding:14px; background:rgba(0,119,182,0.1);
                    border:1px solid rgba(0,119,182,0.2); border-radius:10px;">
          <p style="color:rgba(255,255,255,0.6); font-size:12px; margin:0;">
            <strong style="color:#00b4d8;">Demo Accounts:</strong><br/>
            admin@flowpredict.ai / admin123<br/>
            manager@acmecorp.com / acme2024<br/>
            operator@steelworks.com / steel2024
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()


# ══════════════════════════════════════════════════════════
#  NAVBAR (shown when logged in)
# ══════════════════════════════════════════════════════════
def navbar():
    user = st.session_state.user_info
    st.markdown(f"""
    <div style="background:#0d2137; border-bottom:1px solid rgba(255,255,255,0.08);
                padding:14px 40px; display:flex;
                justify-content:space-between; align-items:center;
                position:sticky; top:0; z-index:999;">
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:22px;">⚙️</span>
        <span style="color:#00b4d8; font-weight:800; font-size:18px;">FlowPredict AI</span>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <div style="background:rgba(0,119,182,0.2); border:1px solid rgba(0,119,182,0.4);
                    border-radius:20px; padding:6px 14px; font-size:12px; color:#00b4d8;">
          🏢 {user.get('company','Company')}
        </div>
        <div style="background:rgba(255,255,255,0.06); border-radius:20px;
                    padding:6px 14px; font-size:12px; color:rgba(255,255,255,0.7);">
          👤 {user.get('role','User')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tab navigation
    tabs = st.columns(5)
    pages = ["🏠 Dashboard", "🔮 Predict", "📈 Analytics", "🎙️ Voice AI", "⚙️ Settings"]
    page_keys = ["dashboard", "predict", "analytics", "voice", "settings"]

    for i, (tab, pg) in enumerate(zip(tabs, page_keys)):
        with tab:
            is_active = st.session_state.page == pg
            label = pages[i]
            if st.button(label, key=f"nav_{pg}",
                         help=f"Go to {label}"):
                st.session_state.page = pg
                st.rerun()


# ══════════════════════════════════════════════════════════
#  PAGE 3 — DASHBOARD (Home after login)
# ══════════════════════════════════════════════════════════
def dashboard_page():
    navbar()
    user = st.session_state.user_info

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a1628,#0d2137);
                padding:40px 48px 30px;">
      <h2 style="color:white; font-size:28px; font-weight:800; margin:0 0 4px;">
        Good day, {user.get('role','User')} 👋
      </h2>
      <p style="color:rgba(255,255,255,0.5); margin:0; font-size:15px;">
        Manufacturing Intelligence Dashboard — FlowPredict AI
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:0 48px; background:#0a1628;'>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)

    # KPI cards
    k1, k2, k3, k4 = st.columns(4)
    kpi_style = """background:rgba(0,119,182,0.12); border:1px solid rgba(0,119,182,0.25);
                   border-radius:14px; padding:20px; text-align:center;"""
    with k1:
        st.markdown(f"""<div style="{kpi_style}">
          <div style="font-size:32px; font-weight:800; color:#00b4d8;">91.0%</div>
          <div style="color:rgba(255,255,255,0.6); font-size:13px; margin-top:4px;">Model R² Score</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div style="{kpi_style}">
          <div style="font-size:32px; font-weight:800; color:#00b4d8;">3.46</div>
          <div style="color:rgba(255,255,255,0.6); font-size:13px; margin-top:4px;">RMSE (parts/hr)</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        preds = len(st.session_state.history)
        st.markdown(f"""<div style="{kpi_style}">
          <div style="font-size:32px; font-weight:800; color:#00b4d8;">{preds}</div>
          <div style="color:rgba(255,255,255,0.6); font-size:13px; margin-top:4px;">Predictions Made</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        avg = round(sum(h['output'] for h in st.session_state.history) / len(st.session_state.history), 1) if st.session_state.history else 0.0
        st.markdown(f"""<div style="{kpi_style}">
          <div style="font-size:32px; font-weight:800; color:#00b4d8;">{avg}</div>
          <div style="color:rgba(255,255,255,0.6); font-size:13px; margin-top:4px;">Avg Output (parts/hr)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Quick action + model info
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px;">
          <h4 style="color:white; margin:0 0 20px; font-size:16px;">🚀 Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔮  New Prediction"):
            st.session_state.page = "predict"
            st.rerun()
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🎙️  Ask Voice AI"):
            st.session_state.page = "voice"
            st.rerun()

    with col_right:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px;">
          <h4 style="color:white; margin:0 0 16px; font-size:16px;">🤖 Model Information</h4>
          <table style="width:100%; color:rgba(255,255,255,0.7); font-size:13px;">
            <tr><td style="padding:6px 0; color:rgba(255,255,255,0.4);">Algorithm</td>
                <td style="color:#00b4d8; font-weight:600;">Gradient Boosting Regressor</td></tr>
            <tr><td style="padding:6px 0; color:rgba(255,255,255,0.4);">Training Samples</td>
                <td>1000 rows</td></tr>
            <tr><td style="padding:6px 0; color:rgba(255,255,255,0.4);">Features</td>
                <td>17 manufacturing parameters</td></tr>
            <tr><td style="padding:6px 0; color:rgba(255,255,255,0.4);">Cross Validation</td>
                <td>5-Fold KFold</td></tr>
            <tr><td style="padding:6px 0; color:rgba(255,255,255,0.4);">Target</td>
                <td>Parts Per Hour</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 4 — PREDICT
# ══════════════════════════════════════════════════════════
def predict_page():
    navbar()

    st.markdown("""
    <div style="background:#0a1628; padding:32px 48px 0;">
      <h2 style="color:white; font-weight:800; font-size:24px; margin:0 0 4px;">
        🔮 Manufacturing Output Predictor
      </h2>
      <p style="color:rgba(255,255,255,0.4); font-size:14px; margin:0 0 24px;">
        Enter machine parameters below to get an instant prediction
      </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background:#0a1628; padding:0 48px 40px;'>", unsafe_allow_html=True)

        # Input section
        st.markdown("""<div style="background:rgba(255,255,255,0.03);
                    border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; margin-bottom:20px;">
          <h4 style="color:#00b4d8; margin:0 0 20px; font-size:15px; font-weight:700;">
            🌡️ Temperature & Pressure Parameters
          </h4></div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            inj_temp  = st.slider("Injection Temp (°C)", 180.0, 300.0, 215.0, step=0.5)
        with col2:
            inj_pres  = st.slider("Injection Pressure (bar)", 50.0, 200.0, 120.0, step=0.5)
        with col3:
            amb_temp  = st.slider("Ambient Temp (°C)", 15.0, 45.0, 25.0, step=0.5)
        with col4:
            temp_pres = st.slider("Temp/Pressure Ratio", 0.5, 5.0, 1.8, step=0.1)

        st.markdown("""<div style="background:rgba(255,255,255,0.03);
                    border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; margin-bottom:20px;">
          <h4 style="color:#00b4d8; margin:0 0 20px; font-size:15px; font-weight:700;">
            ⏱️ Cycle & Time Parameters
          </h4></div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cycle_time   = st.slider("Cycle Time (sec)",       5.0,  60.0, 20.0)
        with col2:
            cooling_time = st.slider("Cooling Time (sec)",     2.0,  30.0, 10.0)
        with col3:
            total_cycle  = st.slider("Total Cycle Time (sec)", 8.0,  90.0, 30.0)
        with col4:
            maint_hours  = st.number_input("Maintenance Hours", 0, 500, 50)

        st.markdown("""<div style="background:rgba(255,255,255,0.03);
                    border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:28px; margin-bottom:20px;">
          <h4 style="color:#00b4d8; margin:0 0 20px; font-size:15px; font-weight:700;">
            🏭 Machine & Operator Parameters
          </h4></div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            machine_age  = st.slider("Machine Age (yrs)",  0.0, 20.0, 5.0)
            mat_visc     = st.slider("Material Viscosity", 50.0, 500.0, 200.0)
        with col2:
            op_exp       = st.slider("Operator Experience", 0.0, 20.0, 5.0)
            eff_score    = st.slider("Efficiency Score",    0.0, 100.0, 75.0)
        with col3:
            machine_util = st.slider("Machine Utilization %", 0.0, 100.0, 80.0)
        with col4:
            shift        = st.selectbox("Shift", [0,1,2],
                           format_func=lambda x: ["Morning","Afternoon","Night"][x])
            machine_type = st.selectbox("Machine Type", [0,1,2,3],
                           format_func=lambda x: f"Type {x+1}")

        col1, col2 = st.columns(2)
        with col1:
            mat_grade   = st.selectbox("Material Grade", [0,1,2],
                          format_func=lambda x: ["Grade A","Grade B","Grade C"][x])
        with col2:
            day_of_week = st.selectbox("Day of Week", list(range(7)),
                          format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])

        st.markdown("<br/>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 2, 1])
        with btn_col:
            predict_btn = st.button("⚙️  Run Prediction →")

        if predict_btn:
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
                "Machine_Utilization":        machine_util
            }

            with st.spinner("🤖 Running ML prediction..."):
                time.sleep(0.5)
                try:
                    res = requests.post("http://localhost:8000/predict", json=payload).json()
                    st.session_state.prediction = res
                    st.session_state.history.append({
                        "output": res['predicted_parts_per_hour'],
                        "status": res['status']
                    })
                except:
                    st.error("❌ Backend not reachable. Run: python -m uvicorn main:app --reload")
                    return

        # Results
        if st.session_state.prediction:
            res = st.session_state.prediction
            predicted = res['predicted_parts_per_hour']
            status    = res['status']

            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("""<h3 style="color:white; font-size:18px; font-weight:700;
                          margin:16px 0;">📊 Prediction Results</h3>""",
                       unsafe_allow_html=True)

            r1, r2, r3 = st.columns(3)

            with r1:
                color = "#2d6a4f" if predicted >= 40 else "#e65100" if predicted < 20 else "#0077b6"
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{color},{color}99);
                            border-radius:16px; padding:32px; text-align:center;">
                  <div style="color:rgba(255,255,255,0.7); font-size:13px;
                               font-weight:600; text-transform:uppercase;
                               letter-spacing:1px; margin-bottom:8px;">
                    Predicted Output
                  </div>
                  <div style="font-size:52px; font-weight:800; color:white;
                               line-height:1; margin-bottom:6px;">
                    {predicted}
                  </div>
                  <div style="color:rgba(255,255,255,0.6); font-size:14px;">
                    parts / hour
                  </div>
                  <div style="margin-top:16px; background:rgba(0,0,0,0.2);
                               border-radius:8px; padding:8px; font-size:13px;
                               color:white; font-weight:600;">
                    {status}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with r2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=predicted,
                    title={'text': "Parts Per Hour", 'font': {'size': 13, 'color': 'white'}},
                    number={'font': {'color': 'white', 'size': 36}},
                    gauge={
                        'axis': {'range': [0, 70], 'tickcolor': 'white'},
                        'bar':  {'color': '#00b4d8'},
                        'bgcolor': 'rgba(0,0,0,0)',
                        'steps': [
                            {'range': [0,  20], 'color': 'rgba(230,81,0,0.3)'},
                            {'range': [20, 40], 'color': 'rgba(0,119,182,0.3)'},
                            {'range': [40, 70], 'color': 'rgba(45,106,79,0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': '#f77f00', 'width': 3},
                            'thickness': 0.75, 'value': 29.3
                        }
                    }
                ))
                fig.update_layout(
                    height=220,
                    margin=dict(t=30, b=10, l=20, r=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with r3:
                mean_val = 29.3
                diff     = round(predicted - mean_val, 1)
                pct      = round((predicted / 68.6) * 100, 1)
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);
                            border:1px solid rgba(255,255,255,0.1);
                            border-radius:16px; padding:24px; height:220px;">
                  <div style="color:rgba(255,255,255,0.5); font-size:12px;
                               font-weight:600; text-transform:uppercase;
                               letter-spacing:1px; margin-bottom:16px;">
                    Performance Analysis
                  </div>
                  <div style="margin-bottom:12px;">
                    <div style="color:rgba(255,255,255,0.5); font-size:12px;">vs Dataset Average</div>
                    <div style="color:{'#4caf50' if diff>=0 else '#f44336'};
                                font-size:20px; font-weight:700;">
                      {'▲' if diff>=0 else '▼'} {abs(diff)} parts/hr
                    </div>
                  </div>
                  <div style="margin-bottom:12px;">
                    <div style="color:rgba(255,255,255,0.5); font-size:12px;">Capacity Usage</div>
                    <div style="color:#00b4d8; font-size:20px; font-weight:700;">
                      {pct}%
                    </div>
                  </div>
                  <div style="background:rgba(255,255,255,0.08); border-radius:6px;
                               height:6px; overflow:hidden;">
                    <div style="background:#00b4d8; height:100%; width:{pct}%;
                                 border-radius:6px;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 5 — ANALYTICS
# ══════════════════════════════════════════════════════════
def analytics_page():
    navbar()
    st.markdown("""
    <div style="background:#0a1628; padding:32px 48px 24px;">
      <h2 style="color:white; font-weight:800; font-size:24px; margin:0 0 4px;">
        📈 Analytics & Insights
      </h2>
      <p style="color:rgba(255,255,255,0.4); font-size:14px; margin:0;">
        Prediction history and model performance
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='background:#0a1628; padding:0 48px 40px;'>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px; padding:60px; text-align:center; margin-top:20px;">
          <div style="font-size:48px; margin-bottom:16px;">📊</div>
          <div style="color:rgba(255,255,255,0.5); font-size:16px;">
            No predictions yet. Run a prediction first!
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Go to Predictor"):
            st.session_state.page = "predict"
            st.rerun()
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df.index += 1

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(hist_df, y='output', title='Prediction History',
                         template='plotly_dark',
                         labels={'output': 'Parts/Hr', 'index': 'Prediction #'})
            fig.update_traces(line_color='#00b4d8', line_width=2.5)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            status_counts = hist_df['status'].value_counts()
            fig2 = px.pie(values=status_counts.values,
                         names=status_counts.index,
                         title='Output Status Distribution',
                         template='plotly_dark',
                         color_discrete_map={
                             '🟢 High Output':   '#2d6a4f',
                             '🟡 Normal Output': '#0077b6',
                             '🔴 Low Output':    '#e65100'
                         })
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Prediction Log**")
        st.dataframe(hist_df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 6 — VOICE AI (Vapi)
# ══════════════════════════════════════════════════════════
def voice_page():
    navbar()
    st.markdown("""
    <div style="background:#0a1628; padding:32px 48px 24px;">
      <h2 style="color:white; font-weight:800; font-size:24px; margin:0 0 4px;">
        🎙️ Voice AI Assistant
      </h2>
      <p style="color:rgba(255,255,255,0.4); font-size:14px; margin:0;">
        Ask FlowPredict AI anything using your voice — powered by Vapi
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Replace YOUR_VAPI_PUBLIC_KEY below with your actual key from vapi.ai
    VAPI_KEY = "f83a3655-29a5-41ed-87f6-c9ffee3568e6"
    VAPI_ASSISTANT_ID = "e86858e1-c399-4cdb-84c2-c4735ea4b649"

    st.components.v1.html(f"""
    <div style="background:#0d2137; min-height:70vh; display:flex;
                flex-direction:column; align-items:center;
                justify-content:center; padding:40px; font-family:Inter,sans-serif;">

      <!-- Mic Button -->
      <div id="vapi-btn" onclick="toggleVapi()"
           style="width:100px; height:100px; border-radius:50%;
                  background:linear-gradient(135deg,#0077b6,#023e8a);
                  display:flex; align-items:center; justify-content:center;
                  cursor:pointer; font-size:40px;
                  box-shadow: 0 0 40px rgba(0,119,182,0.5);
                  transition: all 0.3s; margin-bottom:24px;">
        🎙️
      </div>

      <div id="vapi-status"
           style="color:#00b4d8; font-size:16px; font-weight:600;
                  margin-bottom:12px;">
        Click to start talking
      </div>

      <div id="vapi-transcript"
           style="background:rgba(255,255,255,0.05);
                  border:1px solid rgba(255,255,255,0.1);
                  border-radius:12px; padding:20px;
                  min-height:80px; width:100%; max-width:600px;
                  color:rgba(255,255,255,0.7); font-size:14px;
                  line-height:1.6; text-align:center;">
        Your conversation will appear here...
      </div>

      <div style="margin-top:24px; color:rgba(255,255,255,0.3); font-size:12px;
                  text-align:center; max-width:400px;">
        💡 Try asking: "What is the average parts per hour?" or
        "What parameters affect output the most?"
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/dist/vapi.js"></script>
    <script>
      const vapi = new Vapi("{VAPI_KEY}");
      let active = false;

      vapi.on('speech-start', () => {{
        document.getElementById('vapi-status').textContent = '🔴 Listening...';
        document.getElementById('vapi-btn').style.boxShadow = '0 0 60px rgba(230,57,70,0.7)';
        document.getElementById('vapi-btn').style.background = 'linear-gradient(135deg,#e63946,#c1121f)';
      }});

      vapi.on('speech-end', () => {{
        document.getElementById('vapi-status').textContent = '🤖 Processing...';
      }});

      vapi.on('message', (msg) => {{
        if (msg.type === 'transcript' && msg.role === 'assistant') {{
          document.getElementById('vapi-transcript').textContent = msg.transcript;
          document.getElementById('vapi-status').textContent = '✅ Response received';
        }}
      }});

      vapi.on('call-end', () => {{
        active = false;
        document.getElementById('vapi-status').textContent = 'Click to start talking';
        document.getElementById('vapi-btn').style.boxShadow = '0 0 40px rgba(0,119,182,0.5)';
        document.getElementById('vapi-btn').style.background = 'linear-gradient(135deg,#0077b6,#023e8a)';
        document.getElementById('vapi-btn').textContent = '🎙️';
      }});

      async function toggleVapi() {{
        if (!active) {{
          active = true;
          document.getElementById('vapi-btn').textContent = '⏹️';
          document.getElementById('vapi-status').textContent = '🔴 Connecting...';
          await vapi.start("{VAPI_ASSISTANT_ID}");
        }} else {{
          active = false;
          vapi.stop();
        }}
      }}
    </script>
    """, height=500)

    st.markdown("""
    <div style="background:#0a1628; padding:0 48px 20px;">
    <div style="background:rgba(0,119,182,0.1); border:1px solid rgba(0,119,182,0.25);
                border-radius:12px; padding:20px; margin-top:16px;">
      <h4 style="color:#00b4d8; margin:0 0 10px; font-size:14px;">
        🔧 Setup Vapi Voice AI in 3 Steps
      </h4>
      <ol style="color:rgba(255,255,255,0.6); font-size:13px; margin:0; padding-left:18px; line-height:2;">
        <li>Sign up free at <strong style="color:#00b4d8;">vapi.ai</strong></li>
        <li>Create an assistant → copy your Public Key + Assistant ID</li>
        <li>Replace <code style="background:rgba(255,255,255,0.1);padding:2px 6px;
            border-radius:4px;">YOUR_VAPI_PUBLIC_KEY</code> and
            <code style="background:rgba(255,255,255,0.1);padding:2px 6px;
            border-radius:4px;">YOUR_ASSISTANT_ID</code> in app.py</li>
      </ol>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  PAGE 7 — SETTINGS
# ══════════════════════════════════════════════════════════
def settings_page():
    navbar()
    st.markdown("""
    <div style="background:#0a1628; padding:32px 48px;">
      <h2 style="color:white; font-weight:800; font-size:24px; margin:0 0 24px;">
        ⚙️ Settings
      </h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='background:#0a1628; padding:0 48px 40px;'>", unsafe_allow_html=True)

    user = st.session_state.user_info
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
                border-radius:16px; padding:28px; margin-bottom:20px;">
      <h4 style="color:white; margin:0 0 16px;">👤 Account</h4>
      <p style="color:rgba(255,255,255,0.6); margin:0; font-size:14px; line-height:2;">
        <strong style="color:#00b4d8;">Email:</strong> {st.session_state.user_email}<br/>
        <strong style="color:#00b4d8;">Role:</strong>  {user.get('role','')}<br/>
        <strong style="color:#00b4d8;">Company:</strong> {user.get('company','')}
      </p>
    </div>
    """, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        if st.button("🚪  Sign Out"):
            st.session_state.logged_in  = False
            st.session_state.user_email = ""
            st.session_state.user_info  = {}
            st.session_state.page       = "landing"
            st.session_state.prediction = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════
page = st.session_state.page

if not st.session_state.logged_in:
    if page == "login":
        login_page()
    else:
        landing_page()
else:
    if page in ["landing", "login", "dashboard"]:
        dashboard_page()
    elif page == "predict":
        predict_page()
    elif page == "analytics":
        analytics_page()
    elif page == "voice":
        voice_page()
    elif page == "settings":
        settings_page()
    else:
        dashboard_page()