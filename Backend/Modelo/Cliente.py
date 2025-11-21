class Cliente:
    def __init__(self, id_cliente, tipo, tiempo_llegada):
        self.id = id_cliente
        self.tipo = tipo  # 'A' preferencial, 'M' intermedia, 'B' regular
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_inicio_atencion = None
        self.tiempo_fin_atencion = None

    def __str__(self):
        tipo_nombre = {'A': 'Preferencial', 'M': 'Intermedio', 'B': 'Regular'}
        return f"{self.id} ({tipo_nombre[self.tipo]}) - Llego en t={self.tiempo_llegada}"
