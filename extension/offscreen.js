// offscreen.js

let mediaRecorder;
let recordedChunks = [];

chrome.runtime.onMessage.addListener(async (message) => {
    if (message.target !== "offscreen") return;

    if (message.type === "INIT_RECORDING") {
        startRecording(message.data.streamId);
    } else if (message.type === "STOP_RECORDING") {
        stopRecording();
    }
});

async function startRecording(streamId) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                mandatory: {
                    chromeMediaSource: 'tab',
                    chromeMediaSourceId: streamId
                }
            },
            video: false
        });

        // Continue playing audio to user
        const audioCtx = new AudioContext();
        const source = audioCtx.createMediaStreamSource(stream);
        source.connect(audioCtx.destination);

        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = uploadRecording;

        mediaRecorder.start(1000); // Collect 1s chunks
        console.log("Recording started");

    } catch (error) {
        console.error("Error starting recording:", error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(t => t.stop());
    }
}

async function uploadRecording() {
    const blob = new Blob(recordedChunks, { type: 'audio/webm' });
    recordedChunks = [];

    const formData = new FormData();
    formData.append('file', blob, 'meeting_audio.webm');

    try {
        const response = await fetch('http://localhost:8000/api/upload-stream', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            console.log("Upload successful");
        } else {
            console.error("Upload failed");
        }
    } catch (err) {
        console.error("Upload error", err);
    }
}
