class ColaPrioridadGlobal:

    prioridad_val = {'A': 0, 'M': 1, 'B': 2}

    def __init__(self):
        self._lista = []
        self._seq = 0

    def encolar(self, cliente):
        entry = (self.prioridad_val[cliente.tipo], self._seq, cliente)
        self._seq += 1
        self._lista.append(entry)
        self._lista.sort(key=lambda x: (x[0], x[1]))

    def extraer_siguiente_de_tipo(self, tipo):
        for i, (_, _, cliente) in enumerate(self._lista):
            if cliente.tipo == tipo:
                return self._lista.pop(i)[2]
        return None

    def tamaño(self):
        return len(self._lista)

    def ver_lista(self):
        return [(p, s, c.id, c.tipo) for (p, s, c) in self._lista]

