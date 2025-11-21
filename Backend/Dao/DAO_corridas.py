from config.db import DatabaseConnection

class DAOCorridas:
    def __init__(self, DatabaseConnection):
        self.db_connection = DatabaseConnection

    # -------------------------------
    # CREATE
    # -------------------------------
    def crear_corrida(self, tiempo: int):
        query = "INSERT INTO corridas (tiempo) VALUES (%s)"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (tiempo,))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("Error al crear corrida:", e)
            return None
        finally:
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
            cursor.close()
