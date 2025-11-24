document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const statusText = document.getElementById('statusText');
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            // Start Recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const options = { mimeType: 'audio/webm;codecs=opus' };
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    console.warn(`${options.mimeType} is not supported, using default.`);
                    mediaRecorder = new MediaRecorder(stream);
                } else {
                    mediaRecorder = new MediaRecorder(stream, options);
                }

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    audioChunks = []; // Reset chunks

                    statusText.textContent = "Memproses suara dengan AI...";
                    recordButton.disabled = true;

                    // Upload to server
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.webm');

                    try {
                        const response = await fetch('/api/process_audio', {
                            method: 'POST',
                            body: formData
                        });

                        const result = await response.json();

                        if (result.success) {
                            statusText.textContent = "Selesai!";
                            // Reload page to show new record
                            window.location.reload();
                        } else {
                            statusText.textContent = "Error: " + (result.error || "Gagal memproses");
                        }
                    } catch (err) {
                        console.error(err);
                        statusText.textContent = "Gagal terhubung ke server.";
                    } finally {
                        recordButton.disabled = false;
                    }
                };

                mediaRecorder.start();
                isRecording = true;
                recordButton.classList.add('recording');
                statusText.textContent = "Sedang merekam... (Klik lagi untuk berhenti)";

            } catch (err) {
                console.error("Error accessing microphone:", err);
                statusText.textContent = "Gagal mengakses mikrofon. Pastikan izin diberikan.";
            }
        } else {
            // Stop Recording
            mediaRecorder.stop();
            isRecording = false;
            recordButton.classList.remove('recording');
            statusText.textContent = "Menyimpan...";

            // Stop all tracks
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    });
});
