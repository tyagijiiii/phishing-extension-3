from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
from urllib.parse import urlparse
import re

# Load the trained scaler and model
scaler_path = "scaler.pkl"
model_path = "rf_model_tiny.pkl"  # Update to the compressed model path

if not os.path.exists(scaler_path) or not os.path.exists(model_path):
    raise FileNotFoundError("Scaler or model not found. Train and save them first.")

scaler = joblib.load(scaler_path)
model = joblib.load(model_path)

app = Flask(__name__)

# Dynamically set expected features based on the scaler
expected_features = scaler.mean_.shape[0]

def extract_url_features(url):
    parsed_url = urlparse(url)

    # URL-related features
    url_length = len(url)
    number_of_dots_in_url = url.count('.')
    having_repeated_digits_in_url = len(re.findall(r'(\d)\1', url)) > 0
    number_of_digits_in_url = sum(c.isdigit() for c in url)
    number_of_special_char_in_url = sum(not c.isalnum() and c not in ['-', '_'] for c in url)
    number_of_hyphens_in_url = url.count('-')
    number_of_underline_in_url = url.count('_')
    number_of_slash_in_url = url.count('/')
    number_of_questionmark_in_url = url.count('?')
    number_of_equal_in_url = url.count('=')
    number_of_at_in_url = url.count('@')
    number_of_dollar_in_url = url.count('$')
    number_of_exclamation_in_url = url.count('!')
    number_of_hashtag_in_url = url.count('#')
    number_of_percent_in_url = url.count('%')

    # Domain-related features
    domain_length = len(parsed_url.netloc)
    number_of_dots_in_domain = parsed_url.netloc.count('.')
    number_of_hyphens_in_domain = parsed_url.netloc.count('-')
    having_special_characters_in_domain = bool(re.search(r'[^a-zA-Z0-9.-]', parsed_url.netloc))
    number_of_special_characters_in_domain = sum(not c.isalnum() and c not in ['-', '.'] for c in parsed_url.netloc)
    having_digits_in_domain = any(c.isdigit() for c in parsed_url.netloc)
    number_of_digits_in_domain = sum(c.isdigit() for c in parsed_url.netloc)
    having_repeated_digits_in_domain = len(re.findall(r'(\d)\1', parsed_url.netloc)) > 0
    number_of_subdomains = len(parsed_url.netloc.split('.')) - 2  # Subdomains are in between the protocol and top-level domain
    average_subdomain_length = sum(len(sub) for sub in parsed_url.netloc.split('.')[:-2]) / (number_of_subdomains if number_of_subdomains else 1)
    number_of_special_characters_in_subdomain = sum(not c.isalnum() and c not in ['-', '.'] for c in parsed_url.netloc.split('.')[:-2])
    having_digits_in_subdomain = any(c.isdigit() for c in parsed_url.netloc.split('.')[:-2])
    number_of_digits_in_subdomain = sum(c.isdigit() for c in parsed_url.netloc.split('.')[:-2])
    
    # Path, Query, and Fragment Features
    path_length = len(parsed_url.path)
    having_query = 1 if parsed_url.query else 0
    having_fragment = 1 if parsed_url.fragment else 0
    having_anchor = 1 if parsed_url.fragment else 0

    # Entropy Features
    entropy_of_url = -sum((url.count(c) / len(url)) * (url.count(c) / len(url)) for c in set(url))
    entropy_of_domain = -sum((parsed_url.netloc.count(c) / len(parsed_url.netloc)) * (parsed_url.netloc.count(c) / len(parsed_url.netloc)) for c in set(parsed_url.netloc))

    return [
        url_length, number_of_dots_in_url, having_repeated_digits_in_url, number_of_digits_in_url,
        number_of_special_char_in_url, number_of_hyphens_in_url, number_of_underline_in_url, number_of_slash_in_url,
        number_of_questionmark_in_url, number_of_equal_in_url, number_of_at_in_url, number_of_dollar_in_url,
        number_of_exclamation_in_url, number_of_hashtag_in_url, number_of_percent_in_url, domain_length,
        number_of_dots_in_domain, number_of_hyphens_in_domain, having_special_characters_in_domain,
        number_of_special_characters_in_domain, having_digits_in_domain, number_of_digits_in_domain,
        having_repeated_digits_in_domain, number_of_subdomains, average_subdomain_length,
        number_of_special_characters_in_subdomain, having_digits_in_subdomain, number_of_digits_in_subdomain,
        path_length, having_query, having_fragment, having_anchor, entropy_of_url, entropy_of_domain
    ]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not isinstance(data, dict) or len(data) != expected_features:
            return jsonify({"error": f"Invalid input. Expected {expected_features} features."}), 400

        # Extract features from the provided URL
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        features = extract_url_features(url)

        # Scale the features
        feature_values_scaled = scaler.transform([features])

        # Predict using RF model
        prediction = model.predict(feature_values_scaled)[0]
        probability = model.predict_proba(feature_values_scaled)[0].tolist()

        return jsonify({
            "prediction": "Phishing" if prediction == 1 else "Legit",
            "probabilities": {
                "Legit": probability[0],
                "Phishing": probability[1]
            }
        })

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
