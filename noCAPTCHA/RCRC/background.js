chrome.commands.onCommand.addListener(function (command) {
    if (command === "A") {
        chrome.tabs.executeScript({ file: 'stage1.js' });
    } else if (command === "B") {
        chrome.tabs.executeScript({ file: 'stage2.js' });
    } else if (command === "C") {
        chrome.tabs.executeScript({ file: 'stage3.js' });
    }
});