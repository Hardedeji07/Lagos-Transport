import pickle
import xgboost as xgb  # Required since model.pkl contains an XGBoost regressor

# 1. How to open and look at the features list
with open('feature_name.pkl', 'rb') as f:
    features = pickle.load(f)

print("--- Feature Names ---")
print(type(features))
print(features)


# 2. How to open and inspect the trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

print("\n--- Model Information ---")
print(type(model))
print(model)

# If it is an XGBoost model, you can check its parameters
if hasattr(model, 'get_params'):
    print("\nModel Parameters:")
    print(model.get_params())