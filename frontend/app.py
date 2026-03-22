import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="FlowPredict AI",
    page_icon="⚙️",
    layout="wide"
)

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
  .main { background-color: #0a1628; }
  .stButton > button {
    background: linear-gradient(90deg, #0077b6, #023e8a);
    color: white; border: none; border-radius: 8px;
    padding: 12px 40px; font-size: 15px;
    font-weight: bold; width: 100%;
  }
  .stButton > button:hover { background: #023e8a; }
  .output-card {
    background: linear-gradient(135deg, #0077b6, #023e8a);
    padding: 24px; border-radius: 14px;
    text-align: center; color: white;
    font-size: 26px; font-weight: bold;
    box-shadow: 0 4px 20px rgba(0,119,182,0.4);
  }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────
st.markdown("<h1 style='color:#00b4d8;'>⚙️ FlowPredict AI</h1>",
            unsafe_allow_html=True)
st.markdown("*Intelligent Manufacturing Output Prediction System*")
st.markdown("---")

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ About FlowPredict AI")
    st.info("Predicts manufacturing parts output per hour using ML regression.")
    st.markdown("**Model:** XGBoost Regressor")
    st.markdown("**Target:** Parts Per Hour")
    st.markdown("**Dataset:** 1000 samples")
    st.markdown("---")
    st.markdown("**Team FlowPredict AI**")
    st.markdown("City Engineering College, Bengaluru")

# ── Inputs ──────────────────────────────────────────────────
st.markdown("### 📋 Enter Machine Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🌡️ Temperature & Pressure**")
    inj_temp  = st.slider("Injection Temperature (°C)", 180.0, 300.0, 215.0)
    inj_pres  = st.slider("Injection Pressure (bar)",   50.0,  200.0, 120.0)
    amb_temp  = st.slider("Ambient Temperature (°C)",   15.0,  45.0,  25.0)
    temp_pres = st.slider("Temp/Pressure Ratio",        0.5,   5.0,   1.8)

with col2:
    st.markdown("**⏱️ Time & Cycle**")
    cycle_time   = st.slider("Cycle Time (sec)",        5.0,  60.0, 20.0)
    cooling_time = st.slider("Cooling Time (sec)",      2.0,  30.0, 10.0)
    total_cycle  = st.slider("Total Cycle Time (sec)",  8.0,  90.0, 30.0)
    maint_hours  = st.number_input("Maintenance Hours", 0,    500,  50)

with col3:
    st.markdown("**🏭 Machine & Operator**")
    machine_age   = st.slider("Machine Age (years)",    0.0,  20.0,  5.0)
    op_exp        = st.slider("Operator Experience",    0.0,  20.0,  5.0)
    mat_visc      = st.slider("Material Viscosity",     50.0, 500.0, 200.0)
    eff_score     = st.slider("Efficiency Score",       0.0,  100.0, 75.0)
    machine_util  = st.slider("Machine Utilization %",  0.0,  100.0, 80.0)

st.markdown("**🔧 Machine Configuration**")
cfg1, cfg2, cfg3, cfg4 = st.columns(4)
with cfg1:
    shift        = st.selectbox("Shift",         [0, 1, 2],
                                format_func=lambda x: ["Morning","Afternoon","Night"][x])
with cfg2:
    machine_type = st.selectbox("Machine Type",  [0, 1, 2, 3],
                                format_func=lambda x: f"Type {x+1}")
with cfg3:
    mat_grade    = st.selectbox("Material Grade",[0, 1, 2],
                                format_func=lambda x: ["Grade A","Grade B","Grade C"][x])
with cfg4:
    day_of_week  = st.selectbox("Day of Week",   list(range(7)),
                                format_func=lambda x: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][x])

st.markdown("---")

# ── Predict ─────────────────────────────────────────────────
if st.button("⚙️  Predict Manufacturing Output"):
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

    try:
        res = requests.post("http://localhost:8000/predict", json=payload).json()

        r1, r2 = st.columns([1, 1])

        with r1:
            st.markdown(
                f"<div class='output-card'>"
                f"Predicted Output<br/>"
                f"<span style='font-size:40px'>{res['predicted_parts_per_hour']}</span>"
                f"<br/><span style='font-size:16px'>parts / hour</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:#1d3557;padding:12px;"
                f"border-radius:8px;text-align:center;"
                f"color:white;font-size:18px;'>"
                f"{res['status']}</div>",
                unsafe_allow_html=True
            )

        with r2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res['predicted_parts_per_hour'],
                title={'text': "Parts Per Hour", 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [0, 70]},
                    'bar':  {'color': '#00b4d8'},
                    'steps': [
                        {'range': [0,  20], 'color': '#fce4ec'},
                        {'range': [20, 40], 'color': '#fff8e1'},
                        {'range': [40, 70], 'color': '#e8f5e9'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 3},
                        'thickness': 0.75,
                        'value': 29.3  # dataset mean
                    }
                }
            ))
            fig.update_layout(height=280, margin=dict(t=30,b=10,l=20,r=20),
                              paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        # Input summary
        st.markdown("### 📊 Input Summary")
        st.dataframe(pd.DataFrame([payload]), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Could not connect to backend. Make sure FastAPI is running!\nError: {e}")
