import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# Configuración de conexión a MySQL
usuario = os.getenv("DB_USER")
contrasena = quote_plus(os.getenv("DB_PASSWORD", ""))
host = os.getenv("DB_HOST", "localhost")
puerto = os.getenv("DB_PORT", "3306")
base_datos = os.getenv("DB_NAME", "polirestaurante")

URL_BD = (
    f"mysql+mysqlconnector://{usuario}:{contrasena}"
    f"@{host}:{puerto}/{base_datos}"
)

# Motor de conexión SQLAlchemy
motor = create_engine(URL_BD, pool_pre_ping=True)

# Sesiones para realizar operaciones CRUD
SesionLocal = sessionmaker(bind=motor)


# Clase base para los modelos ORM
class Base(DeclarativeBase):
    pass


# Prueba de conexión
if __name__ == "__main__":
    from sqlalchemy import text

    with motor.connect() as conexion:
        resultado = conexion.execute(text("SELECT DATABASE()"))
        print("ORM conectado correctamente a:", resultado.scalar())