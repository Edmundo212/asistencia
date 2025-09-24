import sys
import os

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import SECRET_KEY, DEBUG
from routes.recognition import recognition_bp

# Serve frontend files by setting the static folder and URL path
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG

# Registrar blueprints for API routes
app.register_blueprint(recognition_bp)

# Route to serve the index.html file
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
