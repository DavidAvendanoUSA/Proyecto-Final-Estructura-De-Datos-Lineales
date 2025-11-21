"""Helpers para la conexión a la base de datos.

Provee la clase `DatabaseConnection` con el método `get_connection()`.
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


class DatabaseConnection:
    """Encapsula la configuración y creación de conexiones MySQL.

    Lee las variables de entorno `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD` y
    `DB_NAME` al inicializar y expone `get_connection()` para obtener una
    conexión nueva.
    """

    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

    def get_connection(self):
        """Devuelve una nueva conexión `mysql.connector` usando la config.

        Lanza excepciones de `mysql.connector` si la conexión falla.
        """
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )