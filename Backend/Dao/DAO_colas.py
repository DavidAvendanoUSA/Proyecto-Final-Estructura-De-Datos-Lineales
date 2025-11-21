"""DAO para la tabla `colas`.

Proporciona operaciones CRUD simples y recibe una instancia de
`config.db.DatabaseConnection` en el constructor.
"""

from config.db import DatabaseConnection
import mysql.connector


class DAOColas:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    # ---------------------------
    # CREATE
    # ---------------------------
    def crear_cola(self, corrida_id, nombre_id, n_entrada, n_atendidos, n_no_atendidos):
        """Inserta una fila en la tabla `colas` según `config/db.sql`.

        La tabla espera los campos: (corrida_id, nombre_id, n_entrada,
        n_atendidos, n_no_atendidos).
        """
        query = """
        INSERT INTO colas (corrida_id, nombre_id, n_entrada, n_atendidos, n_no_atendidos)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (corrida_id, nombre_id, n_entrada, n_atendidos, n_no_atendidos))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as e:
            print("Error al crear cola (DB):", e)
            return None
        except Exception as e:
            print("Error inesperado al crear cola:", e)
            return None
        finally:
            if 'cursor' in locals() and cursor:
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
        except mysql.connector.Error as e:
            print("Error al obtener cola (DB):", e)
            return None
        except Exception as e:
            print("Error inesperado al obtener cola:", e)
            return None
        finally:
            if 'cursor' in locals() and cursor:
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
        except mysql.connector.Error as e:
            print("Error al obtener colas (DB):", e)
            return []
        except Exception as e:
            print("Error inesperado al obtener colas:", e)
            return []
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    # ---------------------------
    # UPDATE
    # ---------------------------
    def actualizar_cola(self, cola_id, nombre, n_entrada, n_atendidos, n_no_atendido):
        query = """
        UPDATE colas
        SET nombre_id = %s,
            n_entrada = %s,
            n_atendidos = %s,
            n_no_atendidos = %s
        WHERE id = %s
        """
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (nombre, n_entrada, n_atendidos, n_no_atendido, cola_id))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as e:
            print("Error al actualizar cola (DB):", e)
            return False
        except Exception as e:
            print("Error inesperado al actualizar cola:", e)
            return False
        finally:
            if 'cursor' in locals() and cursor:
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
        except mysql.connector.Error as e:
            print("Error al eliminar cola (DB):", e)
            return False
        except Exception as e:
            print("Error inesperado al eliminar cola:", e)
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

# ---------------------------
# EJEMPLO DE USO
# ---------------------------
if __name__ == "__main__":
    # Crear instancia de la conexión
    db_conn = DatabaseConnection()  # Ajusta si requiere host, usuario, password, database
    dao = DAOColas(db_conn)

    # --- CREATE ---
    print("Creando corrida de ejemplo y cola...")
    from Dao.DAO_corridas import DAOCorridas
    dao_corr = DAOCorridas(db_conn)
    corrida_id = dao_corr.crear_corrida(0)
    cola_id = dao.crear_cola(corrida_id, "A", 10, 5, 2)
    print("ID creada:", cola_id)

    # --- READ (uno) ---
    print("Obteniendo cola creada...")
    cola = dao.obtener_cola(cola_id)
    print(cola)

    # --- READ (todos) ---
    print("Obteniendo todas las colas...")
    todas = dao.obtener_todas()
    print(todas)

    # --- UPDATE ---
    print("Actualizando cola...")
    exito = dao.actualizar_cola(cola_id, "Cola1 Actualizada", 12, 6, 3)
    print("Actualización exitosa:", exito)
    print("Cola actualizada:", dao.obtener_cola(cola_id))

    # --- DELETE ---
    print("Eliminando cola...")
    exito = dao.eliminar_cola(cola_id)
    print("Eliminación exitosa:", exito)
    print("Cola después de eliminar:", dao.obtener_cola(cola_id))
