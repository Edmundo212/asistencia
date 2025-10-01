from flask import Flask, send_from_directory
from flask_cors import CORS
from config import SECRET_KEY, DEBUG
from routes.recognition import recognition_bp
from database.db import db
from models.attendance import Attendance
from models.face_recognition import KnownFaces

# Serve frontend files by setting the static folder and URL path
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/reconocimiento'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registrar blueprints for API routes
from routes.attendance_routes import attendance_bp

app.register_blueprint(recognition_bp)
app.register_blueprint(attendance_bp, url_prefix="/api")

# Route to serve the index.html file
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
