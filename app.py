import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Define model path
META_MODEL_PATH = "meta_model_xgboost.json"  # Ensure it's JSON format

# Load the XGBoost model
if os.path.exists(META_MODEL_PATH):
    meta_model = xgb.Booster()
    meta_model.load_model(META_MODEL_PATH)  # Load JSON model
    print("✅ Meta-Model Loaded Successfully!")
else:
    raise FileNotFoundError(f"❌ {META_MODEL_PATH} not found. Train and save the model first.")

# Initialize Flask app
app = Flask(__name__)

# Initialize Scaler (should use fit_transform only if fitting first)
scaler = StandardScaler()

@app.route("/")
def home():
    return "Hello, your phishing detection API is running!"

@app.route('/predict', methods=['GET', 'POST'])

def predict(): 
    data = request.json

    if not isinstance(data, dict) or len(data) != 42:
        return jsonify({"error": "Invalid input format. Provide exactly 42 numerical features."}), 400

    try:
        feature_values = pd.DataFrame([list(data.values())])
        feature_values_scaled = scaler.fit_transform(feature_values)  # Consider using transform() if already fitted
        dmatrix = xgb.DMatrix(feature_values_scaled)  # Convert to DMatrix for XGBoost
        prediction = meta_model.predict(dmatrix)[0]  # Get prediction

        return jsonify({
            "prediction": "Phishing" if prediction == 1 else "Legit"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask App on Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use 10000 or whatever Render assigns
    app.run(host="0.0.0.0", port=port, debug=True)
