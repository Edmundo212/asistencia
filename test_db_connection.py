from database.connection import test_connection

if __name__ == "__main__":
    if test_connection():
        print("Conexión a la base de datos exitosa.")
    else:
        print("Error al conectar a la base de datos.")
