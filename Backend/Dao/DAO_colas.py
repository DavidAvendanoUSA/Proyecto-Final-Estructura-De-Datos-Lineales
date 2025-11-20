from config.db import DatabaseConnection

class DAOColas:
    def __init__(self, DatabaseConnection):
        self.db_connection = DatabaseConnection

    # ---------------------------
    # CREATE
    # ---------------------------
    def crear_cola(self, nombre, n_entrada, n_atendidos, n_no_atendido):
        query = """
        INSERT INTO colas (Nombre, N_entrada, N_atendidos, N_no_atendido)
        VALUES (%s, %s, %s, %s)
        """
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (nombre, n_entrada, n_atendidos, n_no_atendido))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print("Error al crear cola:", e)
            return None
        finally:
            cursor.close()

    # ---------------------------
    # READ - Uno
    # ---------------------------
    def obtener_cola(self, cola_id):
        query = "SELECT * FROM colas WHERE id = %s"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (cola_id,))
            return cursor.fetchone()
        except Exception as e:
            print("Error al obtener cola:", e)
            return None
        finally:
            cursor.close()

    # ---------------------------
    # READ - Todos
    # ---------------------------
    def obtener_todas(self):
        query = "SELECT * FROM colas"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("Error al obtener colas:", e)
            return []
        finally:
            cursor.close()

    # ---------------------------
    # UPDATE
    # ---------------------------
    def actualizar_cola(self, cola_id, nombre, n_entrada, n_atendidos, n_no_atendido):
        query = """
        UPDATE colas
        SET Nombre = %s,
            N_entrada = %s,
            N_atendidos = %s,
            N_no_atendido = %s
        WHERE id = %s
        """
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (nombre, n_entrada, n_atendidos, n_no_atendido, cola_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("Error al actualizar cola:", e)
            return False
        finally:
            cursor.close()

    # ---------------------------
    # DELETE
    # ---------------------------
    def eliminar_cola(self, cola_id):
        query = "DELETE FROM colas WHERE id = %s"
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (cola_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print("Error al eliminar cola:", e)
            return False
        finally:
            cursor.close()
