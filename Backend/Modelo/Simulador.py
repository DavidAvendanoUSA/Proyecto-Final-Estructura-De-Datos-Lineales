import random
from Modelo.Cliente import Cliente
from Tda.Ventanillas import Ventanilla
from Tda.Cola_prioridad import ColaPrioridadGlobal
from Tda.Lista_historial import ListaEnlazadaHistorial

class SimuladorBanco:
    def __init__(self, tiempo_total_ticks, prob_llegada, prob_servicio):

        self.tiempo_total = tiempo_total_ticks
        self.prob_llegada = prob_llegada
        self.prob_servicio = prob_servicio

        self.cola_prioridad = ColaPrioridadGlobal()
        self.historial = ListaEnlazadaHistorial()

        self.ventanillas = [
            Ventanilla('A', 'V_Preferencial'),
            Ventanilla('M', 'V_Intermedia'),
            Ventanilla('B', 'V_Regular'),
        ]

        self.stats = {
            'A': {'llegaron': 0, 'atendidos': 0, 'no_atendidos': 0},
            'M': {'llegaron': 0, 'atendidos': 0, 'no_atendidos': 0},
            'B': {'llegaron': 0, 'atendidos': 0, 'no_atendidos': 0}
        }

        self.next_id = 1
        self.logs = []

    # ------------------------
    # LLEGADAS
    # ------------------------
    def generar_llegadas(self, t):
        for tipo, p in self.prob_llegada.items():
            if random.random() < p:
                cid = f"C{self.next_id}"
                self.next_id += 1
                c = Cliente(cid, tipo, t)
                self.cola_prioridad.encolar(c)
                self.stats[tipo]['llegaron'] += 1
                self.logs.append({
                    'tick': t,
                    'event': 'llegada',
                    'cliente': {'id': c.id, 'tipo': c.tipo, 'llegada': c.tiempo_llegada}
                })

    # ------------------------
    # TIEMPO DE SERVICIO
    # ------------------------
    def sample_service_duration(self, tipo):
        p = self.prob_servicio[tipo]
        trials = 1
        while random.random() > p:
            trials += 1
        return trials

    # ------------------------
    # ASIGNAR A VENTANILLAS
    # ------------------------
    def asignar_ventanillas(self, t):
        for v in self.ventanillas:
            if v.libre:
                cliente = self.cola_prioridad.extraer_siguiente_de_tipo(v.tipo)
                if cliente:
                    dur = self.sample_service_duration(v.tipo)
                    cliente.tiempo_inicio_atencion = t
                    v.asignar(cliente, dur)
                    self.logs.append({
                        'tick': t,
                        'event': 'asignacion',
                        'ventanilla': {'nombre': v.nombre, 'tipo': v.tipo},
                        'cliente': {'id': cliente.id, 'tipo': cliente.tipo},
                        'duracion': dur
                    })

    # ------------------------
    # PROCESAR VENTANILLAS
    # ------------------------
    def procesar_ventanillas(self, t):
        for v in self.ventanillas:
            finalizado = v.procesar_tick()
            if finalizado:
                finalizado.tiempo_fin_atencion = t
                self.historial.insertar_final(finalizado)
                self.stats[finalizado.tipo]['atendidos'] += 1
                self.logs.append({
                    'tick': t,
                    'event': 'finalizacion',
                    'cliente': {'id': finalizado.id, 'tipo': finalizado.tipo},
                    'inicio': finalizado.tiempo_inicio_atencion,
                    'fin': finalizado.tiempo_fin_atencion
                })

    # ------------------------
    # EJECUTAR SIMULACIÓN
    # ------------------------
    def run(self):
        # simulación en memoria: eventos registrados en self.logs (sin imprimir)

        for t in range(self.tiempo_total):
            self.generar_llegadas(t)
            self.asignar_ventanillas(t)
            self.procesar_ventanillas(t)

        # NO ATENDIDOS
        restantes = self.cola_prioridad._lista
        for _, _, c in restantes:
            self.stats[c.tipo]['no_atendidos'] += 1

        for v in self.ventanillas:
            if not v.libre:
                self.stats[v.tipo]['no_atendidos'] += 1

        return {
            'estadisticas': self.stats,
            'historial': self.historial.to_list(),
            'cola_prioridad': self.cola_prioridad.ver_lista(),
            'logs': self.logs,
        }
