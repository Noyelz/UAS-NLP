document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('recordButton');
    const statusText = document.getElementById('statusText');
    const questionText = document.getElementById('questionText');
    const progressFill = document.getElementById('progressFill');
    const stepIndicator = document.getElementById('stepIndicator');
    const answerContainer = document.getElementById('answerContainer');
    const answerText = document.getElementById('answerText');
    const actionButtons = document.getElementById('actionButtons');
    const nextButton = document.getElementById('nextButton');
    const retryButton = document.getElementById('retryButton');
    const questionCard = document.getElementById('questionCard');
    const resultCard = document.getElementById('resultCard');
    const resultContent = document.getElementById('resultContent');

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let currentStep = 1;
    let totalSteps = 5;
    let nextStepData = null; // Store data for next step

    // Initialize Interview
    initInterview();

    async function initInterview() {
        try {
            const response = await fetch('/api/interview/start', { method: 'POST' });
            const data = await response.json();

            if (data.error) {
                alert('Error starting interview: ' + data.error);
                return;
            }

            currentStep = data.step;
            totalSteps = data.total_steps;
            updateUI(data.question);
        } catch (err) {
            console.error('Failed to start interview:', err);
            statusText.textContent = "Gagal memuat wawancara.";
        }
    }

    function updateUI(questionObj) {
        questionText.textContent = questionObj.text;
        stepIndicator.textContent = `Langkah ${currentStep} dari ${totalSteps}`;
        const progress = ((currentStep - 1) / totalSteps) * 100;
        progressFill.style.width = `${progress}%`;

        // Reset states
        answerContainer.style.display = 'none';
        actionButtons.style.display = 'none';
        recordButton.disabled = false;
        recordButton.classList.remove('recording');
        statusText.textContent = "Klik untuk mulai merekam jawaban";
        audioChunks = [];
    }

    // Recording Logic
    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const options = { mimeType: 'audio/webm;codecs=opus' };

            if (MediaRecorder.isTypeSupported(options.mimeType)) {
                mediaRecorder = new MediaRecorder(stream, options);
            } else {
                mediaRecorder = new MediaRecorder(stream);
            }

            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await processAudio(audioBlob);

                // Stop tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            recordButton.classList.add('recording');
            statusText.textContent = "Sedang merekam... (Klik lagi untuk berhenti)";
        } catch (err) {
            console.error("Mic Error:", err);
            statusText.textContent = "Gagal akses mikrofon.";
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            recordButton.classList.remove('recording');
            statusText.textContent = "Memproses jawaban...";
            recordButton.disabled = true;
        }
    }

    async function processAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'answer.webm');
        formData.append('step_id', currentStep);

        try {
            const response = await fetch('/api/interview/step', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.error) {
                statusText.textContent = "Error: " + data.error;
                recordButton.disabled = false;
                return;
            }

            // Success
            answerText.textContent = data.answer_text;
            answerContainer.style.display = 'block';
            actionButtons.style.display = 'block';
            statusText.textContent = "Jawaban terekam.";

            // Store next step info
            nextStepData = data;

            if (data.finished) {
                nextButton.innerHTML = 'Selesai & Lihat Hasil <i class="fas fa-check"></i>';
            } else {
                nextButton.innerHTML = 'Pertanyaan Selanjutnya <i class="fas fa-arrow-right"></i>';
            }

        } catch (err) {
            console.error(err);
            statusText.textContent = "Gagal mengirim data.";
            recordButton.disabled = false;
        }
    }

    retryButton.addEventListener('click', () => {
        // Reset UI for retry
        answerContainer.style.display = 'none';
        actionButtons.style.display = 'none';
        recordButton.disabled = false;
        statusText.textContent = "Silakan rekam ulang.";
        audioChunks = [];
    });

    nextButton.addEventListener('click', async () => {
        if (nextStepData && nextStepData.finished) {
            await finishInterview();
        } else if (nextStepData) {
            currentStep = nextStepData.next_step;
            updateUI(nextStepData.next_question);
            nextStepData = null;
        }
    });

    async function finishInterview() {
        questionCard.style.display = 'none';
        resultCard.style.display = 'block';
        resultContent.innerHTML = '<p>Sedang menganalisis semua jawaban...</p>';

        try {
            const response = await fetch('/api/interview/finish', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                renderResult(data.data);
            } else {
                resultContent.innerHTML = '<p class="error">Gagal membuat ringkasan.</p>';
            }
        } catch (err) {
            console.error(err);
            resultContent.innerHTML = '<p class="error">Terjadi kesalahan koneksi.</p>';
        }
    }

    function renderResult(data) {
        // data is JSON object
        let html = '<div class="result-summary" style="text-align: left;">';

        if (data.keluhan_utama) html += `<h4>Keluhan Utama</h4><p>${data.keluhan_utama}</p>`;

        if (data.gejala && data.gejala.length > 0) {
            html += `<h4>Gejala Terdeteksi</h4><ul>`;
            if (Array.isArray(data.gejala)) {
                data.gejala.forEach(g => html += `<li>${g}</li>`);
            } else {
                html += `<li>${data.gejala}</li>`;
            }
            html += `</ul>`;
        }

        if (data.data_vital) html += `<h4>Data Vital</h4><p>${JSON.stringify(data.data_vital).replace(/"/g, '').replace(/{|}/g, '')}</p>`;

        if (data.analisis_tb) html += `<h4>Analisis Risiko TB</h4><p><strong>${data.analisis_tb}</strong></p>`;

        if (data.saran) html += `<h4>Saran Medis</h4><p>${data.saran}</p>`;

        html += '</div>';
        resultContent.innerHTML = html;

        // Update progress to 100%
        progressFill.style.width = '100%';
        stepIndicator.textContent = "Selesai";
    }
});
