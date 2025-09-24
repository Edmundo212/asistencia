import mysql.connector
import os
import logging
import time
from mysql.connector import Error

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection(max_retries=3, retry_delay=1):
    """
    Obtiene una conexión a la base de datos con reintentos.

    Args:
        max_retries (int): Número máximo de reintentos
        retry_delay (int): Tiempo de espera entre reintentos en segundos

    Returns:
        mysql.connector.connection: Conexión a la base de datos

    Raises:
        Error: Si no se puede conectar después de los reintentos
    """
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="reconocimiento",
                port=3306
            )
            logger.info("Conexión a la base de datos establecida exitosamente.")
            return conn
        except Error as e:
            logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                logger.error("No se pudo conectar a la base de datos después de varios intentos.")
                raise e

def test_connection():
    """
    Prueba la conexión a la base de datos.

    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        conn = get_connection()
        conn.close()
        logger.info("Prueba de conexión exitosa.")
        return True
    except Error as e:
        logger.error(f"Prueba de conexión fallida: {e}")
        return False

def init_db():
    """
    Inicializa la base de datos creando las tablas necesarias.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener la ruta al archivo schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        if not os.path.exists(schema_path):
            logger.error(f"Archivo schema.sql no encontrado en {schema_path}")
            return

        with open(schema_path, 'r', encoding='utf-8') as f:
            # Separar y ejecutar cada comando SQL
            commands = f.read().split(';')
            for command in commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        logger.info(f"Comando SQL ejecutado: {command.strip()[:50]}...")
                    except Error as e:
                        logger.warning(f"Error ejecutando comando SQL: {e}")

        conn.commit()
        logger.info("Base de datos inicializada con éxito.")
        conn.close()

    except Error as e:
        logger.error(f"Error inicializando la base de datos: {e}")
        raise e

if __name__ == '__main__':
    # Probar conexión primero
    if test_connection():
        init_db()
    else:
        logger.error("No se puede inicializar la base de datos sin conexión.")
