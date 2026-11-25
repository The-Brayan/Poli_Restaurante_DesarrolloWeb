
import os
import mysql.connector
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        if conexion.is_connected():
            print("Conexión exitosa a PoliRestaurante")
            return conexion

    except mysql.connector.Error as error:
        print("Error al conectar con MySQL:", error)
        return None


# Probar la conexión
if __name__ == "__main__":
    conexion = obtener_conexion()

    if conexion:
        conexion.close()
        print("Conexión cerrada correctamente")
