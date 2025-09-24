#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a la base de datos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import test_connection, get_connection
from mysql.connector import Error

def main():
    print("=== Prueba de Conexión a Base de Datos ===")

    # Probar conexión básica
    print("\n1. Probando conexión básica...")
    if test_connection():
        print("✓ Conexión básica exitosa")
    else:
        print("✗ Error en conexión básica")
        return False

    # Probar operaciones CRUD básicas
    print("\n2. Probando operaciones CRUD...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Probar INSERT
        print("   - Probando INSERT...")
        cursor.execute("INSERT INTO known_faces (name, encoding) VALUES (%s, %s)",
                      ("test_user", b"test_encoding"))
        conn.commit()
        print("   ✓ INSERT exitoso")

        # Probar SELECT
        print("   - Probando SELECT...")
        cursor.execute("SELECT * FROM known_faces WHERE name = %s", ("test_user",))
        result = cursor.fetchone()
        if result:
            print("   ✓ SELECT exitoso")
        else:
            print("   ✗ Error en SELECT")
            return False

        # Probar DELETE (limpiar datos de prueba)
        print("   - Probando DELETE...")
        cursor.execute("DELETE FROM known_faces WHERE name = %s", ("test_user",))
        conn.commit()
        print("   ✓ DELETE exitoso")

        conn.close()
        print("✓ Todas las operaciones CRUD exitosas")

    except Error as e:
        print(f"✗ Error en operaciones CRUD: {e}")
        return False

    print("\n=== Prueba Completada Exitosamente ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
