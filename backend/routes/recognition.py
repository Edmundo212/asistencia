from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models.face_recognition import recognize_user
from models.utils import allowed_file, generate_unique_filename
from config import UPLOAD_FOLDER, RESULT_FOLDER, ALLOWED_EXTENSIONS
import os

recognition_bp = Blueprint('recognition', __name__)

@recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400

    # Guardar archivo subido
    filename = generate_unique_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Procesar imagen
    result_filename = "result_" + filename
    result_path = os.path.join(RESULT_FOLDER, result_filename)

    try:
        user = recognize_user(filepath)

        if user:
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Usuario no reconocido'
            }), 404

    except Exception as e:
        return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 500


@recognition_bp.route('/results/<filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)