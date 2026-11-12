"""Receptor local de acciones n8n. Genera ficheros distintos por decision.

No envia emails ni tramita ayudas. Escucha loopback por defecto.
"""
import argparse
import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ACTIONS = {
    'REVISION_DATOS': ('revision_datos', 'Comprobar campos ausentes y cobertura del modelo.'),
    'REVISION_NORMATIVA': ('revision_normativa', 'Verificar convocatoria, excepciones y documentacion.'),
    'ORIENTACION_PRIORITARIA': ('cita_prioritaria', 'Solicitud interna de atencion prioritaria: pendiente de asignacion humana.'),
    'REVISION_REQUISITOS': ('checklist_requisitos', 'Checklist: edad, renta computable, residencia, titularidad e incompatibilidades.'),
    'BUSCAR_ALTERNATIVAS': ('ficha_alternativas', 'Comparar municipios y presupuesto; no asumir subvenciones concedidas.'),
    'PLANIFICAR_ENTRADA': ('plan_entrada', 'Revisar fianza y gastos de entrada declarados antes de contratar.'),
    'CONSULTAR_GAZTELAGUN': ('checklist_gaztelagun', 'Preparar solicitud para revision administrativa, sin concesion automatica.'),
    'INFORMACION_GENERAL': ('ficha_informativa', 'Presupuesto orientativo; prediccion municipal no es oferta de vivienda.'),
}
LOCK = threading.Lock()


def persist_action(root, action, payload):
    """Una accion por UUID; repetir el mismo evento no duplica solicitudes."""
    event_id = str(uuid.UUID(payload['event_id']))
    decision = payload.get('decision')
    if decision not in ACTIONS or ACTIONS[decision][0] != action:
        raise ValueError('Accion y decision no coinciden')
    allowed = {'event_id', 'decision', 'regla_id', 'renta_estimada', 'origen', 'version'}
    if set(payload) - allowed:
        raise ValueError('El payload contiene datos no autorizados')
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    path = root / f'{event_id}.json'
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    with LOCK:
        if path.exists():
            record = json.loads(path.read_text())
            if record['huella'] != fingerprint:
                raise ValueError('UUID reutilizado con contenido distinto')
        else:
            record = {'event_id': event_id, 'decision': decision, 'accion': action, 'persistido': True,
                      'fecha_utc': datetime.now(timezone.utc).isoformat(), 'huella': fingerprint,
                      'documento': ACTIONS[decision][1], 'regla_id': payload.get('regla_id'),
                      'renta_estimada': payload.get('renta_estimada'), 'resolucion_administrativa': False}
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(record, indent=2), encoding='utf-8'); temporary.replace(path)
        return record


def make_server(root, host='127.0.0.1', port=8091):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path == '/health' else 404); self.end_headers()
        def do_POST(self):
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 8192 or not self.path.startswith('/acciones/'):
                    raise ValueError('Peticion no valida')
                payload = json.loads(self.rfile.read(size))
                result = persist_action(root, self.path.rsplit('/', 1)[-1], payload)
                data = json.dumps(result).encode()
                self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(data)
            except (ValueError, TypeError, KeyError) as error:
                self.send_response(400); self.end_headers(); self.wfile.write(str(error).encode())
        def log_message(self, *args):
            pass
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1'); parser.add_argument('--port', type=int, default=8091)
    parser.add_argument('--output', default='data/acciones_n8n')
    args = parser.parse_args()
    make_server(args.output, args.host, args.port).serve_forever()
