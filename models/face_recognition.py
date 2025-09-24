import os
import logging
import numpy as np
import face_recognition
from mysql.connector import Error
from database.connection import get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO known_faces (nombre, apellido, dni, email, encoding) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nombre, apellido, dni, email, encoding.tobytes()))
        conn.commit()
        logger.info(f"User '{nombre} {apellido}' saved successfully.")
        conn.close()
        return True, "User saved successfully."
    except Error as e:
        logger.error(f"Database error saving user '{nombre}': {e}")
        # Check for duplicate entry
        if e.errno == 1062: # Duplicate entry
            return False, "DNI o email ya existen en la base de datos."
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error saving user '{nombre}': {e}")
        return False, str(e)

def recognize_user(image_path):
    """Recognizes a user by comparing with the database."""
    try:
        input_encoding = extract_face_encoding(image_path)
        if input_encoding is None:
            logger.warning(f"Could not get encoding from {image_path}")
            return None

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, dni, email, encoding FROM known_faces")
        users = cursor.fetchall()
        conn.close()

        logger.info(f"Comparing with {len(users)} users in the database.")

        for user in users:
            try:
                db_encoding = np.frombuffer(user["encoding"], dtype=np.float64)
                if face_recognition.compare_faces([db_encoding], input_encoding)[0]:
                    logger.info(f"User recognized: {user['nombre']} {user['apellido']}")
                    # Don't return the encoding itself
                    user.pop('encoding', None)
                    return user
            except (TypeError, ValueError) as e:
                logger.warning(f"Could not process user {user['id']}: {e}")
                continue

        logger.info(f"No match found for {image_path}")
        return None

    except Error as e:
        logger.error(f"Database error during recognition: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during recognition: {e}")
        return None