document.addEventListener('DOMContentLoaded', async () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusText = document.getElementById('statusText');

    // Check current status
    const response = await chrome.runtime.sendMessage({ target: 'background', type: 'GET_STATUS' });
    updateUI(response.status);

    startBtn.addEventListener('click', async () => {
        // Get the streamId for the current tab
        chrome.tabCapture.getMediaStreamId({ consumerTabId: null }, async (streamId) => {
            if (chrome.runtime.lastError) {
                statusText.innerText = 'Error: ' + chrome.runtime.lastError.message;
                return;
            }

            // Send to background to start offscreen recording
            await chrome.runtime.sendMessage({
                target: 'background',
                type: 'START_RECORDING',
                streamId: streamId
            });

            updateUI("RECORDING");
        });
    });

    stopBtn.addEventListener('click', async () => {
        await chrome.runtime.sendMessage({ target: 'background', type: 'STOP_RECORDING' });
        updateUI("IDLE"); // Or "UPLOADING" if we had that state
        statusText.innerText = "Recording stopped. Uploading...";
    });

    function updateUI(status) {
        if (status === 'RECORDING') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusText.innerText = "Recording in progress...";
            startBtn.style.display = 'none'; // Hide start when recording
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            statusText.innerText = "Ready to record";
            startBtn.style.display = 'block';
        }
    }
});
