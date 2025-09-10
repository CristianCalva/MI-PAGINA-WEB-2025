import os
from MySQLdb import OperationalError
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def get_mysql_engine():
    # Credenciales para la conexión a la base de datos
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    database = os.getenv('MYSQL_DATABASE', 'urbanwalk_db')
    
    # Crear la cadena de conexión
    connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_string, echo=True)
    return engine

from sqlalchemy import text

def test_connection():
    engine = get_mysql_engine()
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION();"))
            version = result.fetchone()
            return f"Conexión exitosa a MySQL: {version[0]}"
    except OperationalError as e:
        return f"Error de conexión a MySQL: {str(e)}"
