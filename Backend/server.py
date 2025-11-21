from flask import Flask, jsonify, request
from flask_cors import CORS
from config.db import DatabaseConnection
from Dao.DAO_colas import DAOColas
from Dao.DAO_corridas import DAOCorridas
from Controller.SimuladorController import SimuladorController


# Config por defecto (puedes permitir override desde front)
DEFAULT_PROB_LLEGADA = {'A': 0.1, 'M': 0.05, 'B': 0.02}
DEFAULT_PROB_SERVICIO = {'A': 0.7, 'M': 0.6, 'B': 0.5}
DEFAULT_TIEMPO = 100


app = Flask(__name__)
CORS(app)


# Bootstrap: crear conexión y DAOs
db_conn = DatabaseConnection()
dao_colas = DAOColas(db_conn)
dao_corridas = DAOCorridas(db_conn)

# Crear controller con DAOs inyectados
controller = SimuladorController(DEFAULT_TIEMPO, DEFAULT_PROB_LLEGADA, DEFAULT_PROB_SERVICIO,
                                 dao_colas, dao_corridas)


@app.route('/simulacion/start', methods=['POST'])
def start_simulacion():
    data = request.get_json(silent=True) or {}
    # Opcional: permitir sobrescribir params por petición
    tiempo = data.get('tiempo', controller.simulador.tiempo_total)
    prob_llegada = data.get('prob_llegada', controller.simulador.prob_llegada)
    prob_servicio = data.get('prob_servicio', controller.simulador.prob_servicio)

    # Aplicar cambios si la simulación no está corriendo
    if controller.is_running():
        return jsonify({'started': False, 'reason': 'already_running'}), 409

    # Restaurar el simulador con parámetros recibidos
    controller.simulador = controller.simulador.__class__(tiempo, prob_llegada, prob_servicio)
    started = controller.correr()
    return jsonify({'started': started}), (201 if started else 500)


@app.route('/simulacion/pause', methods=['POST'])
def pause_simulacion():
    controller.pausar()
    return jsonify({'paused': True})


@app.route('/simulacion/resume', methods=['POST'])
def resume_simulacion():
    controller.reanudar()
    return jsonify({'resumed': True})


@app.route('/simulacion/stop', methods=['POST'])
def stop_simulacion():
    controller.detener()
    return jsonify({'stopped': True})


@app.route('/simulacion/restore', methods=['POST'])
def restore_simulacion():
    controller.restaurar_parametros()
    return jsonify({'restored': True})


@app.route('/simulacion/status', methods=['GET'])
def status():
    sim = controller.simulador
    return jsonify({
        'running': controller.is_running(),
        'pausado': sim.pausado,
        'tiempo_total': sim.tiempo_total,
        'cola_tamaño': sim.cola_prioridad.tamaño(),
        'logs_count': len(sim.logs),
    })


@app.route('/simulacion/result', methods=['GET'])
def result():
    # Devuelve resultados finales si la simulación terminó
    if controller.is_running():
        return jsonify({'status': 'running'}), 202
    res = {
        'estadisticas': controller.simulador.stats,
        'historial': controller.simulador.historial.to_list(),
        'cola_prioridad': controller.simulador.cola_prioridad.ver_lista(),
        'logs': controller.simulador.logs,
    }
    return jsonify(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
