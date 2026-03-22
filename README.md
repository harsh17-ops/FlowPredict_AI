# ⚙️ FlowPredict AI

**FlowPredict AI** is an Intelligent Manufacturing Output Prediction System. It uses a **Gradient Boosting Regressor** machine learning model to predict **Parts Per Hour** based on 17 distinct manufacturing parameters (such as Injection Temperature, Pressure, Cycle Time, Machine Age, and Operator Experience). 

The platform features a modern, beautifully designed **Streamlit Dashboard** and a real-time **Voice AI Assistant** powered by **Vapi**, all backed by a highly optimized **FastAPI** microservice.

---

## 🚀 Features
- **🔮 ML Prediction Engine:** Instantly predict manufacturing output using a custom-trained Gradient Boosting model (R² Score ~ 91%).
- **📈 Analytics Dashboard:** Visualize historical predictions, utilization capacity, and automated performance tracking using interactive Plotly charts.
- **🎙️ Voice AI Assistant:** Integrated Vapi WebRTC voice assistant. Ask contextual questions conversationally using your microphone!
- **⚡ High-Performance Backend:** FastAPI securely serves the machine learning model and resolves strict browser iframe origin policies for WebRTC integrations.
- **🎨 Premium UI:** Custom CSS-injected Streamlit interface featuring glassmorphism, dynamic animations, and curated dark-mode aesthetics.

---

## 🛠️ Tech Stack
- **Frontend:** Streamlit, Plotly, Pandas, HTML/CSS/JS (Custom Integrations)
- **Backend:** FastAPI, Uvicorn
- **Machine Learning:** Scikit-Learn, XGBoost, Numpy, Pickle
- **Voice AI:** Vapi.ai SDK (Daily.co WebRTC)

---

## 📁 Project Structure
```text
flowpredict-ai/
├── backend/
│   ├── main.py             # FastAPI Server, prediction logic, and Voice endpoint
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── app.py              # Streamlit Dashboard and UI logic
│   └── requirements.txt    # Frontend dependencies
├── model/
│   ├── model.pkl           # Pre-trained Gradient Boosting Regressor model
│   └── scaler.pkl          # Standardization scaler for input features
└── README.md
```

---

## 💻 Running Locally

Ensure you have Python 3.9+ installed.

### 1. Start the Backend (FastAPI)
Open a terminal and navigate to the `backend` folder:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
> The backend runs on `http://localhost:8000`. It exposes the `/predict` API and uniquely serves the `/vapi` widget to bypass browser iframe microphone restrictions.

### 2. Start the Frontend (Streamlit)
Open a *second* terminal and navigate to the `frontend` folder:
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
> The dashboard will open automatically in your browser at `http://localhost:8501`. 
> *⚠️ Note: Always use `localhost` (not your network IP) when testing locally, otherwise modern browsers will block the microphone.*

---

## 🌍 Production Deployment Guide

This project is fully production-ready and designed to be deployed cleanly via environment variables:

### Part 1: Deploying the Backend (Render / Railway)
1. Link your GitHub repository to a service like [Render](https://render.com/).
2. Set the Root Directory to `backend`.
3. Set the Environment to `Python`.
4. Use the start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Deploy and copy your live URL (e.g., `https://flowpredict-backend.onrender.com`).

### Part 2: Deploying the Frontend (Streamlit Cloud)
1. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Deploy a new app from your repository and point the main file path to `frontend/app.py`.
3. **Pre-Deploy Step:** Go to **Advanced Settings -> Secrets** and paste your backend URL to dynamically link the frontend to your live backend:
```toml
BACKEND_URL = "https://flowpredict-backend.onrender.com"
```
4. Click Deploy! 🎉
