# ⚙️ FlowPredict AI

**FlowPredict AI** is an Intelligent Manufacturing Equipment Output Prediction System built as a Capstone ML Project. It uses a **Stacking Ensemble of 6 ML models** (best: **CatBoost Regressor**, R² = 0.9363) to predict **Parts Per Hour** in real-time from 17 manufacturing parameters — including Injection Temperature, Pressure, Cycle Time, Machine Age, and Operator Experience.

The platform features a premium **Streamlit Dashboard** with dark/light mode, a real-time **Voice AI Assistant** powered by **Vapi**, and a high-performance **FastAPI** backend that computes 25 engineered features on every prediction request.

> 🏆 **Best Model:** CatBoost · **R² = 0.9363** · **RMSE = 2.8827 parts/hr** · **42 features** (17 raw + 25 engineered)

---

## 🚀 Features

| Feature | Description |
|---|---|
| **🔮 ML Prediction Engine** | Stacking Ensemble of 6 models (XGBoost, LightGBM, CatBoost, Gradient Boosting, Extra Trees, Random Forest) with Ridge meta-learner. Achieves R² = 0.9363 on test data |
| **🧠 Feature Engineering** | Backend automatically computes 25 derived features from 17 raw inputs — log transforms, ratios, interaction terms, and polynomial features |
| **📈 Analytics Dashboard** | Session prediction history, trend charts, output status distribution, and performance vs dataset average |
| **🎙️ Voice AI Assistant** | Integrated Vapi WebRTC voice assistant — ask about model accuracy, feature importance, or usage guidance hands-free |
| **⚡ High-Performance Backend** | FastAPI serves the model with sub-100ms response times and resolves strict browser iframe origin policies for WebRTC |
| **🎨 Premium UI** | Glassmorphism navbar, animated stat counters, dark/light mode toggle, hover animations, and curated dark-mode aesthetics |

---

## 📊 Model Performance

| Model | R² Score | RMSE | MAE |
|---|---|---|---|
| **CatBoost ⭐ Best** | **0.9363** | **2.8827** | **2.2574** |
| Gradient Boosting | 0.9204 | 3.2230 | 2.5025 |
| XGBoost | 0.9146 | 3.3379 | 2.5656 |
| LightGBM | 0.9134 | 3.3615 | 2.6671 |
| Ridge Regression | 0.9118 | 3.3933 | 2.6732 |
| Linear Regression | 0.9093 | 3.4402 | 2.6613 |
| Random Forest | 0.8638 | 4.2163 | 3.2593 |
| **Stacking Ensemble** | **0.9332** | **2.9533** | **2.3614** |

**5-Fold KFold CV R²: 0.9343 ± 0.011** — stable, no overfitting.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Machine Learning** | CatBoost, XGBoost, LightGBM, Scikit-Learn, Optuna (Bayesian tuning) |
| **Backend** | FastAPI, Uvicorn, Pandas, NumPy, Pickle |
| **Frontend** | Streamlit, Plotly, HTML/CSS/JS (custom integrations) |
| **Voice AI** | Vapi.ai SDK (Daily.co WebRTC) |

---

## 📁 Project Structure

```text
flowpredict-ai/
├── backend/
│   ├── main.py               # FastAPI server, 42-feature prediction logic, Vapi endpoint
│   └── requirements.txt      # Backend dependencies
├── frontend/
│   ├── app.py                # Streamlit dashboard — all pages, dark/light mode
│   └── requirements.txt      # Frontend dependencies
├── model/
│   ├── model.pkl             # Trained CatBoost / Stacking Ensemble model
│   ├── scaler.pkl            # StandardScaler fitted on all 42 features
│   └── feature_names.pkl     # Exact feature column order (CRITICAL for correct predictions)
├── notebook/
│   └── training.ipynb        # Full training pipeline — EDA → preprocessing → models → evaluation
└── README.md
```

> ⚠️ **Important:** `feature_names.pkl` ensures the backend sends features to the scaler in the exact same column order used during training. Without it, predictions will be wildly incorrect.

---

## 💻 Running Locally

Requires Python 3.9+.

### Step 1 — Install Dependencies

```bash
# Install everything at once
pip install fastapi uvicorn scikit-learn xgboost lightgbm catboost numpy pandas streamlit plotly requests
```

Or separately:

```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend (new terminal)
cd frontend && pip install -r requirements.txt
```

### Step 2 — Start the Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
✅ Model loaded
✅ Scaler loaded
✅ Feature names loaded — 42 features
INFO: Uvicorn running on http://127.0.0.1:8000
```

Verify at: `http://localhost:8000/health`

### Step 3 — Start the Frontend (Streamlit)

Open a **second terminal**:

```bash
cd frontend
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

> ⚠️ **Always use `localhost`** (not your network IP) when testing locally — modern browsers block microphone access on non-localhost origins.

### Step 4 — Login

Use any of the demo accounts:

| Email | Password | Role |
|---|---|---|
| admin@flowpredict.ai | admin123 | Admin |
| manager@acmecorp.com | acme2024 | Manager |
| operator@steelworks.com | steel2024 | Operator |

---

## 🔮 How Predictions Work

The backend receives 17 raw user inputs and automatically computes 25 additional engineered features before passing 42 total features to the scaler and model:

```
User Input (17 params)
        ↓
Feature Engineering (25 derived: log transforms, ratios, interactions, polynomials)
        ↓
StandardScaler (fitted on all 42 features in exact training order)
        ↓
CatBoost / Stacking Ensemble
        ↓
Predicted Parts Per Hour (5.0 – 68.6 range)
```

**Key engineered features:**
- `Cycle_Time_Sq` — most important feature (importance: 14.5)
- `Speed_Ratio = Injection_Pressure / (Cycle_Time + 1)`
- `Log_Cycle_Time`, `Log_Total_Cycle`, `Log_Cooling_Time`
- `Human_Factor = Operator_Experience × Efficiency_Score / 100`
- `Machine_Performance = (Utilization × Efficiency) / (Age + 1)`

---

## 🌍 Production Deployment

### Deploy Backend (Render / Railway)

1. Push your repo to GitHub
2. Create a new Web Service on [Render](https://render.com/)
3. Set **Root Directory** to `backend`
4. Set **Start Command** to:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 10000
   ```
5. Deploy and copy your live URL (e.g., `https://flowpredict-backend.onrender.com`)

### Deploy Frontend (Streamlit Cloud)

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Connect your GitHub repo, set main file to `frontend/app.py`
3. Under **Advanced Settings → Secrets**, add:
   ```toml
   BACKEND_URL = "https://flowpredict-backend.onrender.com"
   ```
4. Click **Deploy** 🎉

---

## 👥 Team

**Group 2 · TNS India Foundation · B.E. AI & ML · City Engineering College · 2026**

| Name | Role |
|---|---|
| **Harshavardhan G** | Lead — ML, Backend, Deployment |
| **Channakeshava L** | Frontend, Backend Support |
| **Madhushree S** | Documentation, Report |
| **Kranti Shantveer** | Frontend (PulseCheck AI) |
| **Kondreddy Akhila** | ML, EDA (PulseCheck AI) |
| **P Raghu Ram Reddy** | Presentation, Documentation |

---

## 📄 License

This project was built for academic purposes as part of a Capstone Project submission.
