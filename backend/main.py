from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="FlowPredict AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load model and scaler
model  = pickle.load(open('../model/model.pkl',  'rb'))
scaler = pickle.load(open('../model/scaler.pkl', 'rb'))

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
    Shift:                      int    # encoded: 0,1,2
    Machine_Type:               int    # encoded: 0,1,2...
    Material_Grade:             int    # encoded: 0,1,2...
    Day_of_Week:                int    # encoded: 0–6
    Temperature_Pressure_Ratio: float
    Total_Cycle_Time:           float
    Efficiency_Score:           float
    Machine_Utilization:        float

@app.get("/")
def root():
    return {"message": "FlowPredict AI is running ✅"}

@app.post("/predict")
def predict(data: ManufacturingInput):
    features = np.array([[
        data.Injection_Temperature,
        data.Injection_Pressure,
        data.Cycle_Time,
        data.Cooling_Time,
        data.Material_Viscosity,
        data.Ambient_Temperature,
        data.Machine_Age,
        data.Operator_Experience,
        data.Maintenance_Hours,
        data.Shift,
        data.Machine_Type,
        data.Material_Grade,
        data.Day_of_Week,
        data.Temperature_Pressure_Ratio,
        data.Total_Cycle_Time,
        data.Efficiency_Score,
        data.Machine_Utilization
    ]])

    scaled     = scaler.transform(features)
    prediction = model.predict(scaled)[0]
    prediction = round(float(prediction), 2)

    if prediction >= 40:
        status = "🟢 High Output"
    elif prediction >= 20:
        status = "🟡 Normal Output"
    else:
        status = "🔴 Low Output"

    return {
        "predicted_parts_per_hour": prediction,
        "status": status,
        "unit": "parts/hr"
    }
