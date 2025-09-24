document.addEventListener('DOMContentLoaded', () => {
    // Tabs
    const tabRecognize = document.getElementById('tab-recognize');
    const tabRegister = document.getElementById('tab-register');
    const recognizeSection = document.getElementById('recognize-section');
    const registerSection = document.getElementById('register-section');

    // Video
    const videoRecognize = document.getElementById('video-recognize');
    const videoRegister = document.getElementById('video-register');

    // Recognition
    const captureBtn = document.getElementById('capture-btn');
    const resultContainer = document.getElementById('result-container');
    const faceCountEl = document.getElementById('face-count');
    const recognizedNamesEl = document.getElementById('recognized-names');
    const resultImage = document.getElementById('result-image');

    // Registration
    const nombreInput = document.getElementById('nombre-input');
    const apellidoInput = document.getElementById('apellido-input');
    const dniInput = document.getElementById('dni-input');
    const emailInput = document.getElementById('email-input');
    const registerBtn = document.getElementById('register-btn');
    const registerFeedback = document.getElementById('register-feedback');

    // Common
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');

    let stream = null;

    async function startCamera() {
        try {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRecognize.srcObject = stream;
            videoRegister.srcObject = stream;
        } catch (err) {
            showError('No se pudo acceder a la cámara: ' + err.message);
        }
    }

    tabRecognize.addEventListener('click', () => {
        tabRecognize.classList.add('active');
        tabRegister.classList.remove('active');
        recognizeSection.classList.add('active');
        registerSection.classList.remove('active');
    });

    tabRegister.addEventListener('click', () => {
        tabRegister.classList.add('active');
        tabRecognize.classList.remove('active');
        registerSection.classList.add('active');
        recognizeSection.classList.remove('active');
    });

    captureBtn.addEventListener('click', () => {
        handleRequest(async () => {
            const blob = await captureFrame(videoRecognize);
            const formData = new FormData();
            formData.append('image', blob, 'capture.jpg');

            const response = await fetch('http://localhost:5000/recognize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                faceCountEl.textContent = `Rostros detectados: ${data.face_count}`;
                displayRecognizedUsers(data.recognized_users);
                resultImage.src = 'http://localhost:5000' + data.result_image_url;
                resultContainer.classList.remove('hidden');
            } else {
                showError(data.error || 'Error desconocido en el reconocimiento');
            }
        });
    });

    registerBtn.addEventListener('click', () => {
        const nombre = nombreInput.value.trim();
        const apellido = apellidoInput.value.trim();
        const dni = dniInput.value.trim();
        const email = emailInput.value.trim();

        if (!nombre || !apellido || !dni || !email) {
            showFeedback('Todos los campos son obligatorios.', 'error');
            return;
        }

        handleRequest(async () => {
            const blob = await captureFrame(videoRegister);
            const formData = new FormData();
            formData.append('image', blob, 'register.jpg');
            formData.append('nombre', nombre);
            formData.append('apellido', apellido);
            formData.append('dni', dni);
            formData.append('email', email);

            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showFeedback(`Usuario '${nombre} ${apellido}' registrado con éxito.`, 'success');
                [nombreInput, apellidoInput, dniInput, emailInput].forEach(input => input.value = '');
            } else {
                showFeedback(data.error || 'Error desconocido en el registro.', 'error');
            }
        });
    });

    function displayRecognizedUsers(users) {
        recognizedNamesEl.innerHTML = ''; // Clear previous results
        if (!users || users.length === 0) {
            recognizedNamesEl.textContent = 'Ningún usuario reconocido.';
            return;
        }

        const title = document.createElement('h3');
        title.textContent = 'Usuarios Reconocidos:';
        recognizedNamesEl.appendChild(title);

        users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.classList.add('user-card');
            userDiv.innerHTML = `
                <p><strong>Nombre:</strong> ${user.nombre} ${user.apellido}</p>
                <p><strong>DNI:</strong> ${user.dni}</p>
                <p><strong>Email:</strong> ${user.email}</p>
            `;
            recognizedNamesEl.appendChild(userDiv);
        });
    }

    function captureFrame(videoElement) {
        return new Promise(resolve => {
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(blob => resolve(blob), 'image/jpeg');
        });
    }

    async function handleRequest(requestFn) {
        errorEl.classList.add('hidden');
        resultContainer.classList.add('hidden');
        registerFeedback.classList.add('hidden');
        loadingEl.classList.remove('hidden');

        try {
            await requestFn();
        } catch (err) {
            showError(`Error de conexión: ${err.message}`);
        } finally {
            loadingEl.classList.add('hidden');
        }
    }

    function showError(message) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }

    function showFeedback(message, type) {
        registerFeedback.textContent = message;
        registerFeedback.className = `feedback ${type}`;
        registerFeedback.classList.remove('hidden');
    }

    // Initialize
    startCamera();
});