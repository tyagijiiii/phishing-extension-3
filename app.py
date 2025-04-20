from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from urllib.parse import urlparse
import joblib
import os
import re
import pandas as pd

app = FastAPI()

# Load model and scaler
scaler_path = "scaler.pkl"
model_path = "rf_model.pkl"

if not os.path.exists(scaler_path) or not os.path.exists(model_path):
    raise FileNotFoundError("Scaler or model not found. Train and save them first.")

scaler = joblib.load(scaler_path)
model = joblib.load(model_path)

# Input model
class URLRequest(BaseModel):
    url: str

# Feature extraction
def extract_url_features(url: str):
    parsed_url = urlparse(url)

    url_length = len(url)
    number_of_dots_in_url = url.count('.')
    having_repeated_digits_in_url = int(len(re.findall(r'(\d)\1', url)) > 0)
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

    domain = parsed_url.netloc
    domain_length = len(domain)
    number_of_dots_in_domain = domain.count('.')
    number_of_hyphens_in_domain = domain.count('-')
    having_special_characters_in_domain = int(bool(re.search(r'[^a-zA-Z0-9.-]', domain)))
    number_of_special_characters_in_domain = sum(not c.isalnum() and c not in ['-', '.'] for c in domain)
    having_digits_in_domain = int(any(c.isdigit() for c in domain))
    number_of_digits_in_domain = sum(c.isdigit() for c in domain)
    having_repeated_digits_in_domain = int(len(re.findall(r'(\d)\1', domain)) > 0)
    subdomains = domain.split('.')[:-2]
    number_of_subdomains = len(subdomains)
    average_subdomain_length = sum(len(sub) for sub in subdomains) / (number_of_subdomains if number_of_subdomains else 1)
    number_of_special_characters_in_subdomain = sum(not c.isalnum() and c not in ['-', '.'] for c in ''.join(subdomains))
    having_digits_in_subdomain = int(any(c.isdigit() for c in ''.join(subdomains)))
    number_of_digits_in_subdomain = sum(c.isdigit() for c in ''.join(subdomains))

    path_length = len(parsed_url.path)
    having_query = int(bool(parsed_url.query))
    having_fragment = int(bool(parsed_url.fragment))
    having_anchor = int(bool(parsed_url.fragment))

    entropy_of_url = -sum((url.count(c) / len(url)) * (url.count(c) / len(url)) for c in set(url))
    entropy_of_domain = -sum((domain.count(c) / len(domain)) * (domain.count(c) / len(domain)) for c in set(domain))

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

# Prediction endpoint
@app.post("/predict")
def predict(request: URLRequest):
    try:
        features = extract_url_features(request.url)
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]

        return {
            "prediction": "Phishing" if prediction == 1 else "Legit",
            "probabilities": {
                "Legit": probability[0],
                "Phishing": probability[1]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
