import os
import joblib
import pandas as pd
import numpy as np
import xgboost as xgb

def load_and_predict():
    # Define file names
    features_file = 'feature_name.pkl'
    model_file = 'model.pkl'

    # Check if files exist in the directory
    if not os.path.exists(features_file) or not os.path.exists(model_file):
        print("❌ Error: Make sure 'feature_name.pkl' and 'model.pkl' are in this exact folder.")
        return

    # 1. Open and read the feature names
    print("--- Step 1: Reading Feature Names ---")
    feature_names = joblib.load(features_file)
    print(f"Successfully loaded {len(feature_names)} features.")
    
    # Cleanly display the features list
    features_list = list(feature_names)
    for idx, name in enumerate(features_list, start=1):
        print(f"  {idx}. {name}")
    print("-" * 40)

    # 2. Open and load the XGBoost Model
    print("\n--- Step 2: Loading Trained Model ---")
    model = joblib.load(model_file)
    print(f"Model Type: {type(model)}")
    print("-" * 40)

    # 3. Setup mock data to test a traffic prediction scenario
    print("\n--- Step 3: Setting Up Test Scenario & Predicting ---")
    
    # Mock scenario: 5:00 PM (17:00) on a Friday, rainy weather, high historical traffic
    mock_scenario = {
        'hour': 17,
        'weekday': 4,              # Friday (0=Monday, 6=Sunday)
        'is_weekend': 0,           # False
        'is_holiday': 0,           # False
        'is_market_day': 1,        # True (rush hour market activity)
        'hour_sin': np.sin(2 * np.pi * 17 / 24),
        'hour_cos': np.cos(2 * np.pi * 17 / 24),
        'day_sin': np.sin(2 * np.pi * 4 / 7),
        'day_cos': np.cos(2 * np.pi * 4 / 7),
        'zone_code': 1,            # Transport corridor zone identifier
        'temperature_2m': 28.5,    # Temperature in °C
        'rain': 4.2,               # Rain in mm
        'precipitation': 4.2,
        'windspeed_10m': 12.0,
        'cloudcover': 85.0,
        'relativehumidity_2m': 90.0,
        'is_raining': 1,           # True
        'heavy_rain': 0,           # False
        'congestion_lag1': 0.75,   # Traffic score 1 hour ago
        'congestion_lag3': 0.60,   # Traffic score 3 hours ago
        'congestion_lag24': 0.70,  # Traffic score 24 hours ago
        'congestion_rolling3': 0.68,# 3-hour rolling average
        'congestion_score': 0.0    # Placeholder (target column to be predicted)
    }

    # Convert scenario to a pandas DataFrame
    df_input = pd.DataFrame([mock_scenario])

    # Ensure columns match the precise layout and order expected by the model
    # (Excludes the target 'congestion_score' column itself)
    features_to_model = [f for f in features_list if f != 'congestion_score']
    df_input = df_input[features_to_model]

    # Generate prediction
    prediction = model.predict(df_input)
    print(f"🚨 Predicted Traffic Congestion Score: {prediction[0]:.4f}")

if __name__ == "__main__":
    load_and_predict()