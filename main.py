from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
import os

app = FastAPI(title="Traffic Congestion Predictor API")

# Enable CORS so your React frontend can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic configuration to locate files anywhere on your machine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "feature_name.pkl")

try:
    model = joblib.load(MODEL_PATH)
    raw_features = joblib.load(FEATURES_PATH)
    feature_names = [f for f in raw_features if f != "congestion_score"]
    print(f"✅ Model & {len(feature_names)} features successfully loaded from: {BASE_DIR}")
except Exception as e:
    print(f"❌ Initialization Error: {e}")
    print("💡 Please make sure 'model.pkl' and 'feature_name.pkl' are inside this same folder!")
    feature_names = []

class TrafficInput(BaseModel):
    hour: int
    weekday: int
    is_weekend: int
    is_holiday: int
    is_market_day: int
    hour_sin: float
    hour_cos: float
    day_sin: float
    day_cos: float
    zone_code: int
    temperature_2m: float
    rain: float
    precipitation: float
    windspeed_10m: float
    cloudcover: float
    relativehumidity_2m: float
    is_raining: int
    heavy_rain: int
    congestion_lag1: float
    congestion_lag3: float
    congestion_lag24: float
    congestion_rolling3: float

@app.get("/")
def home():
    return {"status": "Online", "features_required": len(feature_names)}

@app.post("/predict")
def predict_congestion(data: TrafficInput):
    input_dict = data.model_dump()
    df = pd.DataFrame([input_dict], columns=feature_names)
    prediction = model.predict(df)[0]
    final_score = float(np.clip(prediction, 0.0, 1.0))
    return {"congestion_score": round(final_score, 4), "status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)