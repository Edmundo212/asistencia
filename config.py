import os

# Rutas
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
RESULT_FOLDER = os.path.join(os.getcwd(), 'static', 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Configuración Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Credenciales de administrador (única cuenta)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'Edgar Jhon')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '12345')
