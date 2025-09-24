from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import os

from models.utils import allowed_file, generate_unique_filename
from models.face_recognition import extract_face_encoding, save_user
from config import UPLOAD_FOLDER, RESULT_FOLDER
from database.connection import get_connection

recognition_bp = Blueprint('recognition', __name__)

def get_known_users():
    """Fetches all known user data and encodings from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, dni, email, encoding FROM known_faces")
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            try:
                user['encoding'] = np.frombuffer(user["encoding"], dtype=np.float64)
            except (ValueError, TypeError):
                user['encoding'] = None # Mark as invalid
        
        # Filter out users with invalid encodings
        return [u for u in users if u['encoding'] is not None]
    except Exception as e:
        print(f"Error getting known users: {e}")
        return []

@recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file'}), 400

    filename = generate_unique_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        uploaded_image = face_recognition.load_image_file(upload_path)
        face_locations = face_recognition.face_locations(uploaded_image)
        face_encodings = face_recognition.face_encodings(uploaded_image, face_locations)

        known_users = get_known_users()
        known_face_encodings = [user['encoding'] for user in known_users]

        pil_image = Image.fromarray(uploaded_image)
        draw = ImageDraw.Draw(pil_image)

        recognized_users = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Desconocido"
            user_info = None

            if True in matches:
                first_match_index = matches.index(True)
                matched_user = known_users[first_match_index]
                name = f"{matched_user['nombre']} {matched_user['apellido']}"
                user_info = matched_user.copy()
                user_info.pop('encoding', None) # Don't send encoding to frontend
                recognized_users.append(user_info)

            # Draw rectangles and labels
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0), width=2)
            text_bbox = draw.textbbox((left, bottom), name)
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        del draw

        result_filename = "result_" + filename
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        pil_image.save(result_path)

        result_image_url = f'/results/{result_filename}'

        return jsonify({
            'success': True,
            'face_count': len(face_locations),
            'recognized_users': recognized_users,
            'result_image_url': result_image_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing image: {str(e)}'}), 500
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)

@recognition_bp.route('/register', methods=['POST'])
def register_user():
    form_data = request.form
    required_fields = ['nombre', 'apellido', 'dni', 'email']
    if 'image' not in request.files or not all(field in form_data for field in required_fields):
        return jsonify({'success': False, 'error': 'Faltan datos en el formulario'}), 400

    file = request.files['image']
    nombre = form_data['nombre']
    apellido = form_data['apellido']
    dni = form_data['dni']
    email = form_data['email']

    if file.filename == '' or not all([nombre, apellido, dni, email]):
        return jsonify({'success': False, 'error': 'Todos los campos son obligatorios'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400

    filename = generate_unique_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        encoding = extract_face_encoding(upload_path)
        if encoding is None:
            return jsonify({'success': False, 'error': 'No se encontró un rostro en la imagen o la imagen no es clara'}), 400

        success, message = save_user(nombre, apellido, dni, email, encoding)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': message}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error procesando la imagen: {str(e)}'}), 500
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)

@recognition_bp.route('/results/<filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)
