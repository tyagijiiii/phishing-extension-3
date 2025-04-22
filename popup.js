document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get("lastResult", (data) => {
        if (chrome.runtime.lastError) {
            console.error("Error retrieving last result:", chrome.runtime.lastError);
            document.getElementById("result").textContent = "Unable to retrieve result.";
        } else {
            document.getElementById("result").textContent = data.lastResult || "Checking...";
        }
    });
});
