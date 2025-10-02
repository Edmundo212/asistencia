document.addEventListener('DOMContentLoaded', () => {
    // Tabs
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

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

    // Admin
    const adminSection = document.getElementById('admin-section');
    const adminLogin = document.getElementById('admin-login');
    const adminPanel = document.getElementById('admin-panel');
    const adminUsername = document.getElementById('admin-username');
    const adminPassword = document.getElementById('admin-password');
    const adminLoginBtn = document.getElementById('admin-login-btn');
    const adminLogoutBtn = document.getElementById('admin-logout-btn');
    const loginFeedback = document.getElementById('login-feedback');
    const usersTableBody = document.querySelector('#users-table tbody');
    const addUserBtn = document.getElementById('add-user-btn');
    const refreshUsersBtn = document.getElementById('refresh-users-btn');
    const userModal = document.getElementById('user-modal');
    const modalTitle = document.getElementById('modal-title');
    const userForm = document.getElementById('user-form');
    const userIdInput = document.getElementById('user-id');
    const modalNombreInput = document.getElementById('modal-nombre');
    const modalApellidoInput = document.getElementById('modal-apellido');
    const modalDniInput = document.getElementById('modal-dni');
    const modalEmailInput = document.getElementById('modal-email');
    const closeModalBtn = document.querySelector('.close-btn');


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
            showError(`No se pudo acceder a la cámara: ${err.message}`);
        }
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            const targetId = tab.id.replace('tab-', '') + '-section';
            const target = document.getElementById(targetId);
            if (target) {
                target.classList.add('active');
            }

            if (targetId === 'admin-section') {
                checkAdminLogin();
            }
        });
    });

    captureBtn.addEventListener('click', () => {
        handleRequest(async () => {
            const blob = await captureFrame(videoRecognize);
            const formData = new FormData();
            formData.append('image', blob, 'capture.jpg');

            const response = await fetch('/recognize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                faceCountEl.textContent = `Rostros detectados: ${data.face_count}`;
                displayRecognizedUsers(data.recognized_users);
                resultImage.src = window.location.origin + data.result_image_url;
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

            const response = await fetch('/register', {
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
        registerFeedback.className = 'feedback'; // Reset classes
        registerFeedback.classList.add(type);
        registerFeedback.classList.remove('hidden');
    }

    // Admin Panel Logic
    async function checkAdminLogin() {
        try {
            const response = await fetch('/api/admin/known_faces', { credentials: 'include' });
            if (response.ok) {
                const users = await response.json();
                adminLogin.classList.add('hidden');
                adminPanel.classList.remove('hidden');
                renderUsersTable(users);
            } else if (response.status === 401) {
                adminPanel.classList.add('hidden');
                adminLogin.classList.remove('hidden');
            } else {
                showError('Error al verificar sesión.');
            }
        } catch (error) {
            showError('Error de conexión al verificar sesión.');
        }
    }

    async function fetchUsers() {
        try {
            const response = await fetch('/api/admin/known_faces', { credentials: 'include' });
            const users = await response.json();
            renderUsersTable(users);
        } catch (error) {
            showError('Error al cargar los usuarios.');
        }
    }

    function renderUsersTable(users) {
        usersTableBody.innerHTML = '';
        if (!users || users.length === 0) {
            usersTableBody.innerHTML = '<tr><td colspan="7">No hay usuarios registrados.</td></tr>';
            return;
        }

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.nombre}</td>
                <td>${user.apellido}</td>
                <td>${user.dni}</td>
                <td>${user.email}</td>
                <td>${user.created_at}</td>
                <td>
                    <button class="action-btn edit-btn" data-id="${user.id}">Editar</button>
                    <button class="action-btn delete-btn" data-id="${user.id}">Eliminar</button>
                </td>
            `;
            usersTableBody.appendChild(row);
        });
    }

    function openUserModal(user = null) {
        userForm.reset();
        if (user) {
            modalTitle.textContent = 'Editar Usuario';
            userIdInput.value = user.id;
            modalNombreInput.value = user.nombre;
            modalApellidoInput.value = user.apellido;
            modalDniInput.value = user.dni;
            modalEmailInput.value = user.email;
        } else {
            modalTitle.textContent = 'Añadir Usuario';
            userIdInput.value = '';
        }
        userModal.classList.remove('hidden');
    }

    function closeUserModal() {
        userModal.classList.add('hidden');
    }

    async function handleFormSubmit(event) {
        event.preventDefault();
        const userId = userIdInput.value;
        const userData = {
            nombre: modalNombreInput.value,
            apellido: modalApellidoInput.value,
            dni: modalDniInput.value,
            email: modalEmailInput.value,
        };

        const url = userId ? `/api/admin/known_faces/${userId}` : '/api/admin/known_faces';
        const method = userId ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
                credentials: 'include',
            });

            if (response.ok) {
                closeUserModal();
                fetchUsers();
            } else {
                const errorData = await response.json();
                showError(errorData.error || 'Error al guardar el usuario.');
            }
        } catch (error) {
            showError('Error de conexión al guardar el usuario.');
        }
    }

    async function deleteUser(userId) {
        if (!confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/known_faces/${userId}`, {
                method: 'DELETE',
                credentials: 'include',
            });

            if (response.ok) {
                fetchUsers();
            } else {
                const errorData = await response.json();
                showError(errorData.error || 'Error al eliminar el usuario.');
            }
        } catch (error) {
            showError('Error de conexión al eliminar el usuario.');
        }
    }
    
    addUserBtn.addEventListener('click', () => openUserModal());
    refreshUsersBtn.addEventListener('click', fetchUsers);
    closeModalBtn.addEventListener('click', closeUserModal);
    userForm.addEventListener('submit', handleFormSubmit);

    usersTableBody.addEventListener('click', (event) => {
        const target = event.target;
        const userId = target.dataset.id;

        if (target.classList.contains('edit-btn')) {
            // Find the user data to pre-fill the form
            fetch(`/api/admin/known_faces`, { credentials: 'include' })
                .then(res => res.json())
                .then(users => {
                    const user = users.find(u => u.id == userId);
                    if(user) openUserModal(user);
                });
        }

        if (target.classList.contains('delete-btn')) {
            deleteUser(userId);
        }
    });

    window.addEventListener('click', (event) => {
        if (event.target === userModal) {
            closeUserModal();
        }
    });


    // Admin login logic
    adminLoginBtn.addEventListener('click', async () => {
        const username = adminUsername.value.trim();
        const password = adminPassword.value.trim();

        if (!username || !password) {
            loginFeedback.textContent = 'Por favor ingrese usuario y contraseña.';
            loginFeedback.classList.remove('hidden');
            return;
        }

        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'include',
            });

            if (response.ok) {
                loginFeedback.classList.add('hidden');
                adminLogin.classList.add('hidden');
                adminPanel.classList.remove('hidden');
                fetchUsers();
            } else {
                const errorData = await response.json();
                loginFeedback.textContent = errorData.error || 'Error en el inicio de sesión.';
                loginFeedback.classList.remove('hidden');
            }
        } catch (error) {
            loginFeedback.textContent = 'Error de conexión al iniciar sesión.';
            loginFeedback.classList.remove('hidden');
        }
    });

    // Admin logout logic
    adminLogoutBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/admin/logout', {
                method: 'POST',
                credentials: 'include',
            });

            if (response.ok) {
                adminPanel.classList.add('hidden');
                adminLogin.classList.remove('hidden');
                adminUsername.value = '';
                adminPassword.value = '';
                usersTableBody.innerHTML = '';
            } else {
                showError('Error al cerrar sesión.');
            }
        } catch (error) {
            showError('Error de conexión al cerrar sesión.');
        }
    });

    // Initialize
    startCamera();
});
