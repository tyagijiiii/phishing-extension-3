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
expected_features = scaler.mean_.shape[0]

class URLRequest(BaseModel):
    url: str

# Feature extraction (34 features matching training)
def extract_url_features(url: str):
    parsed = urlparse(url)
    domain = parsed.netloc
    subs = domain.split('.')[:-2]

    features = [
        len(url),
        url.count('.'),
        int(len(re.findall(r"(\d)\1", url)) > 0),
        sum(c.isdigit() for c in url),
        sum(not c.isalnum() and c not in ['-', '_'] for c in url),
        url.count('-'),
        url.count('_'),
        url.count('/'),
        url.count('?'),
        url.count('='),
        url.count('@'),
        url.count('$'),
        url.count('!'),
        url.count('#'),
        url.count('%'),
        len(domain),
        domain.count('.'),
        domain.count('-'),
        int(bool(re.search(r"[^a-zA-Z0-9.-]", domain))),
        sum(not c.isalnum() and c not in ['-', '.'] for c in domain),
        int(any(c.isdigit() for c in domain)),
        sum(c.isdigit() for c in domain),
        int(len(re.findall(r"(\d)\1", domain)) > 0),
        len(subs),
        sum(len(s) for s in subs) / (len(subs) if subs else 1),
        sum(not c.isalnum() and c not in ['-', '.'] for c in ''.join(subs)),
        int(any(c.isdigit() for c in ''.join(subs))),
        # Total: 27 features
    ]

    if len(features) != expected_features:
        raise ValueError(f"Extracted {len(features)} features, but scaler expects {expected_features}")
    
    return features

@app.post("/predict")
async def predict(req: URLRequest):
    try:
        features = extract_url_features(req.url)
        scaled = scaler.transform([features])
        pred = model.predict(scaled)[0]
        proba = model.predict_proba(scaled)[0]
        return {
            "prediction": "Phishing" if pred == 1 else "Legit",
            "probabilities": {"Legit": float(proba[0]), "Phishing": float(proba[1])}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
