import os
import joblib
import pandas as pd

def read_lagos_transport_features():
    # File name configuration
    file_path = 'feature_name.pkl'
    
    # Check if the file exists in the current folder to prevent errors
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find '{file_path}' in this folder.")
        print("Please ensure the script is running in the same directory as your pickle file.")
        return

    try:
        # Load the feature names using joblib to avoid namespace errors
        feature_names = joblib.load(file_path)
        
        # Display the formatted header details
        print("=" * 45)
        print("       LAGOS TRANSPORT FEATURE EXPLORER       ")
        print("=" * 45)
        print(f"📁 Source File: {file_path}")
        print(f"📊 Data Type:   {type(feature_names)}")
        print(f"🔢 Total Count: {len(feature_names)} features")
        print("-" * 45)
        
        # Iteratively print each feature name with a clean enumeration list
        print("List of Features:")
        for index, feature in enumerate(feature_names, start=1):
            print(f"  {index:02d}. {feature}")
            
        print("=" * 45)
        
    except Exception as e:
        print(f"❌ An unexpected error occurred while reading the file: {e}")

if __name__ == "__main__":
    read_lagos_transport_features()