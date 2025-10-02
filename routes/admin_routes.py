from flask import Blueprint, request, jsonify, session, redirect, url_for
from models.face_recognition import KnownFaces
from database.db import db
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from functools import wraps
import numpy as np

admin_bp = Blueprint('admin_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid credentials'}), 401

@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('admin_logged_in', None)
    return jsonify({'message': 'Logout successful'})

# Get all users
@admin_bp.route('/known_faces', methods=['GET'])
@login_required
def get_all_known_faces():
    try:
        users = KnownFaces.query.all()
        users_list = []
        for user in users:
            users_list.append({
                'id': user.id,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'dni': user.dni,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(users_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a user
@admin_bp.route('/known_faces/<int:user_id>', methods=['DELETE'])
@login_required
def delete_known_face(user_id):
    try:
        user = KnownFaces.query.get(user_id)
        if user:
            from models.attendance import Attendance
            Attendance.query.filter_by(user_id=user_id).delete()
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update a user
@admin_bp.route('/known_faces/<int:user_id>', methods=['PUT'])
@login_required
def update_known_face(user_id):
    try:
        user = KnownFaces.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json
        user.nombre = data.get('nombre', user.nombre)
        user.apellido = data.get('apellido', user.apellido)
        user.dni = data.get('dni', user.dni)
        user.email = data.get('email', user.email)
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Add a new user (without image for now)
@admin_bp.route('/known_faces', methods=['POST'])
@login_required
def add_known_face():
    try:
        data = request.json
        # For simplicity, we are not handling face encoding here. 
        # This would require a file upload and processing.
        # We will add a placeholder for the encoding.
        placeholder_encoding = np.zeros(128).tobytes() # Placeholder
        
        new_user = KnownFaces(
            nombre=data['nombre'],
            apellido=data['apellido'],
            dni=data['dni'],
            email=data['email'],
            encoding=placeholder_encoding
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
