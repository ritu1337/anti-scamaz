// Perform the callback when a message is received from the content script
chrome.runtime.onMessage.addListener(function(message, sender) {
    if (message.action == 'update icon') {
        console.log('wutface')

        chrome.pageAction.setIcon({
            tabId: sender.tab.id,
            path: "icons/wutface.png"
        });
    }
});

// Check whether new version is installed
chrome.runtime.onInstalled.addListener(function(details) {
    if (details.reason == "install") {
        console.log("This is a first install!");

        var homepage_url = "https://github.com/RiTu1337/anti-scamaz";
        chrome.tabs.create({
            url: homepage_url
        });
    } else if (details.reason == "update") {
        var thisVersion = chrome.runtime.getManifest().version;
        console.log("Updated from " + details.previousVersion + " to " + thisVersion + "!");
    }
});
