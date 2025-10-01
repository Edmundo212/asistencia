import os
import logging
import numpy as np
import face_recognition
from mysql.connector import Error
from database.connection import get_connection
from database.db import db
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnownFaces(db.Model):
    __tablename__ = "known_faces"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    encoding = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<KnownFaces {self.nombre} {self.apellido} - {self.dni}>"

def extract_face_encoding(image_path):
    """Extracts face encoding from an image."""
    try:
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            logger.info(f"Successfully extracted encoding from {image_path}")
            return encodings[0]
        else:
            logger.warning(f"No faces found in {image_path}")
            return None
    except Exception as e:
        logger.error(f"Error extracting encoding from {image_path}: {e}")
        return None

def save_user(nombre, apellido, dni, email, encoding):
    """Saves a new user to the database."""
    try:
        from database.db import db
        user = KnownFaces(nombre=nombre, apellido=apellido, dni=dni, email=email, encoding=encoding.tobytes())
        db.session.add(user)
        db.session.commit()
        logger.info(f"User '{nombre} {apellido}' saved successfully.")
        return True, "User saved successfully."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error saving user '{nombre}': {e}")
        # Check for duplicate entry
        if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
            return False, "DNI o email ya existen en la base de datos."
        return False, str(e)

def recognize_user(image_path):
    """Recognizes a user by comparing with the database."""
    try:
        input_encoding = extract_face_encoding(image_path)
        if input_encoding is None:
            logger.warning(f"Could not get encoding from {image_path}")
            return None

        from database.db import db
        users = KnownFaces.query.all()

        logger.info(f"Comparing with {len(users)} users in the database.")

        for user in users:
            try:
                db_encoding = np.frombuffer(user.encoding, dtype=np.float64)
                if face_recognition.compare_faces([db_encoding], input_encoding)[0]:
                    logger.info(f"User recognized: {user.nombre} {user.apellido}")
                    return {
                        'id': user.id,
                        'nombre': user.nombre,
                        'apellido': user.apellido,
                        'dni': user.dni,
                        'email': user.email
                    }
            except (TypeError, ValueError) as e:
                logger.warning(f"Could not process user {user.id}: {e}")
                continue

        logger.info(f"No match found for {image_path}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error during recognition: {e}")
        return None
