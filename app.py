import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

META_MODEL_PATH = "meta_model_xgboost.json"  # Use JSON instead of .pkl

if os.path.exists(META_MODEL_PATH):
    meta_model = xgb.Booster()
    meta_model.load_model(META_MODEL_PATH)  # Load JSON model
    print("✅ Meta-Model Loaded Successfully!")
else:
    raise FileNotFoundError(f"❌ {META_MODEL_PATH} not found. Train and save the model first.")


app = Flask(__name__)

scaler = StandardScaler()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    if not isinstance(data, dict) or len(data) != 42:
        return jsonify({"error": "Invalid input format. Provide exactly 42 numerical features."}), 400

    try:
        feature_values = pd.DataFrame([list(data.values())])
        feature_values_scaled = scaler.fit_transform(feature_values)
        prediction = meta_model.predict(feature_values_scaled)[0]

        return jsonify({
            "prediction": "Phishing" if prediction == 1 else "Legit"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Modify Flask to Work on Render
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
