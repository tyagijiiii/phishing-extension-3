# Phishing Detection System

Description:
This project is a **phishing detection system** that utilizes **machine learning** to classify URLs as phishing or legitimate. It consists of:
- A **Flask API** that processes URLs and predicts their legitimacy.
- A **Browser Extension** for real-time URL scanning.
- A **Machine Learning Model** (Random Forest & XGBoost) trained on phishing datasets.

Features:
- **Real-time URL classification** via a REST API.
- **Ensemble learning** (Random Forest & XGBoost) for better accuracy.
- **Browser extension** that scans URLs automatically.
- **Lightweight and user-friendly UI**.

Installation:
Clone the Repository-
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo

Install Dependencies:
```bash
pip install -r requirements.txt
```

Run the Flask Server:
```bash
python app.py
```

Load the Browser Extension:
1. Open **Chrome** and go to `chrome://extensions/`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the extension folder.

Usage:
- **API:** Send a POST request to the Flask API with a URL to classify it.
- **Browser Extension:** The extension automatically scans URLs when opened.
- **Results:** Displays whether the website is **Phishing** or **Legitimate**.

Technologies Used:
- **Python:** Flask, scikit-learn, xgboost, pandas
- **JavaScript:** Chrome Extension (background.js, popup.js)
- **HTML/CSS:** Frontend for the browser extension

Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

License
This project is licensed under the **MIT License**.
