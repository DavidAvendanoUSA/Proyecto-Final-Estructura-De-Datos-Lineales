class Ventanilla:
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        self.libre = True
        self.cliente = None
        self.tiempo_restante = 0

    def asignar(self, cliente, duracion):
        self.cliente = cliente
        self.tiempo_restante = duracion
        self.libre = False

    def procesar_tick(self):
        if not self.libre:
            self.tiempo_restante -= 1
            if self.tiempo_restante <= 0:
                finalizado = self.cliente
                self.cliente = None
                self.libre = True
                return finalizado
        return None