from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import joblib
import os
import re
import pandas as pd

app = FastAPI()

# Paths to model and scaler (trained on 34 features)
model_path = "models/rf_model.pkl"
scaler_path = "models/scaler.pkl"

# Ensure files exist
for p in (model_path, scaler_path):
    if not os.path.exists(p):
        raise FileNotFoundError(f"Required file not found: {p}")

# Load model and scaler
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
# Determine expected feature count from scaler
expected_features = scaler.mean_.shape[0]

class URLRequest(BaseModel):
    url: str

# Feature extraction (34 features matching training)
def extract_url_features(url: str):
    parsed = urlparse(url)
    domain = parsed.netloc
    subs = domain.split('.')[:-2]

    features = [
        len(url),  # 1
        url.count('.'),  # 2
        int(len(re.findall(r"(\d)\1", url)) > 0),  # 3
        sum(c.isdigit() for c in url),  # 4
        sum(not c.isalnum() and c not in ['-', '_'] for c in url),  # 5
        url.count('-'),  # 6
        url.count('_'),  # 7
        url.count('/'),  # 8
        url.count('?'),  # 9
        url.count('='),  # 10
        url.count('@'),  # 11
        url.count('$'),  # 12
        url.count('!'),  # 13
        url.count('#'),  # 14
        url.count('%'),  # 15
        len(domain),  # 16
        domain.count('.'),  # 17
        domain.count('-'),  # 18
        int(bool(re.search(r"[^a-zA-Z0-9.-]", domain))),  # 19
        sum(not c.isalnum() and c not in ['-', '.'] for c in domain),  # 20
        int(any(c.isdigit() for c in domain)),  # 21
        sum(c.isdigit() for c in domain),  # 22
        int(len(re.findall(r"(\d)\1", domain)) > 0),  # 23
        len(subs),  # 24
        sum(len(s) for s in subs) / (len(subs) if subs else 1),  # 25
        sum(not c.isalnum() and c not in ['-', '.'] for c in ''.join(subs)),  # 26
        int(any(c.isdigit() for c in ''.join(subs))),  # 27
        # Remove or adjust any additional features that exceed 27
    ]

    if len(features) != expected_features:
        raise ValueError(f"Extracted {len(features)} features, but scaler expects {expected_features}")
    
    return features
@app.post("/predict")
async def predict(req: URLRequest):
    try:
        # Extract raw features
        features = extract_url_features(req.url)
        # Scale features
        scaled = scaler.transform([features])
        # Predict
        pred = model.predict(scaled)[0]
        proba = model.predict_proba(scaled)[0]
        return {
            "prediction": "Phishing" if pred == 1 else "Legit",
            "probabilities": {"Legit": float(proba[0]), "Phishing": float(proba[1])}
        }
except Exception as e:
    print("Error:", e)
=======
        raise HTTPException(status_code=500, detail=str(e))
>>>>>>> cf7a338486d730819faf48096b59314b22f6fd4f
