from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import os

app = FastAPI(title="FlowPredict AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Robust paths ───────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, '..', 'model', 'model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, '..', 'model', 'scaler.pkl')

model  = pickle.load(open(MODEL_PATH,  'rb'))
scaler = pickle.load(open(SCALER_PATH, 'rb'))

print("✅ Model loaded  — expects 24 features")
print("✅ Scaler loaded — expects 24 features")

# ── Input schema — 17 raw features from user ──────────────
class ManufacturingInput(BaseModel):
    Injection_Temperature:      float
    Injection_Pressure:         float
    Cycle_Time:                 float
    Cooling_Time:               float
    Material_Viscosity:         float
    Ambient_Temperature:        float
    Machine_Age:                float
    Operator_Experience:        float
    Maintenance_Hours:          float
    Shift:                      int
    Machine_Type:               int
    Material_Grade:             int
    Day_of_Week:                int
    Temperature_Pressure_Ratio: float
    Total_Cycle_Time:           float
    Efficiency_Score:           float
    Machine_Utilization:        float

@app.get("/")
def root():
    return {"message": "FlowPredict AI is running ✅"}

@app.get("/health")
def health():
    return {
        "status":           "healthy",
        "model":            "Gradient Boosting Regressor",
        "target":           "Parts Per Hour",
        "raw_features":     17,
        "total_features":   24,
        "engineered":       7
    }

@app.post("/predict")
def predict(data: ManufacturingInput):

    # ── Step 1: Original 17 features ──────────────────────
    f = data  # shorthand

    # ── Step 2: Compute 7 engineered features ─────────────
    # Same formulas used in Colab Cell 11
    Speed_Ratio            = f.Injection_Pressure / (f.Cycle_Time + 1)
    Thermal_Efficiency     = f.Injection_Temperature / (f.Cooling_Time + 1)
    Operator_Machine_Score = f.Operator_Experience * f.Machine_Utilization / 100
    Machine_Health         = (100 - f.Machine_Age * 3) * (f.Maintenance_Hours / 100 + 0.5)
    Cycle_Efficiency       = f.Efficiency_Score / (f.Total_Cycle_Time + 1)
    Pressure_Viscosity     = f.Injection_Pressure / (f.Material_Viscosity + 1)
    Temp_Deviation         = abs(f.Injection_Temperature - 215)

    # ── Step 3: Build full 24-feature array ───────────────
    # Order must match exactly what was used in Colab training
    features = np.array([[
        # Original 17
        f.Injection_Temperature,
        f.Injection_Pressure,
        f.Cycle_Time,
        f.Cooling_Time,
        f.Material_Viscosity,
        f.Ambient_Temperature,
        f.Machine_Age,
        f.Operator_Experience,
        f.Maintenance_Hours,
        f.Shift,
        f.Machine_Type,
        f.Material_Grade,
        f.Day_of_Week,
        f.Temperature_Pressure_Ratio,
        f.Total_Cycle_Time,
        f.Efficiency_Score,
        f.Machine_Utilization,
        # Engineered 7
        Speed_Ratio,
        Thermal_Efficiency,
        Operator_Machine_Score,
        Machine_Health,
        Cycle_Efficiency,
        Pressure_Viscosity,
        Temp_Deviation,
    ]])

    # ── Step 4: Scale + Predict ───────────────────────────
    scaled     = scaler.transform(features)
    prediction = model.predict(scaled)[0]
    prediction = round(float(prediction), 2)

    # ── Step 5: Status label ──────────────────────────────
    if prediction >= 40:
        status = "🟢 High Output"
    elif prediction >= 20:
        status = "🟡 Normal Output"
    else:
        status = "🔴 Low Output"

    return {
        "predicted_parts_per_hour": prediction,
        "status":                   status,
        "unit":                     "parts/hr"
    }

@app.get("/vapi", response_class=HTMLResponse)
def get_vapi_widget():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * { margin:0; padding:0; box-sizing:border-box;
              font-family:'Inter',sans-serif; }
        body {
          background: linear-gradient(135deg, #080f1a 0%, #0d1f35 100%);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 20px;
          color: white;
        }
        .mic-ring {
          width: 130px; height: 130px; border-radius: 50%;
          background: linear-gradient(135deg, #0077b6, #023e8a);
          display: flex; align-items: center; justify-content: center;
          cursor: pointer; font-size: 46px;
          box-shadow: 0 0 0 0 rgba(0,119,182,0.6);
          transition: all 0.3s ease;
          animation: pulse 2.5s infinite;
          margin-bottom: 28px;
          border: 2px solid rgba(0,180,216,0.3);
        }
        .mic-ring:hover {
          transform: scale(1.06);
          box-shadow: 0 0 40px rgba(0,119,182,0.6);
        }
        .mic-ring.listening {
          background: linear-gradient(135deg, #e63946, #c1121f);
          animation: pulse-red 1s infinite;
          box-shadow: 0 0 0 0 rgba(230,57,70,0.6);
          border-color: rgba(230,57,70,0.5);
        }
        @keyframes pulse {
          0%   { box-shadow: 0 0 0 0 rgba(0,119,182,0.5); }
          70%  { box-shadow: 0 0 0 18px rgba(0,119,182,0); }
          100% { box-shadow: 0 0 0 0 rgba(0,119,182,0); }
        }
        @keyframes pulse-red {
          0%   { box-shadow: 0 0 0 0 rgba(230,57,70,0.7); }
          70%  { box-shadow: 0 0 0 22px rgba(230,57,70,0); }
          100% { box-shadow: 0 0 0 0 rgba(230,57,70,0); }
        }
        .status {
          font-size: 15px; font-weight: 600;
          color: #00b4d8; margin-bottom: 24px;
          letter-spacing: 0.3px;
        }
        .transcript {
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 14px; padding: 22px 28px;
          min-height: 90px; width: 100%; max-width: 640px;
          color: rgba(255,255,255,0.75); font-size: 14px;
          line-height: 1.7; text-align: center;
          margin-bottom: 28px;
        }
        .hint {
          color: rgba(255,255,255,0.25);
          font-size: 12px; text-align: center;
          max-width: 480px; line-height: 1.8;
        }
        .hint strong { color: rgba(0,180,216,0.7); }
        .wave-bars {
          display: none; gap: 4px; align-items: flex-end;
          height: 30px; margin-bottom: 8px;
        }
        .wave-bars.active { display: flex; }
        .bar {
          width: 4px; border-radius: 3px;
          background: #00b4d8;
          animation: wave 0.8s ease-in-out infinite;
        }
        .bar:nth-child(1) { height: 10px; animation-delay: 0s;    }
        .bar:nth-child(2) { height: 22px; animation-delay: 0.1s;  }
        .bar:nth-child(3) { height: 14px; animation-delay: 0.2s;  }
        .bar:nth-child(4) { height: 26px; animation-delay: 0.3s;  }
        .bar:nth-child(5) { height: 18px; animation-delay: 0.15s; }
        .bar:nth-child(6) { height: 12px; animation-delay: 0.25s; }
        @keyframes wave {
          0%, 100% { transform: scaleY(1);   }
          50%       { transform: scaleY(1.8); }
        }
      </style>
    </head>
    <body>
      <div class="wave-bars" id="waveBars">
        <div class="bar"></div><div class="bar"></div>
        <div class="bar"></div><div class="bar"></div>
        <div class="bar"></div><div class="bar"></div>
      </div>

      <div class="mic-ring" id="micBtn" onclick="toggleVapi()">🎙️</div>

      <div class="status" id="statusText">Click microphone to start talking</div>

      <div class="transcript" id="transcript">
        Your conversation with FlowPredict AI will appear here...
      </div>

      <script type="module">
        import VapiAmbient from "https://cdn.jsdelivr.net/npm/@vapi-ai/web@latest/+esm";
        const Vapi = VapiAmbient.default || VapiAmbient;

        const VAPI_KEY = "f83a3655-29a5-41ed-87f6-c9ffee3568e6";
        const ASST_ID  = "e86858e1-c399-4cdb-84c2-c4735ea4b649";
        let vapi, active = false;

        function initVapi() {
          const v = new Vapi(VAPI_KEY);
          v.on('speech-start', () => {
            document.getElementById('statusText').textContent = "🔴  Listening...";
            document.getElementById('micBtn').classList.add('listening');
            document.getElementById('micBtn').textContent = "⏹️";
            document.getElementById('waveBars').classList.add('active');
          });
          v.on('speech-end', () => {
            document.getElementById('statusText').textContent = "🤖  Processing...";
            document.getElementById('waveBars').classList.remove('active');
          });
          v.on('message', (msg) => {
            if (msg.type === 'transcript') {
              const t = document.getElementById('transcript');
              if (msg.role === 'assistant') {
                t.innerHTML = '<span style="color:#00b4d8;font-weight:600;">FlowPredict AI:</span><br/>' + msg.transcript;
                document.getElementById('statusText').textContent = "✅  Response received";
              } else if (msg.role === 'user') {
                t.innerHTML = '<span style="color:rgba(255,255,255,0.5);font-weight:600;">You:</span><br/>' + msg.transcript;
              }
            }
          });
          v.on('call-end', () => {
            active = false;
            document.getElementById('statusText').textContent = "Click microphone to start talking";
            document.getElementById('micBtn').classList.remove('listening');
            document.getElementById('micBtn').textContent = "🎙️";
            document.getElementById('waveBars').classList.remove('active');
          });
          return v;
        }

        window.toggleVapi = async function() {
          if (!vapi) vapi = initVapi();
          if (!vapi) return;
          if (!active) {
            active = true;
            document.getElementById('statusText').textContent = "🔵  Connecting...";
            try {
              await vapi.start(ASST_ID);
            } catch (err) {
              document.getElementById('statusText').innerHTML = "❌ Browser blocked mic: " + err.message;
              active = false;
              document.getElementById('micBtn').classList.remove('listening');
            }
          } else {
            active = false;
            vapi.stop();
          }
        }
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)