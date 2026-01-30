// background.js - Service Worker

let recordingState = "IDLE"; // IDLE, RECORDING, OFFSCREEN_READY

// Listen for messages from popup or offscreen
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.target !== "background") return;

    if (message.type === "START_RECORDING") {
        await startRecording(message.streamId);
        sendResponse({ success: true });
    } else if (message.type === "STOP_RECORDING") {
        await stopRecording();
        sendResponse({ success: true });
    } else if (message.type === "GET_STATUS") {
        sendResponse({ status: recordingState });
    }

    return true;
});

async function startRecording(streamId) {
    if (recordingState === "RECORDING") return;

    // Create offscreen document
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
    });

    if (existingContexts.length > 0) {
        // Already exists
    } else {
        await chrome.offscreen.createDocument({
            url: 'offscreen.html',
            reasons: ['USER_MEDIA'],
            justification: 'Recording meeting audio',
        });
    }

    recordingState = "RECORDING";

    // Get active tab to record
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // We need to get the stream ID in the popup context usually, 
    // but for tabCapture we can use the streamId passed from popup 
    // or use activeTab to capture.

    // Actually, standard pattern: 
    // 1. Popup calls chrome.tabCapture.getMediaStreamId
    // 2. Passes ID to background
    // 3. Background passes ID to offscreen
    // 4. Offscreen uses getUserMedia with chromeMediaSource: 'tab'

    chrome.runtime.sendMessage({
        target: "offscreen",
        type: "INIT_RECORDING",
        data: { streamId: streamId }
    });
}

async function stopRecording() {
    if (recordingState !== "RECORDING") return;

    chrome.runtime.sendMessage({
        target: "offscreen",
        type: "STOP_RECORDING"
    });

    recordingState = "IDLE";

    // Close offscreen document (optional, mostly keep it open or close after upload)
    await chrome.offscreen.closeDocument();
}
