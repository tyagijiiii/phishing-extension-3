const API_URL = "https://d171-34-16-166-188.ngrok-free.app/predict"; // Updated API URL

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete" && tab.url) {
        checkPhishing(tab.url);
    }
});

function checkPhishing(url) {
    fetch(API_URL, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        let message = data.prediction === "Phishing" 
            ? "🚨 Warning! This site may be a phishing attempt!" 
            : "✅ Safe site!";

        chrome.notifications.create({
            type: "basic",
            iconUrl: "icon.png",
            title: "Phishing Detector",
            message: message
        });

        chrome.storage.local.set({ lastResult: message });
    })
    .catch(error => console.error("Error:", error));
}
