import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import face_recognition
import numpy as np
from database.connection import get_connection
from mysql.connector import Error

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_face_encoding(image_path):
    """
    Extrae el encoding facial de una imagen.

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        np.array or None: Encoding facial o None si no se encuentra
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"Imagen no encontrada: {image_path}")
            return None

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            logger.info(f"Encoding facial extraído exitosamente de {image_path}")
            return encodings[0]
        else:
            logger.warning(f"No se encontraron rostros en la imagen: {image_path}")
            return None

    except Exception as e:
        logger.error(f"Error extrayendo encoding facial de {image_path}: {e}")
        return None

def save_user(name, encoding):
    """
    Guarda un usuario en la base de datos.

    Args:
        name (str): Nombre del usuario
        encoding (np.array): Encoding facial

    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO known_faces (name, encoding) VALUES (%s, %s)",
            (name, encoding.tobytes())
        )
        conn.commit()
        logger.info(f"Usuario '{name}' guardado exitosamente en la base de datos")
        conn.close()
        return True

    except Error as e:
        logger.error(f"Error guardando usuario '{name}' en la base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado guardando usuario '{name}': {e}")
        return False

def recognize_user(image_path):
    """
    Reconoce un usuario comparando con la base de datos.

    Args:
        image_path (str): Ruta a la imagen a reconocer

    Returns:
        dict or None: Información del usuario reconocido o None
    """
    try:
        if not os.path.exists(image_path):
            logger.error(f"Imagen no encontrada: {image_path}")
            return None

        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            logger.warning(f"No se encontraron rostros en la imagen: {image_path}")
            return None

        input_encoding = encodings[0]
        logger.info(f"Procesando reconocimiento para {image_path}")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, encoding FROM known_faces")
        users = cursor.fetchall()
        conn.close()

        logger.info(f"Comparando con {len(users)} usuarios en la base de datos")

        for user in users:
            try:
                db_encoding = np.frombuffer(user["encoding"], dtype=np.float64)
                matches = face_recognition.compare_faces([db_encoding], input_encoding)
                if matches[0]:
                    logger.info(f"Usuario reconocido: {user['name']} (ID: {user['id']})")
                    return {"id": user["id"], "name": user["name"]}
            except Exception as e:
                logger.warning(f"Error comparando con usuario {user['name']}: {e}")
                continue

        logger.info(f"No se encontró coincidencia para {image_path}")
        return None

    except Error as e:
        logger.error(f"Error de base de datos en reconocimiento: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en reconocimiento: {e}")
        return None
