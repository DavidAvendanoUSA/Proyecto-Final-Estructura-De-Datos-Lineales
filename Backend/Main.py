from Modelo.Simulador import SimuladorBanco

tiempo_total = 3600
prob_llegada = {'A': 0.01, 'M': 0.02, 'B': 0.03}
prob_servicio = {'A': 0.005, 'M': 0.004, 'B': 0.003}

sim = SimuladorBanco(tiempo_total, prob_llegada, prob_servicio)



resultado = sim.run()

import json
print("\n--- ESTADÍSTICAS FINALES ---")
print(json.dumps(resultado['estadisticas'], indent=2))

print("\nHistorial (primeros 10):")
for r in resultado['historial'][:10]:
    print(r)