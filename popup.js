document.addEventListener("DOMContentLoaded", () => {
    chrome.storage.local.get("lastResult", (data) => {
        document.getElementById("result").textContent = data.lastResult || "Checking...";
    });
});
