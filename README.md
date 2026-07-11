# GoSlow — Lagos Traffic Congestion API

Serves your real trained model (`model.pkl`) to the dashboard, replacing the
built-in client-side simulation.

## Setup

1. Copy your `model.pkl` and `feature_name.pkl` into this `backend/` folder
   (same folder as `app.py`).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
4. Check it's alive:
   ```bash
   curl http://localhost:8000/health
   ```
   You should see `"model_loaded": true`.

## API Reference

### `GET /health`
Confirms the model loaded and how many features it expects.

### `POST /predict`
Single-stage congestion prediction — same as before, unchanged.

### `POST /optimize-route`
**New.** Multi-stop route optimization. Given a list of stops (first = departure, rest = destinations in *any* order), it:

1. Calls OSRM's **Trip** service — a real solver for "what's the best order to visit these stops," working over actual road distances (not straight-line guesses).
2. Predicts congestion for each leg of that optimized order using your trained model, chaining `congestion_lag1`/`rolling3` leg-to-leg the same way `/predict` does stage-to-stage.
3. Returns the visiting order, per-leg distance/duration/congestion, totals, and route geometry for drawing on a map.

Example request:
```json
{
  "stops": [
    { "name": "Ikeja", "lat": 6.6018, "lon": 3.3515 },
    { "name": "Balogun Market", "lat": 6.4531, "lon": 3.3958 },
    { "name": "Oshodi Market", "lat": 6.5544, "lon": 3.3488 },
    { "name": "Ojuelegba", "lat": 6.5086, "lon": 3.3653 }
  ],
  "hour": 17, "weekday": 4, "is_market_day": 1, "rain": 4.2
}
```
Returns the optimal visiting order (which may differ from the order submitted), not just the order you sent in — the whole point is that the API decides the best sequence for you. Capped at 12 stops, since OSRM's free public demo server isn't meant for very large optimization problems.

## Using it from the dashboard

1. Open `lagos_transport_dashboard.html`.
2. Go to **Route** → enter a **From** (or leave blank for your current location) and a **To** → tap **Plan route**. This resolves both points, fetches a real road route from OSRM, and splits it into stages.
3. Go to **Settings** → turn on **Use live model API** → confirm the API URL is `http://localhost:8000` (or wherever you've deployed it) → tap **Test**.
4. Back on the **Dashboard**, tap **Recalculate route** — each stage now gets its congestion score from your actual XGBoost model instead of the built-in approximation, using the route you just planned. If the API is unreachable, the dashboard falls back to the simulation automatically and shows a warning banner.

## Notes

- The API expects the 21 input features your model was trained on (hour,
  weekday, weather, market-day flag, and rolling/lag congestion features).
  The dashboard builds these automatically per stage, chaining
  `congestion_lag1` from each stage's own predicted score as it walks the
  route.
- **`zone_code` caveat:** originally trained against 6 known Lagos hubs (Ikeja, Yaba, Oshodi, Mushin, Ojuelegba, Balogun). Since routes are now planned dynamically to any destination, the frontend sends a sequential zone code (0-4) per stage as a rough position stand-in rather than an exact trained category — predictions for arbitrary destinations are directionally useful but less precise than for those original 6 hubs. The API also clamps any incoming `zone_code` to the trained range (0-5) before prediction, so a longer route with more stages than the original hubs can't push the model into extrapolating on a value it's never seen.
- `/optimize-route` calls OSRM's public demo Trip service over the network — same free-tier caveat as the routing already used elsewhere: fine for demos, not for high-volume production use.
- CORS is wide open (`allow_origins=["*"]`) for local development. Tighten
  this before deploying anywhere public.
- If you deploy the API (Render, Railway, Fly.io, etc.), just update the API
  URL field in Settings to the deployed address — no other changes needed.
