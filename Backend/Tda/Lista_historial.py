from Tda.Nodo import Nodo

class ListaEnlazadaHistorial:
    def __init__(self):
        self.cabeza = None

    def insertar_final(self, cliente):
        nuevo = Nodo(cliente)
        if not self.cabeza:
            self.cabeza = nuevo
            return
        actual = self.cabeza
        while actual.siguiente:
            actual = actual.siguiente
        actual.siguiente = nuevo

    def to_list(self):
        out = []
        actual = self.cabeza
        while actual:
            c = actual.cliente
            out.append({
                'id': c.id,
                'tipo': c.tipo,
                'llegada': c.tiempo_llegada,
                'inicio': c.tiempo_inicio_atencion,
                'fin': c.tiempo_fin_atencion
            })
            actual = actual.siguiente
        return out
