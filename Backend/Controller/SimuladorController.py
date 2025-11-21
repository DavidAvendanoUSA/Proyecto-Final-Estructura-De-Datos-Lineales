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
        self.last_corrida_id = None

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

            # Crear registro de corrida en BD al inicio para devolver id inmediato
            try:
                corrida_id = self.dao_corridas.crear_corrida(self.simulador.tiempo_total)
                self.last_corrida_id = corrida_id
            except Exception as e:
                print("Error creating corrida at start:", e)

            self._thread = threading.Thread(target=self._run_and_persist, daemon=True)
            self._thread.start()
            return True

    def _run_and_persist(self):
        """Ejecuta la simulación (bloqueante) y persiste resultados al terminar."""
        resultado = self.simulador.run()
        # Usar el corrida_id creado al iniciar la simulación (si existe)
        corrida_id = getattr(self, 'last_corrida_id', None)
        if corrida_id is None:
            print("Aviso: corrida_id es None; los inserts en 'colas' pueden fallar")

        # Guardar estadísticas de colas por ventanilla (si se pudo crear corrida)
        stats = resultado.get('estadisticas', {})
        for tipo, dato in stats.items():
            # nombre_id usará el tipo de ventanilla (A/M/B) para ajustarse a la DB
            nombre_id = tipo
            lleg = dato.get('llegaron', 0)
            atend = dato.get('atendidos', 0)
            no_att = dato.get('no_atendidos', 0)
            try:
                # Si no hay corrida_id, pasamos None (DAO deberá manejarlo o fallar)
                self.dao_colas.crear_cola(corrida_id, nombre_id, lleg, atend, no_att)
            except Exception as e:
                print("Error guardando estadistica en colas:", e)

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
