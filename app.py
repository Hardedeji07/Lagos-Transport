"""
GoSlow — Lagos traffic congestion prediction API.

Loads the trained XGBoost model (model.pkl) and its feature order
(feature_name.pkl) and exposes:
  - POST /predict         single-stage congestion prediction (used by the
                           dashboard's "Recalculate route")
  - POST /optimize-route  multi-stop route optimization: finds the best
                           visiting order for a list of stops (via OSRM's
                           Trip service) and predicts congestion per leg

Run:
    pip install -r requirements.txt
    uvicorn app:app --reload --port 8000

Place model.pkl and feature_name.pkl in this same folder before starting
(or set MODEL_PATH / FEATURES_PATH env vars to point elsewhere).
"""

import os
import math
import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

MODEL_PATH = os.environ.get("MODEL_PATH", "model.pkl")
FEATURES_PATH = os.environ.get("FEATURES_PATH", "feature_name.pkl")
OSRM_TRIP_URL = os.environ.get("OSRM_TRIP_URL", "https://router.project-osrm.org/trip/v1/driving")

app = FastAPI(title="GoSlow · Lagos Traffic Prediction API")

# Dev-friendly CORS so the dashboard (served from a file:// or localhost
# origin) can call this API directly from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
feature_names = None
load_error = None

try:
    model = joblib.load(MODEL_PATH)
    feature_names = list(joblib.load(FEATURES_PATH))
except Exception as e:  # noqa: BLE001 - surfaced via /health for the user
    load_error = str(e)


class PredictRequest(BaseModel):
    hour: int
    weekday: int
    is_weekend: int = 0
    is_holiday: int = 0
    is_market_day: int = 0
    hour_sin: float
    hour_cos: float
    day_sin: float
    day_cos: float
    # NOTE: zone_code was originally trained against 6 known Lagos hubs
    # (Ikeja=0, Yaba=1, Oshodi=2, Mushin=3, Ojuelegba=4, Balogun=5). Since
    # routes are now planned dynamically (From/To + OSRM) instead of fixed
    # named stops, the frontend assigns zone_code sequentially per stage
    # (0-4) as a geographic-position approximation, not an exact category
    # match. Predictions for arbitrary destinations are therefore
    # directionally useful but less precise than for the original 6 hubs.
    zone_code: int
    temperature_2m: float = 28.0
    rain: float = 0.0
    precipitation: float = 0.0
    windspeed_10m: float = 10.0
    cloudcover: float = 50.0
    relativehumidity_2m: float = 70.0
    is_raining: int = 0
    heavy_rain: int = 0
    congestion_lag1: float = 0.5
    congestion_lag3: float = 0.5
    congestion_lag24: float = 0.5
    congestion_rolling3: float = 0.5


class Stop(BaseModel):
    name: Optional[str] = None
    lat: float
    lon: float


class OptimizeRequest(BaseModel):
    stops: List[Stop]                 # first = departure, rest = destinations to visit, in any order
    hour: int
    weekday: int
    is_weekend: int = 0
    is_holiday: int = 0
    is_market_day: int = 0
    temperature_2m: float = 28.0
    rain: float = 0.0
    windspeed_10m: float = 10.0
    cloudcover: float = 50.0
    relativehumidity_2m: float = 70.0


def predict_score(payload: dict) -> float:
    """Shared prediction path used by both /predict and /optimize-route."""
    if model is None or feature_names is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. Check MODEL_PATH/FEATURES_PATH. ({load_error})",
        )
    payload = dict(payload)
    payload["congestion_score"] = 0.0
    payload["zone_code"] = max(0, min(5, payload.get("zone_code", 0)))
    try:
        model_features = [f for f in feature_names if f != "congestion_score"]
        row = {f: payload.get(f, 0.0) for f in model_features}
        df = pd.DataFrame([row])[model_features]
        prediction = float(model.predict(df)[0])
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
    return max(0.0, min(1.0, prediction))


@app.get("/health")
def health():
    model_features = [f for f in feature_names if f != "congestion_score"] if feature_names else None
    return {
        "model_loaded": model is not None,
        "num_features_expected": len(model_features) if model_features else None,
        "feature_list_length": len(feature_names) if feature_names else None,
        "error": load_error,
    }


@app.post("/predict")
def predict(req: PredictRequest):
    return {"congestion_score": predict_score(req.dict())}


@app.post("/optimize-route")
def optimize_route(req: OptimizeRequest):
    """
    Finds the best order to visit a list of stops (route optimization),
    then predicts congestion for each leg of that optimized route.

    Route ordering comes from OSRM's Trip service (a real TSP solver over
    actual road distances) — the model doesn't invent the ordering itself,
    it scores congestion on the roads OSRM says are the optimal path.
    """
    if len(req.stops) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 stops (1 departure + 1 destination).")
    if len(req.stops) > 12:
        raise HTTPException(status_code=400, detail="Too many stops for the free OSRM demo server — keep it to 12 or fewer.")

    coords = ";".join(f"{s.lon},{s.lat}" for s in req.stops)
    url = f"{OSRM_TRIP_URL}/{coords}?source=first&destination=last&roundtrip=false&geometries=geojson&overview=full"

    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the routing service: {e}")

    if data.get("code") != "Ok" or not data.get("trips"):
        raise HTTPException(status_code=422, detail=f"No drivable route found between those stops (OSRM said: {data.get('code')}).")

    trip = data["trips"][0]
    # waypoints are in INPUT order; waypoint_index gives each one's position
    # in the actual optimized visiting order.
    order = sorted(range(len(req.stops)), key=lambda i: data["waypoints"][i]["waypoint_index"])
    ordered_stops = [req.stops[i] for i in order]

    hour_angle = 2 * math.pi * req.hour / 24
    day_angle = 2 * math.pi * req.weekday / 7
    is_raining = 1 if req.rain > 0 else 0
    base_features = {
        "hour": req.hour, "weekday": req.weekday,
        "is_weekend": req.is_weekend, "is_holiday": req.is_holiday, "is_market_day": req.is_market_day,
        "hour_sin": math.sin(hour_angle), "hour_cos": math.cos(hour_angle),
        "day_sin": math.sin(day_angle), "day_cos": math.cos(day_angle),
        "temperature_2m": req.temperature_2m, "rain": req.rain, "precipitation": req.rain,
        "windspeed_10m": req.windspeed_10m, "cloudcover": req.cloudcover,
        "relativehumidity_2m": req.relativehumidity_2m,
        "is_raining": is_raining, "heavy_rain": 1 if req.rain > 10 else 0,
    }

    legs_out = []
    history = []  # predicted scores so far, for lag/rolling features — mirrors the frontend's chaining logic
    for i, leg in enumerate(trip.get("legs", [])):
        lag1 = history[-1] if history else 0.5
        lag3 = history[-3] if len(history) >= 3 else lag1
        rolling3 = sum(history[-3:]) / len(history[-3:]) if history else lag1

        score = predict_score({
            **base_features,
            "zone_code": i + 1,
            "congestion_lag1": lag1, "congestion_lag3": lag3,
            "congestion_lag24": lag1, "congestion_rolling3": rolling3,
        })
        history.append(score)

        legs_out.append({
            "from": ordered_stops[i].name or f"Stop {order[i]}",
            "to": ordered_stops[i+1].name or f"Stop {order[i+1]}",
            "distance_m": leg["distance"],
            "duration_s_free_flow": leg["duration"],
            "congestion_score": score,
        })

    return {
        "visit_order": order,  # indices into the original req.stops list, in the order to actually visit them
        "ordered_stop_names": [s.name or f"Stop {i}" for s, i in zip(ordered_stops, order)],
        "legs": legs_out,
        "total_distance_m": trip["distance"],
        "total_duration_s_free_flow": trip["duration"],
        "geometry": trip["geometry"],  # GeoJSON coordinates for drawing the optimized path on a map
    }
