import os
import joblib
import urllib.parse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 🔥 FastAPI App
app = FastAPI()

# ⏳ Model placeholder
rf_model = None

# ✅ Lazy load Random Forest Model on startup
@app.on_event("startup")
def load_model():
    global rf_model
    model_path = "models/random_forest_model_compressed.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ {model_path} not found. Train and save the model first.")
    
    rf_model = joblib.load(model_path)
    print("✅ Model loaded successfully")

# 🚀 Feature Extraction (no pandas)
def extract_features(url: str):
    parsed_url = urllib.parse.urlparse(url)
    return [[
        len(url),
        url.count('.'),
        int("@" in url),
        int("-" in parsed_url.netloc),
        int(parsed_url.scheme == "https"),
        parsed_url.netloc.count('.'),
        url.count('/'),
        sum(c.isdigit() for c in url),
        sum(c in "?&=_$" for c in url)
    ]]

# Define Pydantic model for input data validation
class URLRequest(BaseModel):
    url: str

@app.post("/predict")
async def predict(data: URLRequest):
    if rf_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    url = data.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    features = extract_features(url)
    prediction = rf_model.predict(features)[0]

    result = {
        "url": url,
        "prediction": "Phishing" if prediction == 1 else "Legit"
    }

    return result


@app.get("/")
async def root():
    return {"message": "URL Phishing Detector is running!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use the port specified by Render or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
