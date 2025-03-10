chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete" && tab.url) {
        checkPhishing(tab.url);
    }
});

function checkPhishing(url) {
    fetch("http://your-flask-api-url/predict", {  // Replace with your ngrok or localhost URL
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        let message = data.prediction === "Phishing" ? "🚨 Warning! This site may be a phishing attempt!" : "✅ Safe site!";
        
        chrome.notifications.create({
            type: "basic",
            iconUrl: "logo.png",
            title: "Phishing Detector",
            message: message
        });

        chrome.storage.local.set({ lastResult: message });
    })
    .catch(error => console.error("Error:", error));
}
