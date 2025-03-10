import os
import requests
import joblib
import pandas as pd
import urllib.parse
from flask import Flask, request, jsonify

# ✅ Model Configuration
MODEL_PATH = "random_forest_phishing_model.pkl"
DRIVE_URL = "https://drive.google.com/uc?export=download&id=1epAux99gIiaFZUG8somh-NpCha7-Bj88"

# ✅ Function to Download the Model
def download_model():
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print("✅ Model loaded successfully!")
            return model
        except Exception as e:
            print(f"⚠️ Model loading failed: {e}. Re-downloading...")

    print("🔽 Downloading model from Google Drive...")
    response = requests.get(DRIVE_URL, stream=True)
    
    if response.status_code == 200:
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("✅ Model downloaded successfully!")
        return joblib.load(MODEL_PATH)
    else:
        raise Exception(f"❌ Failed to download model. Status Code: {response.status_code}")

# ✅ Load Model
model = download_model()

# ✅ Function to Extract Features from a URL
def extract_features(url):
    parsed_url = urllib.parse.urlparse(url)
    return [
        len(url),  
        url.count('.'),  
        int("@" in url),  
        int("-" in parsed_url.netloc),  
        int(parsed_url.scheme == "https"),  
        parsed_url.netloc.count('.'),  
        url.count('/'),  
        sum(c.isdigit() for c in url),  
        sum(c in "?&=_$" for c in url)  
    ]

# ✅ Initialize Flask API
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL missing"}), 400

    features = extract_features(url)
    features_df = pd.DataFrame([features])
    prediction = model.predict(features_df)[0]

    return jsonify({"url": url, "prediction": "Phishing" if prediction == 1 else "Legit"})

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(debug=True, port=5000)
