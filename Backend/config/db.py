import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    
    def conectar_db():
        conexion = mysql.connector.connect(
            host= os.getenv("DB_HOST"),
            user= os.getenv("DB_USERNAME"),
            password= os.getenv("DB_PASSWORD"),
            database= os.getenv("DB_NAME")
        )
        return conexion