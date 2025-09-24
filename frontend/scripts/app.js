document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('capture-btn');
    const resultContainer = document.getElementById('result-container');
    const faceCountEl = document.getElementById('face-count');
    const resultImage = document.getElementById('result-image');
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');

    // Acceder a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            showError('No se pudo acceder a la cámara: ' + err.message);
        });

    captureBtn.addEventListener('click', () => {
        // Ocultar resultados anteriores
        resultContainer.classList.add('hidden');
        errorEl.classList.add('hidden');

        // Mostrar loading
        loadingEl.classList.remove('hidden');

        // Capturar imagen del video
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'capture.jpg');

            try {
                const response = await fetch('http://localhost:5000/recognize', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    faceCountEl.textContent = `Rostros detectados: ${data.face_count}`;
                    resultImage.src = 'http://localhost:5000' + data.result_image_url;
                    resultContainer.classList.remove('hidden');
                } else {
                    showError(data.error || 'Error desconocido');
                }
            } catch (err) {
                showError('Error de conexión con el servidor: ' + err.message);
            } finally {
                loadingEl.classList.add('hidden');
            }
        }, 'image/jpeg');
    });

    function showError(message) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        loadingEl.classList.add('hidden');
    }
});