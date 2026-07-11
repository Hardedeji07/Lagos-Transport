import joblib
import json
import os

# Define file paths
model_file = 'model.pkl'
output_json = 'model_readable.json'

if not os.path.exists(model_file):
    print(f"❌ Error: Could not find '{model_file}' in this folder.")
else:
    try:
        # Load the model using joblib
        model = joblib.load(model_file)
        
        # 1. Extract the internal Booster configurations from XGBoost
        booster = model.get_booster()
        model_config = json.loads(booster.save_config())
        
        # 2. Save the structure to a beautifully formatted JSON file
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(model_config, f, indent=4)
            
        print(f"✅ Success! Your model has been translated into plain text.")
        print(f"📁 Open '{output_json}' in VS Code to view hyper-parameters and configurations!")
        
        # 3. Dump the literal decision trees as text
        output_trees = 'model_trees.txt'
        trees_dump = booster.get_dump()
        with open(output_trees, 'w', encoding='utf-8') as f:
            for i, tree in enumerate(trees_dump):
                f.write(f"=== DECISION TREE {i} ===\n")
                f.write(tree)
                f.write("\n\n")
        print(f"📁 Open '{output_trees}' in VS Code to read the exact decision logic split by split!")

    except Exception as e:
        print(f"❌ An error occurred during conversion: {e}")