import joblib
import pandas as pd
import urllib.parse
from flask import Flask, request, jsonify

# Load trained model
model = joblib.load("random_forest_phishing_model.pkl")

# Function to extract features from a URL
def extract_features(url):
    parsed_url = urllib.parse.urlparse(url)
    return [
        len(url),  # URL length
        url.count('.'),  # Number of dots
        int("@" in url),  # Presence of '@'
        int("-" in parsed_url.netloc),  # Presence of '-'
        int(parsed_url.scheme == "https"),  # HTTPS usage
        parsed_url.netloc.count('.'),  # Number of subdomains
        url.count('/'),  # Number of '/'
        sum(c.isdigit() for c in url),  # Count of digits
        sum(c in "?&=_$" for c in url)  # Special characters
    ]

# Define API
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

# Run API
if __name__ == '__main__':
    app.run(debug=True)
