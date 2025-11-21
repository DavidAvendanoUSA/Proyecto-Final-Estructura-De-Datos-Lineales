import threading
from Modelo.Simulador import SimuladorBanco
from Dao.DAO_colas import DAOColas
from Dao.DAO_corridas import DAOCorridas


class SimuladorController:
    """Controller para gestionar ciclos de simulación usando el modelo y DAOs.

    Métodos públicos:
    - correr(): inicia la simulación en un hilo fondo (no bloqueante).
    - pausar(): pausa la simulación (usa el método del modelo).
    - reanudar(): reanuda la simulación.
    - detener(): detiene la simulación.
    - restaurar_parametros(): restaura parámetros iniciales en el simulador.
    """

    def __init__(self, tiempo_total_ticks, prob_llegada, prob_servicio,
                 dao_colas: DAOColas, dao_corridas: DAOCorridas):
        """Inicializa el controller recibiendo instancias de DAO.

        Este controller NO crea ni conoce la conexión a BD. Las instancias
        de `DAOColas` y `DAOCorridas` deben ser creadas fuera y pasadas aquí.
        """
        if dao_colas is None or dao_corridas is None:
            raise ValueError("dao_colas y dao_corridas son requeridos")

        self.dao_colas = dao_colas
        self.dao_corridas = dao_corridas

        self.simulador = SimuladorBanco(tiempo_total_ticks, prob_llegada, prob_servicio)

        self._thread = None
        self._lock = threading.Lock()

    # -----------------------
    # Control de ejecución
    # -----------------------
    def correr(self):
        """Inicia la simulación en segundo plano. Devuelve True si arrancó.

        Si ya hay una corrida en ejecución, no hace nada y devuelve False.
        """
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False

            self._thread = threading.Thread(target=self._run_and_persist, daemon=True)
            self._thread.start()
            return True

    def _run_and_persist(self):
        """Ejecuta la simulación (bloqueante) y persiste resultados al terminar."""
        resultado = self.simulador.run()

        # Guardar corrida (solo el tiempo total como ejemplo)
        try:
            tiempo = self.simulador.tiempo_total
            corrida_id = self.dao_corridas.crear_corrida(tiempo)
        except Exception as e:
            corrida_id = None

        # Guardar estadísticas de colas por ventanilla
        try:
            stats = resultado.get('estadisticas', {})
            # Cada entrada en stats es por tipo 'A','M','B'
            for tipo, dato in stats.items():
                # Buscar el nombre de la ventanilla correspondiente
                nombre = None
                for v in self.simulador.ventanillas:
                    if v.tipo == tipo:
                        nombre = v.nombre
                        break

                nombre = nombre or f"V_{tipo}"
                lleg = dato.get('llegaron', 0)
                atend = dato.get('atendidos', 0)
                no_att = dato.get('no_atendidos', 0)
                try:
                    self.dao_colas.crear_cola(nombre, lleg, atend, no_att)
                except Exception:
                    # no detener el flujo por errores de BD
                    pass
        except Exception:
            pass

    def pausar(self):
        self.simulador.pausar()

    def reanudar(self):
        self.simulador.reanudar()

    def detener(self):
        self.simulador.detener_simulacion()

    def restaurar_parametros(self):
        self.simulador.restaurar_parametros()

    # -----------------------
    # Auxiliares
    # -----------------------
    def is_running(self):
        return bool(self._thread and self._thread.is_alive())
