import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import time
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="FlowPredict AI", page_icon="⚙️",
                   layout="wide", initial_sidebar_state="collapsed")

USERS = {
    "admin@flowpredict.ai":    {"password": "admin123",  "role": "Admin",    "company": "FlowPredict Industries"},
    "manager@acmecorp.com":    {"password": "acme2024",  "role": "Manager",  "company": "ACME Manufacturing"},
    "operator@steelworks.com": {"password": "steel2024", "role": "Operator", "company": "SteelWorks Ltd"},
}

for key, val in {
    "logged_in": False, "user_email": "", "user_info": {},
    "page": "landing", "prediction": None, "history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── CONSTANTS ──────────────────────────────────────────────
BG     = "#080f1a"
BG2    = "#0d1526"
CARD   = "rgba(255,255,255,0.04)"
BORDER = "rgba(255,255,255,0.08)"
BORDER2= "rgba(255,255,255,0.14)"
TEXT   = "#e2e8f0"
TEXT2  = "rgba(255,255,255,0.55)"
TEXT3  = "rgba(255,255,255,0.32)"
ACCENT = "#00b4d8"
ACC2   = "#0077b6"
MAXW   = "1320px"  # max content width
PX     = "72px"    # horizontal padding

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, sans-serif !important;
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
#MainMenu, footer, header {{ visibility: hidden !important; }}
.block-container {{ padding: 36px 64px !important; max-width: 1400px !important; margin: 0 auto !important; overflow-x: hidden !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: #0a1628; }}
::-webkit-scrollbar-thumb {{ background: {ACC2}55; border-radius: 4px; }}

/* ── Text inputs ── */
.stTextInput input {{
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid {BORDER2} !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 13px 16px !important;
    caret-color: {ACCENT} !important;
}}
.stTextInput input::placeholder {{ color: {TEXT3} !important; }}
.stTextInput input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px rgba(0,180,216,0.2) !important;
}}
.stTextInput input:-webkit-autofill,
.stTextInput input:-webkit-autofill:focus {{
    -webkit-text-fill-color: #ffffff !important;
    -webkit-box-shadow: 0 0 0px 1000px #0d1a2e inset !important;
}}
.stTextInput label {{ color: rgba(255,255,255,0.75) !important; font-size: 13px !important; font-weight: 600 !important; }}

/* ── Selects ── */
.stSelectbox > div > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important; color: white !important; font-size: 13px !important;
}}
.stSelectbox label {{ color: {TEXT2} !important; font-size: 12px !important; font-weight: 600 !important; }}

/* ── Number input ── */
.stNumberInput input {{
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important; color: white !important; font-size: 13px !important;
}}
.stNumberInput label {{ color: {TEXT2} !important; font-size: 12px !important; font-weight: 600 !important; }}

/* ── Sliders ── */
.stSlider label {{ color: {TEXT2} !important; font-size: 12px !important; font-weight: 600 !important; }}
.stSlider [data-baseweb="slider"] {{ margin-top: 6px !important; }}
.stSlider [data-baseweb="slider"] > div > div {{ height: 5px !important; border-radius: 99px !important; }}
[data-baseweb="slider"] [data-testid="stThumbValue"] {{
    color: {ACCENT} !important; font-weight: 700 !important; font-size: 12px !important;
    background: rgba(0,180,216,0.12) !important;
    padding: 2px 8px !important; border-radius: 6px !important;
    border: 1px solid rgba(0,180,216,0.25) !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, {ACC2}, #023e8a) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: 11px 24px !important; width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(0,119,182,0.3) !important;
    letter-spacing: 0.2px !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,119,182,0.45) !important;
    background: linear-gradient(135deg, #0090d4, #0353a4) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: rgba(0,119,182,0.1) !important;
    border: 1px solid rgba(0,119,182,0.25) !important;
    border-radius: 16px !important; padding: 22px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
}}
[data-testid="metric-container"] label {{
    color: {TEXT3} !important; font-size: 11px !important;
    font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1px !important;
}}
[data-testid="metric-container"] [data-testid="metric-value"] {{
    color: {ACCENT} !important; font-size: 28px !important; font-weight: 800 !important;
}}

/* ── Misc ── */
.stDataFrame {{ border-radius: 14px !important; overflow: hidden !important; }}
.streamlit-expanderHeader {{
    background: {CARD} !important; border: 1px solid {BORDER} !important;
    border-radius: 10px !important; color: white !important; font-weight: 600 !important;
}}
.stSpinner > div {{ border-top-color: {ACCENT} !important; }}
div[data-testid="stVerticalBlock"] > div {{ background: transparent !important; }}

@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-up {{ animation: fadeUp 0.35s ease forwards; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def sp(h=8):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)

def section_title(text):
    st.markdown(
        f'<p style="color:{TEXT3};font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:1.6px;margin:0 0 14px;">{text}</p>',
        unsafe_allow_html=True)

def page_header(icon, title, subtitle):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{BG},{BG2});
    border-bottom:1px solid {BORDER};padding:28px 0 24px;">
      <div style="max-width:{MAXW};margin:0 auto;padding:0 {PX};
      display:flex;align-items:center;gap:14px;">
        <div style="width:44px;height:44px;border-radius:12px;flex-shrink:0;
        background:linear-gradient(135deg,{ACC2},{ACCENT});
        display:flex;align-items:center;justify-content:center;font-size:20px;
        box-shadow:0 4px 14px rgba(0,119,182,0.35);">{icon}</div>
        <div>
          <h2 style="color:white;font-size:21px;font-weight:800;margin:0;letter-spacing:-0.5px;">{title}</h2>
          <p style="color:{TEXT3};font-size:13px;margin:0;margin-top:2px;">{subtitle}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

def content_wrap():
    """Returns HTML to start a centered, padded content block."""
    return f'<div style="max-width:{MAXW};margin:0 auto;padding:36px {PX} 52px;">'

def divider():
    st.markdown(
        f'<div style="height:1px;background:linear-gradient(90deg,transparent,{BORDER2},transparent);'
        f'margin:18px 0;"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════
def landing_page():
    # NAV — full bleed, content centered inside
    st.markdown(f"""
    <div style="background:{BG};border-bottom:1px solid {BORDER};padding:0 {PX};height:60px;
    display:flex;justify-content:space-between;align-items:center;
    position:sticky;top:0;z-index:999;">
      <div style="max-width:{MAXW};margin:0 auto;width:100%;
      display:flex;justify-content:space-between;align-items:center;">
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:28px;height:28px;border-radius:7px;
          background:linear-gradient(135deg,{ACC2},{ACCENT});
          display:flex;align-items:center;justify-content:center;font-size:13px;">⚙️</div>
          <span style="color:{ACCENT};font-weight:800;font-size:16px;letter-spacing:-0.4px;">FlowPredict AI</span>
        </div>
        <div style="display:flex;gap:4px;">
          <span style="color:{TEXT3};font-size:13px;font-weight:500;padding:6px 14px;cursor:pointer;border-radius:8px;"
          onmouseover="this.style.color='{ACCENT}';this.style.background='rgba(255,255,255,0.05)'"
          onmouseout="this.style.color='{TEXT3}';this.style.background='transparent'">Features</span>
          <span style="color:{TEXT3};font-size:13px;font-weight:500;padding:6px 14px;cursor:pointer;border-radius:8px;"
          onmouseover="this.style.color='{ACCENT}';this.style.background='rgba(255,255,255,0.05)'"
          onmouseout="this.style.color='{TEXT3}';this.style.background='transparent'">How It Works</span>
          <span style="color:{TEXT3};font-size:13px;font-weight:500;padding:6px 14px;cursor:pointer;border-radius:8px;"
          onmouseover="this.style.color='{ACCENT}';this.style.background='rgba(255,255,255,0.05)'"
          onmouseout="this.style.color='{TEXT3}';this.style.background='transparent'">About</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # HERO
    st.markdown(f"""
    <div style="background:radial-gradient(ellipse at 50% 0%,rgba(0,119,182,0.12) 0%,transparent 68%);">
      <div style="max-width:{MAXW};margin:0 auto;padding:84px {PX} 52px;text-align:center;">
        <div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(0,180,216,0.08);border:1px solid rgba(0,180,216,0.2);
        border-radius:100px;padding:6px 18px;margin-bottom:34px;">
          <div style="width:6px;height:6px;border-radius:50%;background:{ACCENT};"></div>
          <span style="font-size:12px;color:{ACCENT};font-weight:600;letter-spacing:0.5px;">
            AI-Powered Manufacturing Intelligence
          </span>
        </div>
        <h1 style="font-size:60px;font-weight:900;color:white;line-height:1.06;
        margin:0 0 22px;letter-spacing:-2.5px;max-width:760px;margin-left:auto;margin-right:auto;">
          Predict. Optimize.<br/>
          <span style="background:linear-gradient(90deg,{ACC2},{ACCENT},#48cae4);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Manufacture Smarter.
          </span>
        </h1>
        <p style="font-size:17px;color:{TEXT2};max-width:540px;margin:0 auto 52px;line-height:1.8;">
          A production-grade ML platform forecasting manufacturing output in real-time
          using a Stacking Ensemble achieving <strong style="color:white;">R² = 0.9363</strong>.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # STATS — centered container
    st.components.v1.html(f"""
    <div style="background:{BG};padding:0 {PX} 52px;">
      <div style="max-width:{MAXW};margin:0 auto;">
        <div style="display:flex;background:rgba(255,255,255,0.03);
        border:1px solid rgba(255,255,255,0.08);border-radius:20px;overflow:hidden;
        box-shadow:0 4px 24px rgba(0,0,0,0.2);">

          <div class="s" style="flex:1;padding:36px 20px;text-align:center;border-right:1px solid rgba(255,255,255,0.07);">
            <div id="s1" data-t="94" data-s="%" style="font-size:46px;font-weight:900;color:#00b4d8;line-height:1;letter-spacing:-2px;">0%</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.38);margin-top:8px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;">Model Accuracy</div>
            <div style="font-size:10px;color:rgba(0,180,216,0.6);margin-top:4px;">R² = 0.9363 · CV = 0.9343</div>
          </div>

          <div class="s" style="flex:1;padding:36px 20px;text-align:center;border-right:1px solid rgba(255,255,255,0.07);">
            <div id="s2" data-t="1000" data-s="+" style="font-size:46px;font-weight:900;color:#00b4d8;line-height:1;letter-spacing:-2px;">0+</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.38);margin-top:8px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;">Training Samples</div>
            <div style="font-size:10px;color:rgba(0,180,216,0.6);margin-top:4px;">800 train · 200 test (80/20)</div>
          </div>

          <div class="s" style="flex:1;padding:36px 20px;text-align:center;border-right:1px solid rgba(255,255,255,0.07);">
            <div id="s3" data-t="42" data-s="" style="font-size:46px;font-weight:900;color:#00b4d8;line-height:1;letter-spacing:-2px;">0</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.38);margin-top:8px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;">Total Features</div>
            <div style="font-size:10px;color:rgba(0,180,216,0.6);margin-top:4px;">17 raw + 25 engineered</div>
          </div>

          <div class="s" style="flex:1;padding:36px 20px;text-align:center;">
            <div id="s4" data-t="6" data-s="" style="font-size:46px;font-weight:900;color:#00b4d8;line-height:1;letter-spacing:-2px;">0</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.38);margin-top:8px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;">ML Models Stacked</div>
            <div style="font-size:10px;color:rgba(0,180,216,0.6);margin-top:4px;">XGB · LGBM · CatBoost · GBM · ET · RF</div>
          </div>

        </div>
      </div>
    </div>
    <script>
    function anim(el,t,s){{let st=0,dur=1800,sT=null;function step(ts){{if(!sT)sT=ts;let p=Math.min((ts-sT)/dur,1),e=1-Math.pow(1-p,4);el.textContent=Math.floor(e*t).toLocaleString()+s;if(p<1)requestAnimationFrame(step);}}requestAnimationFrame(step);}}
    let d=false;const io=new IntersectionObserver(en=>{{if(en[0].isIntersecting&&!d){{d=true;['s1','s2','s3','s4'].forEach(id=>{{const el=document.getElementById(id);if(el)anim(el,parseInt(el.dataset.t),el.dataset.s);}});}}}},{{threshold:0.3}});
    const f=document.querySelector('.s');if(f)io.observe(f);
    </script>""", height=152)

    # FEATURES
    st.markdown(f"""
    <div style="max-width:{MAXW};margin:0 auto;padding:0 {PX};">
      <hr style="border:none;border-top:1px solid {BORDER};margin:0 0 52px;"/>
      <div style="text-align:center;margin-bottom:36px;">
        <p style="font-size:11px;color:{TEXT3};font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">Core Features</p>
        <h2 style="font-size:30px;font-weight:800;color:white;margin:0 0 10px;letter-spacing:-1px;">Everything you need to optimize output</h2>
        <p style="font-size:15px;color:{TEXT2};max-width:480px;margin:0 auto;">End-to-end ML platform — from raw data to deployed predictions</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns(4)
    feats = [
        ("🤖","Stacking Ensemble","#0077b6","6 ML models stacked with Optuna tuning. Best: CatBoost R² = 0.9363. Production-grade manufacturing regression."),
        ("⚡","Sub-100ms API","#7c3aed","FastAPI backend computes 25 engineered features on-the-fly and returns predictions in under 100ms."),
        ("🎙️","Voice AI","#0891b2","Vapi-powered voice assistant. Ask about model accuracy, feature importance, or get usage guidance hands-free."),
        ("📊","Analytics","#059669","Full prediction history, trend charts, status distribution pie, and performance vs dataset average per session."),
    ]
    for col,(icon,title,color,desc) in zip([f1,f2,f3,f4],feats):
        with col:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:18px;
            padding:26px 20px;min-height:218px;transition:all 0.25s ease;cursor:default;"
            onmouseover="this.style.borderColor='{color}55';this.style.transform='translateY(-4px)';this.style.boxShadow='0 14px 36px rgba(0,0,0,0.18)'"
            onmouseout="this.style.borderColor='{BORDER}';this.style.transform='translateY(0)';this.style.boxShadow='none'">
              <div style="width:46px;height:46px;border-radius:12px;margin-bottom:14px;
              background:linear-gradient(135deg,{color}25,{color}0d);
              border:1px solid {color}30;display:flex;align-items:center;justify-content:center;font-size:22px;">{icon}</div>
              <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">{title}</div>
              <div style="font-size:12px;color:{TEXT2};line-height:1.7;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    sp(60)

    # HOW IT WORKS
    st.markdown(f"""
    <div style="max-width:{MAXW};margin:0 auto;padding:0 {PX};text-align:center;margin-bottom:36px;">
      <p style="font-size:11px;color:{TEXT3};font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">How It Works</p>
      <h2 style="font-size:30px;font-weight:800;color:white;margin:0;letter-spacing:-1px;">From inputs to predictions in 4 steps</h2>
    </div>""", unsafe_allow_html=True)

    st.components.v1.html(f"""
    <div style="background:rgba(255,255,255,0.015);
    border-top:1px solid rgba(255,255,255,0.06);border-bottom:1px solid rgba(255,255,255,0.06);
    padding:48px 0;font-family:Inter,sans-serif;">
      <div style="max-width:{MAXW};margin:0 auto;padding:0 {PX};display:flex;align-items:flex-start;">

        <div style="flex:1;text-align:center;padding:0 16px;">
          <div style="width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#0077b6,#023e8a);
          display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:800;
          color:white;margin:0 auto 16px;box-shadow:0 0 0 8px rgba(0,119,182,0.12);">1</div>
          <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">Enter 17 Parameters</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.75;">Fill temperature, pressure, cycle time, machine age, operator experience and more via sliders</div>
        </div>

        <div style="padding-top:24px;color:rgba(255,255,255,0.18);font-size:22px;flex-shrink:0;">›</div>

        <div style="flex:1;text-align:center;padding:0 16px;">
          <div style="width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#5e35b1,#7c3aed);
          display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:800;
          color:white;margin:0 auto 16px;box-shadow:0 0 0 8px rgba(124,58,237,0.12);">2</div>
          <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">Feature Engineering</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.75;">Backend auto-computes 25 features: log transforms, ratios, interaction terms, and polynomial features</div>
        </div>

        <div style="padding-top:24px;color:rgba(255,255,255,0.18);font-size:22px;flex-shrink:0;">›</div>

        <div style="flex:1;text-align:center;padding:0 16px;">
          <div style="width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#0077b6,#00b4d8);
          display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:800;
          color:white;margin:0 auto 16px;box-shadow:0 0 0 8px rgba(0,180,216,0.12);">3</div>
          <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">Stacking Ensemble</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.75;">All 42 features passed through 6 base models, then Ridge meta-learner combines their predictions</div>
        </div>

        <div style="padding-top:24px;color:rgba(255,255,255,0.18);font-size:22px;flex-shrink:0;">›</div>

        <div style="flex:1;text-align:center;padding:0 16px;">
          <div style="width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#059669,#10b981);
          display:flex;align-items:center;justify-content:center;font-size:21px;font-weight:800;
          color:white;margin:0 auto 16px;box-shadow:0 0 0 8px rgba(5,150,105,0.12);">4</div>
          <div style="font-size:14px;font-weight:700;color:white;margin-bottom:8px;">Instant Results</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.75;">Predicted Parts/Hr, gauge chart, performance vs average, and High/Normal/Low status in &lt;100ms</div>
        </div>

      </div>
    </div>""", height=222)

    sp(58)

    # ABOUT
    st.markdown(f"""
    <div style="max-width:{MAXW};margin:0 auto;padding:0 {PX};text-align:center;margin-bottom:32px;">
      <p style="font-size:11px;color:{TEXT3};font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">About The Project</p>
      <h2 style="font-size:30px;font-weight:800;color:white;margin:0;letter-spacing:-1px;">Built as a Capstone ML Project</h2>
    </div>""", unsafe_allow_html=True)

    a1,a2,a3,a4 = st.columns(4)
    abouts = [
        ("🎓","Project Details",[("Title","Manufacturing Output Prediction"),("Category","Supervised — Regression"),("Dataset","1000 manufacturing samples"),("Target","Parts Per Hour"),("Split","80/20 Train-Test"),("Org","Tns India Foundation · Group 2")]),
        ("🤖","Model Performance",[("Best Model","CatBoost Regressor"),("Test R²","0.9363 (93.63%)"),("CV R²","0.9343 ± 0.011 (5-Fold)"),("RMSE","2.8827 parts/hr"),("MAE","2.2574 parts/hr"),("Features","42 (17 raw + 25 eng.)")]),
        ("🛠️","Tech Stack",[("ML","XGBoost · LightGBM · CatBoost"),("Tuning","Optuna Bayesian Opt."),("Backend","FastAPI + Uvicorn"),("Frontend","Streamlit + Plotly"),("Voice","Vapi AI Voice Agent")]),
        ("👥","Team FlowPredict AI",[("Lead","Harshavardhan G"),("Member","Channakeshava L"),("Member","Madhushree S"),("Member","Kranti Shantveer"),("Member","Kondreddy Akhila"),("Member","P Raghu Ram Reddy")]),
    ]
    for col,(icon,title,items) in zip([a1,a2,a3,a4],abouts):
        with col:
            rows = "".join([
                f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                f'<span style="color:{TEXT3};font-size:11px;min-width:55px;flex-shrink:0;">{k}</span>'
                f'<span style="color:rgba(255,255,255,0.78);font-size:11px;font-weight:500;text-align:right;">{v}</span></div>'
                for k,v in items
            ])
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:18px;padding:22px 18px;
            transition:transform 0.2s,box-shadow 0.2s;"
            onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 12px 32px rgba(0,0,0,0.15)'"
            onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
              <div style="font-size:26px;margin-bottom:10px;">{icon}</div>
              <div style="font-size:13px;font-weight:700;color:white;margin-bottom:12px;">{title}</div>
              {rows}
            </div>""", unsafe_allow_html=True)

    sp(48)
    _,c1,_g,c2,_ = st.columns([1.5,0.85,0.1,0.85,1.5])
    with c1:
        if st.button("🚀  Get Started — Login", key="cta_login"):
            st.session_state.page = "login"; st.rerun()
    with c2:
        if st.button("🔮  Try a Prediction", key="cta_pred"):
            st.session_state.page = "login"; st.rerun()

    sp(24)
    st.markdown(f'<p style="text-align:center;color:rgba(255,255,255,0.12);font-size:12px;padding-bottom:24px;">FlowPredict AI · Capstone Regression · CatBoost + Stacking Ensemble · R² = 0.9363</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════
def login_page():
    sp(52)
    _,center,_ = st.columns([1,1.0,1])
    with center:
        st.markdown(f"""
        <div class="fade-up" style="text-align:center;margin-bottom:28px;">
          <div style="width:52px;height:52px;border-radius:14px;margin:0 auto 14px;
          background:linear-gradient(135deg,{ACC2},{ACCENT});
          display:flex;align-items:center;justify-content:center;font-size:24px;
          box-shadow:0 8px 24px rgba(0,119,182,0.35);">⚙️</div>
          <h2 style="color:white;font-size:24px;font-weight:800;margin:0 0 6px;letter-spacing:-0.6px;">FlowPredict AI</h2>
          <p style="color:{TEXT2};font-size:14px;margin:0;">Sign in to your company account</p>
        </div>
        <div style="background:{CARD};border:1px solid {BORDER2};border-radius:20px;padding:32px 32px 6px;
        box-shadow:0 20px 60px rgba(0,0,0,0.3);">
        """, unsafe_allow_html=True)

        email    = st.text_input("📧  Company Email", placeholder="admin@flowpredict.ai", key="login_email")
        sp(4)
        password = st.text_input("🔒  Password", type="password", placeholder="Enter your password", key="login_pass")
        sp(14)
        if st.button("Sign In  →", key="signin_btn"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.session_state.user_info  = USERS[email]
                st.session_state.page       = "dashboard"
                st.rerun()
            else:
                st.error("❌  Invalid email or password.")
        st.markdown("</div>", unsafe_allow_html=True)
        sp(16)

        st.markdown(f"""
        <div style="background:rgba(0,119,182,0.07);border:1px solid rgba(0,119,182,0.18);
        border-radius:14px;padding:16px 20px;">
          <p style="color:{ACCENT};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px;">Demo Accounts</p>
          <p style="color:{TEXT2};font-size:12px;margin:0;line-height:2.1;font-family:monospace;">
            admin@flowpredict.ai / admin123<br/>
            manager@acmecorp.com / acme2024<br/>
            operator@steelworks.com / steel2024
          </p>
        </div>""", unsafe_allow_html=True)

        sp(12)
        if st.button("←  Back to Home", key="back_home"):
            st.session_state.page = "landing"; st.rerun()


# ══════════════════════════════════════════════════════════
#  NAVBAR (authenticated)
# ══════════════════════════════════════════════════════════
def navbar():
    user = st.session_state.user_info
    
    # Proper header using st.columns
    c1, c2, c3 = st.columns([1.5, 4.5, 1.5], vertical_alignment="center")
    
    with c1:
        st.markdown(f"### <span style='color:{ACCENT};'>⚙️</span> FlowPredict AI", unsafe_allow_html=True)
        
    with c2:
        pages     = ["🏠 Dashboard","🔮 Predict","📈 Analytics","🎙️ Voice AI"]
        page_keys = ["dashboard","predict","analytics","voice"]
        cols      = st.columns(4)
        
        for i, (col, label, key) in enumerate(zip(cols, pages, page_keys)):
            is_active = st.session_state.page == key
            with col:
                st.markdown(f"""<style>
                div[data-testid="column"]:nth-child({i+1}) .stButton > button {{
                    background:{"linear-gradient(135deg,rgba(0,119,182,0.2),rgba(0,180,216,0.1))" if is_active else "transparent"} !important;
                    border:{"1px solid "+ACCENT if is_active else "1px solid transparent"} !important;
                    color:{"white" if is_active else TEXT3} !important;
                    padding:8px 12px !important;
                    border-radius:20px !important;
                    font-size:13px !important;
                    font-weight:600 !important;
                }}
                div[data-testid="column"]:nth-child({i+1}) .stButton > button:hover {{
                    background:rgba(255,255,255,0.05) !important;
                }}
                </style>""", unsafe_allow_html=True)
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state.page = key
                    st.rerun()
                    
    with c3:
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"""<style>
            div[data-testid="column"]:nth-child(1) .stButton > button[key="nav_admin"] {{
                background:transparent !important; border:1px solid rgba(255,255,255,0.15) !important;
                border-radius:20px !important; color:{TEXT2} !important; font-size:13px !important; font-weight:600 !important;
            }}
            </style>""", unsafe_allow_html=True)
            if st.button("👤 Admin", key="nav_admin", use_container_width=True):
                st.session_state.page = "settings"
                st.rerun()
        with tc2:
            st.markdown(f"""<style>
            div[data-testid="column"]:nth-child(2) .stButton > button[key="nav_theme"] {{
                background:transparent !important; border:1px solid rgba(255,255,255,0.15) !important;
                border-radius:20px !important; color:{TEXT2} !important; font-size:13px !important; font-weight:600 !important;
            }}
            </style>""", unsafe_allow_html=True)
            if st.button("🌞 Mode", key="nav_theme", use_container_width=True):
                pass # theme toggle logic can be added later

    st.markdown("<hr style='margin-top: 12px; margin-bottom: 32px; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════
def dashboard_page():
    navbar()
    user = st.session_state.user_info
    page_header("🏠", f"Good day, {user.get('role','User')} 👋",
                "Manufacturing Intelligence Dashboard — FlowPredict AI")

    st.markdown(content_wrap(), unsafe_allow_html=True)

    preds   = len(st.session_state.history)
    avg_out = round(sum(h['output'] for h in st.session_state.history)/preds,1) if preds else 0.0

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("Model R² Score",   "93.63%")
    with k2: st.metric("RMSE",             "2.88 parts/hr")
    with k3: st.metric("Predictions Made", preds)
    with k4: st.metric("Avg Output",       f"{avg_out} parts/hr")

    sp(32)
    col_l, col_r = st.columns([1, 1.7], gap="large")

    with col_l:
        section_title("Quick Actions")
        sp(4)
        for icon,label,pg in [
            ("🔮","New Prediction","predict"),
            ("🎙️","Ask Voice AI","voice"),
            ("📈","View Analytics","analytics"),
        ]:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:14px;
            padding:14px 18px;margin-bottom:10px;display:flex;align-items:center;gap:14px;
            transition:all 0.2s ease;cursor:pointer;"
            onmouseover="this.style.borderColor='rgba(0,119,182,0.4)';this.style.transform='translateX(4px)';this.style.background='rgba(0,119,182,0.07)'"
            onmouseout="this.style.borderColor='{BORDER}';this.style.transform='translateX(0)';this.style.background='{CARD}'">
              <div style="width:38px;height:38px;border-radius:10px;flex-shrink:0;
              background:rgba(0,119,182,0.18);border:1px solid rgba(0,119,182,0.3);
              display:flex;align-items:center;justify-content:center;font-size:17px;">{icon}</div>
              <div style="flex:1;color:white;font-size:13px;font-weight:600;">{label}</div>
              <div style="color:{TEXT3};font-size:18px;">›</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Go to {label}", key=f"qa_{pg}"):
                st.session_state.page = pg; st.rerun()
            st.markdown(f"<style>button[title='Go to {label}']{{display:none!important;}}</style>", unsafe_allow_html=True)

    with col_r:
        section_title("Model Information")
        rows = [
            ("Algorithm",    "CatBoost Regressor (Best) + Stacking Ensemble"),
            ("Base Models",  "XGBoost · LightGBM · CatBoost · GBM · ET · RF"),
            ("Meta Learner", "Ridge Regression (Optuna optimized)"),
            ("Samples",      "1,000 rows · 800 train / 200 test"),
            ("Features",     "42 total — 17 raw + 25 engineered"),
            ("Validation",   "5-Fold KFold · CV R² = 0.9343 ± 0.011"),
            ("Best R²",      "0.9363 (CatBoost) · RMSE = 2.8827 parts/hr"),
            ("Target",       "Parts Per Hour · range: 5.0 – 68.6"),
        ]
        html = f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;overflow:hidden;">'
        for i,(k,v) in enumerate(rows):
            bg = "rgba(255,255,255,0.025)" if i%2==0 else "transparent"
            html += (f'<div style="display:flex;justify-content:space-between;align-items:center;'
                     f'padding:11px 20px;background:{bg};border-bottom:1px solid rgba(255,255,255,0.04);">'
                     f'<span style="color:{TEXT3};font-size:12px;min-width:120px;">{k}</span>'
                     f'<span style="color:{ACCENT};font-size:12px;font-weight:600;text-align:right;">{v}</span></div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    sp(32)
    section_title("All Models Comparison (R² Score)")

    model_data = pd.DataFrame({
        "Model": ["Random Forest","Linear Reg","Ridge Reg","LightGBM","XGBoost","Gradient Boost","CatBoost"],
        "R2":    [0.8638, 0.9093, 0.9118, 0.9134, 0.9146, 0.9204, 0.9363],
        "Color": ["#1a3a5c","#1e4570","#1e4570","#1a5080","#1a5e8a","#12689e","#00b4d8"],
    }).sort_values("R2")

    fig = go.Figure()
    for _,row in model_data.iterrows():
        fig.add_trace(go.Bar(
            x=[row["R2"]], y=[row["Model"]], orientation='h',
            marker=dict(color=row["Color"], line=dict(color='rgba(0,0,0,0)',width=0)),
            text=f"  {row['R2']:.4f}", textposition='outside',
            textfont=dict(color='rgba(255,255,255,0.8)',size=11),
            showlegend=False,
            hovertemplate=f"<b>{row['Model']}</b><br>R² = {row['R2']:.4f}<extra></extra>"
        ))
    fig.add_shape(type='line', x0=0.9363, x1=0.9363, y0=-0.5, y1=6.5,
                  line=dict(color="rgba(0,180,216,0.3)", width=1.5, dash='dot'))
    fig.add_annotation(x=0.9363, y=6.85, text="Best: 0.9363",
                       font=dict(color=ACCENT, size=11), showarrow=False)
    fig.update_layout(
        height=300, barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=90,t=20,b=10),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0.82,0.985]),
        yaxis=dict(tickfont=dict(color=TEXT2, size=12), ticksuffix="  "),
        font=dict(color='white'), bargap=0.3,
    )
    st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:20px 24px;">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close content_wrap


# ══════════════════════════════════════════════════════════
#  PREDICT PAGE
# ══════════════════════════════════════════════════════════
def predict_page():
    navbar()
    page_header("🔮", "Manufacturing Output Predictor",
                "Enter 17 machine parameters — 42-feature model predicts Parts Per Hour")

    st.markdown(content_wrap(), unsafe_allow_html=True)

    section_title("🌡️  Temperature & Pressure Parameters")
    c1,c2,c3,c4 = st.columns(4)
    with c1: inj_temp  = st.slider("Injection Temp (°C)",       180.0, 300.0, 215.0, 0.5)
    with c2: inj_pres  = st.slider("Injection Pressure (bar)",   80.0, 150.0, 116.0, 0.5)
    with c3: amb_temp  = st.slider("Ambient Temp (°C)",          18.0,  28.0,  23.0, 0.5)
    with c4: temp_pres = st.slider("Temp / Pressure Ratio",       1.2,   2.9,   1.9, 0.01)

    sp(14); divider(); sp(14)

    section_title("⏱️  Cycle & Time Parameters")
    c1,c2,c3,c4 = st.columns(4)
    with c1: cycle_time   = st.slider("Cycle Time (sec)",        16.0,  60.0, 35.0, 0.5)
    with c2: cooling_time = st.slider("Cooling Time (sec)",       8.0,  20.0, 12.0, 0.5)
    with c3: total_cycle  = st.slider("Total Cycle Time (sec)",  24.0,  65.0, 47.0, 0.5)
    with c4: maint_hours  = st.number_input("Maintenance Hours",  26,   500,   50)

    sp(14); divider(); sp(14)

    section_title("🏭  Machine & Operator Parameters")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        machine_age  = st.slider("Machine Age (yrs)",     1.0,  15.0,  8.0, 0.5)
        mat_visc     = st.slider("Material Viscosity",  100.0,1000.0,250.0, 5.0)
    with c2:
        op_exp       = st.slider("Operator Experience",   1.0, 120.0, 30.0, 1.0)
        eff_score    = st.slider("Efficiency Score (0–1)", 0.0,  0.84, 0.19, 0.01)
    with c3:
        machine_util = st.slider("Utilization (0–1)",    0.0,  0.76, 0.36, 0.01)
    with c4:
        shift        = st.selectbox("Shift", [0,1,2], format_func=lambda x: ["Morning","Afternoon","Night"][x])
        machine_type = st.selectbox("Machine Type", [0,1,2,3], format_func=lambda x: f"Type {x+1}")

    c1,c2,_,_ = st.columns(4)
    with c1: mat_grade   = st.selectbox("Material Grade", [0,1,2], format_func=lambda x: ["Grade A","Grade B","Grade C"][x])
    with c2: day_of_week = st.selectbox("Day of Week", list(range(7)), format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])

    sp(28)
    _,bc,_ = st.columns([1.6,1,1.6])
    with bc:
        run = st.button("⚙️  Run Prediction  →", key="run_pred")

    if run:
        payload = {
            "Injection_Temperature": inj_temp, "Injection_Pressure": inj_pres,
            "Cycle_Time": cycle_time, "Cooling_Time": cooling_time,
            "Material_Viscosity": mat_visc, "Ambient_Temperature": amb_temp,
            "Machine_Age": machine_age, "Operator_Experience": op_exp,
            "Maintenance_Hours": float(maint_hours), "Shift": shift,
            "Machine_Type": machine_type, "Material_Grade": mat_grade,
            "Day_of_Week": day_of_week, "Temperature_Pressure_Ratio": temp_pres,
            "Total_Cycle_Time": total_cycle, "Efficiency_Score": eff_score,
            "Machine_Utilization": machine_util,
        }
        with st.spinner("Running prediction..."):
            time.sleep(0.35)
            try:
                res = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=5).json()
                st.session_state.prediction = res
                st.session_state.history.append({"output": res["predicted_parts_per_hour"], "status": res["status"]})
            except requests.exceptions.ConnectionError:
                st.error("❌  Backend not reachable — run:\n\n`cd backend && python -m uvicorn main:app --reload --port 8000`")
            except Exception as e:
                st.error(f"❌  {e}")

    if st.session_state.prediction:
        res       = st.session_state.prediction
        predicted = res["predicted_parts_per_hour"]
        status    = res["status"]
        diff      = round(predicted - 29.3, 1)
        pct       = round((predicted / 68.6) * 100, 1)
        arrow     = "▲" if diff >= 0 else "▼"
        aclr      = "#22c55e" if diff >= 0 else "#ef4444"
        if predicted >= 40:   out_clr = "#16a34a"
        elif predicted < 20:  out_clr = "#ea580c"
        else:                 out_clr = "#0077b6"

        sp(28); divider(); sp(18)
        section_title("📊  Prediction Results")

        r1,r2,r3 = st.columns([1,1.25,1], gap="large")

        with r1:
            st.markdown(f"""
            <div class="fade-up" style="background:linear-gradient(135deg,{out_clr}cc,{out_clr}88);
            border:1.5px solid {out_clr};border-radius:20px;padding:32px 24px;text-align:center;
            box-shadow:0 8px 32px rgba(0,0,0,0.15);">
              <div style="color:rgba(255,255,255,0.6);font-size:11px;font-weight:700;
              text-transform:uppercase;letter-spacing:1.8px;margin-bottom:12px;">Predicted Output</div>
              <div style="font-size:58px;font-weight:900;color:white;line-height:1;
              letter-spacing:-2px;margin-bottom:8px;">{predicted}</div>
              <div style="color:rgba(255,255,255,0.55);font-size:14px;margin-bottom:22px;">parts / hour</div>
              <div style="background:rgba(0,0,0,0.28);border-radius:10px;padding:10px;
              font-size:13px;color:white;font-weight:700;">{status}</div>
            </div>""", unsafe_allow_html=True)

        with r2:
            gauge_color = "#22c55e" if predicted >= 40 else ("#f97316" if predicted < 20 else ACCENT)
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=predicted,
                title={"text":"Parts Per Hour","font":{"size":13,"color":TEXT2}},
                number={"font":{"color":"white","size":40}},
                gauge={
                    "axis":{"range":[0,70],"tickcolor":TEXT3,"tickfont":{"color":TEXT3,"size":10},"nticks":8},
                    "bar":{"color":gauge_color,"thickness":0.3},
                    "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                    "steps":[{"range":[0,20],"color":"rgba(239,68,68,0.12)"},{"range":[20,40],"color":"rgba(59,130,246,0.12)"},{"range":[40,70],"color":"rgba(34,197,94,0.12)"}],
                    "threshold":{"line":{"color":"#f97316","width":2},"thickness":0.8,"value":29.3}
                }
            ))
            fig.update_layout(height=240, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(t=24,b=0,l=20,r=20), font={"color":"white"})
            st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:18px;padding:8px;">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        with r3:
            st.markdown(f"""
            <div class="fade-up" style="background:{CARD};border:1px solid {BORDER};
            border-radius:20px;padding:28px;height:256px;">
              <div style="color:{TEXT3};font-size:11px;font-weight:700;
              text-transform:uppercase;letter-spacing:1.4px;margin-bottom:22px;">Performance</div>
              <div style="margin-bottom:20px;">
                <div style="color:{TEXT3};font-size:11px;margin-bottom:5px;">vs Dataset Average (29.3)</div>
                <div style="color:{aclr};font-size:26px;font-weight:800;letter-spacing:-1px;">
                  {arrow} {abs(diff)} <span style="font-size:14px;font-weight:500;">parts/hr</span>
                </div>
              </div>
              <div style="margin-bottom:14px;">
                <div style="color:{TEXT3};font-size:11px;margin-bottom:5px;">Capacity Usage</div>
                <div style="color:{ACCENT};font-size:26px;font-weight:800;letter-spacing:-1px;">
                  {pct}<span style="font-size:14px;font-weight:500;">%</span>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:6px;overflow:hidden;">
                <div style="background:linear-gradient(90deg,{ACC2},{ACCENT});
                height:100%;width:{min(pct,100)}%;border-radius:8px;box-shadow:0 0 8px {ACCENT}55;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:5px;">
                <span style="color:{TEXT3};font-size:10px;">0</span>
                <span style="color:{TEXT3};font-size:10px;">68.6 max</span>
              </div>
            </div>""", unsafe_allow_html=True)

        sp(22)
        with st.expander("📋  View Input Summary"):
            st.dataframe(pd.DataFrame([{
                "Inj.Temp":inj_temp,"Inj.Pres":inj_pres,"Cycle":cycle_time,
                "Cooling":cooling_time,"Amb.Temp":amb_temp,"Viscosity":mat_visc,
                "Mach.Age":machine_age,"Op.Exp":op_exp,"Maint.Hrs":maint_hours,
                "Efficiency":eff_score,"Utilization":machine_util,
                "Shift":shift,"M.Type":machine_type,"M.Grade":mat_grade,"Day":day_of_week,
            }]), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ANALYTICS PAGE
# ══════════════════════════════════════════════════════════
def analytics_page():
    navbar()
    page_header("📈","Analytics & Insights","Session prediction history, trends, and performance metrics")
    st.markdown(content_wrap(), unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(f"""
        <div style="background:{CARD};border:1px solid {BORDER};border-radius:20px;
        padding:80px;text-align:center;">
          <div style="font-size:48px;margin-bottom:18px;">📊</div>
          <div style="color:rgba(255,255,255,0.5);font-size:18px;font-weight:700;margin-bottom:8px;">No predictions yet</div>
          <div style="color:{TEXT3};font-size:14px;">Head to the Predict page and run your first prediction</div>
        </div>""", unsafe_allow_html=True)
        sp(16)
        _,c,_ = st.columns([2,1,2])
        with c:
            if st.button("→  Go to Predictor"):
                st.session_state.page = "predict"; st.rerun()
    else:
        hist_df = pd.DataFrame(st.session_state.history)
        hist_df.index += 1

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Total Predictions", len(hist_df))
        with m2: st.metric("Average Output",    f"{hist_df['output'].mean():.1f} parts/hr")
        with m3: st.metric("Highest Output",    f"{hist_df['output'].max():.1f} parts/hr")
        with m4: st.metric("Lowest Output",     f"{hist_df['output'].min():.1f} parts/hr")

        sp(28)
        c1,c2 = st.columns(2, gap="large")
        with c1:
            section_title("Prediction History Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist_df.index, y=hist_df["output"], mode="lines+markers",
                line=dict(color=ACCENT, width=2.5, shape='spline'),
                marker=dict(color=ACCENT, size=8, line=dict(color=BG, width=2)),
                fill="tozeroy", fillcolor="rgba(0,180,216,0.07)",
                hovertemplate="Prediction %{x}: <b>%{y:.2f}</b> parts/hr<extra></extra>"
            ))
            fig.add_hline(y=29.3, line_dash="dot", line_color="rgba(251,146,60,0.5)",
                         annotation_text="Mean 29.3", annotation_font=dict(color="rgba(251,146,60,0.8)",size=11))
            fig.update_layout(height=275, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=0,r=0,t=8,b=0), showlegend=False,
                              xaxis=dict(title="Prediction #", gridcolor=BORDER, tickfont=dict(color=TEXT3,size=11)),
                              yaxis=dict(title="Parts/Hr", gridcolor=BORDER, tickfont=dict(color=TEXT3,size=11)))
            st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:20px;">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            section_title("Output Status Distribution")
            counts = hist_df["status"].value_counts()
            clr_map = {"🟢 High Output":"#16a34a","🟡 Normal Output":ACC2,"🔴 Low Output":"#dc2626"}
            fig2 = go.Figure(go.Pie(
                labels=counts.index, values=counts.values, hole=0.58,
                marker=dict(colors=[clr_map.get(k,"#555") for k in counts.index],
                           line=dict(color=BG,width=3)),
                textfont=dict(color="white",size=12),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
            ))
            fig2.update_layout(height=275, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=8,b=0),
                              legend=dict(font=dict(color=TEXT2,size=11),bgcolor='rgba(0,0,0,0)',orientation='v',yanchor='middle',y=0.5))
            st.markdown(f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:16px;padding:20px;">', unsafe_allow_html=True)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        sp(24)
        section_title("Full Prediction Log")
        st.dataframe(hist_df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  VOICE AI PAGE
# ══════════════════════════════════════════════════════════
def voice_page():
    navbar()
    page_header("🎙️","Voice AI Assistant","Ask FlowPredict AI anything using your voice — powered by Vapi")
    st.markdown(f'<iframe src="{BACKEND_URL}/vapi" allow="microphone; autoplay; camera" '
                f'width="100%" height="600" style="border:none;background:{BG};"></iframe>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  SETTINGS PAGE
# ══════════════════════════════════════════════════════════
def settings_page():
    navbar()
    page_header("⚙️","Settings","Account information and preferences")
    st.markdown(content_wrap(), unsafe_allow_html=True)
    user = st.session_state.user_info
    _,col,_ = st.columns([1,1.8,1])

    with col:
        section_title("Account Information")
        st.markdown(f"""
        <div style="background:{CARD};border:1px solid {BORDER};
        border-radius:18px;padding:28px;margin-bottom:22px;">
          <div style="display:flex;align-items:center;gap:16px;padding-bottom:18px;
          margin-bottom:18px;border-bottom:1px solid {BORDER};">
            <div style="width:52px;height:52px;border-radius:14px;flex-shrink:0;
            background:linear-gradient(135deg,{ACC2},{ACCENT});
            display:flex;align-items:center;justify-content:center;
            font-size:20px;font-weight:800;color:white;
            box-shadow:0 4px 14px rgba(0,119,182,0.3);">{user.get('role','U')[0]}</div>
            <div>
              <div style="color:white;font-size:15px;font-weight:700;">{user.get('role','User')}</div>
              <div style="color:{TEXT2};font-size:13px;margin-top:2px;">{st.session_state.user_email}</div>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};font-size:13px;">Company</span><span style="color:{ACCENT};font-size:13px;font-weight:600;">{user.get('company','')}</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};font-size:13px;">Role</span><span style="color:{ACCENT};font-size:13px;font-weight:600;">{user.get('role','')}</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};font-size:13px;">Predictions Made</span><span style="color:{ACCENT};font-size:13px;font-weight:600;">{len(st.session_state.history)} this session</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        section_title("App Information")
        st.markdown(f"""
        <div style="background:{CARD};border:1px solid {BORDER};
        border-radius:16px;padding:22px 28px;margin-bottom:24px;">
          <div style="display:flex;flex-direction:column;gap:12px;font-size:13px;">
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};">Version</span><span style="color:{TEXT2};">2.0.0</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};">Backend</span><span style="color:{TEXT2};">FastAPI + Uvicorn</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};">ML Model</span><span style="color:{TEXT2};">CatBoost + Stacking Ensemble</span></div>
            <div style="display:flex;justify-content:space-between;"><span style="color:{TEXT3};">Best R²</span><span style="color:{ACCENT};font-weight:700;">0.9363</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Red sign-out
        st.markdown("""<style>
        .signout .stButton > button {
            background: linear-gradient(135deg, #7f1d1d, #991b1b) !important;
            box-shadow: 0 4px 14px rgba(153,27,27,0.35) !important;
        }
        </style>""", unsafe_allow_html=True)
        st.markdown('<div class="signout">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="signout_btn"):
            st.session_state.logged_in  = False
            st.session_state.user_email = ""
            st.session_state.user_info  = {}
            st.session_state.prediction = None
            st.session_state.history    = []
            st.session_state.page       = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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