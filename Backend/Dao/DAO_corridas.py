"""DAO para operaciones sobre la tabla `corridas`.

Expone `DAOCorridas` que recibe una instancia de
`config.db.DatabaseConnection` y realiza operaciones CRUD.
"""

from config.db import DatabaseConnection


class DAOCorridas:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    # -------------------------------
    # CREATE
    # -------------------------------
    def crear_corrida(self, tiempo: int):
        # La tabla `corridas` en db.sql define `tiempo` como DATETIME.
        # Para evitar errores de tipo, guardamos la fecha/hora actual con NOW().
        query = "INSERT INTO corridas (tiempo) VALUES (NOW())"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            # Devolver None y propagar impresión para facilitar debugging
            print("Error al crear corrida:", e)
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    # -------------------------------
    # READ (uno)
    # -------------------------------
    def obtener_corrida(self, corrida_id: int):
        query = "SELECT * FROM corridas WHERE id = %s"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (corrida_id,))
            return cursor.fetchone()
        except Exception as e:
            print("Error al obtener corrida:", e)
            return None
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    # -------------------------------
    # READ (todos)
    # -------------------------------
    def obtener_todas(self):
        query = "SELECT * FROM corridas"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Error al obtener corridas:", e)
            return []
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    # -------------------------------
    # UPDATE
    # -------------------------------
    def actualizar_corrida(self, corrida_id: int, nuevo_tiempo: int):
        query = "UPDATE corridas SET tiempo = %s WHERE id = %s"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (nuevo_tiempo, corrida_id))
            conn.commit()
            return cursor.rowcount > 0  # True si actualizó
        except Exception as e:
            print("Error al actualizar corrida:", e)
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    # -------------------------------
    # DELETE
    # -------------------------------
    def eliminar_corrida(self, corrida_id: int):
        query = "DELETE FROM corridas WHERE id = %s"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (corrida_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("Error al eliminar corrida:", e)
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
