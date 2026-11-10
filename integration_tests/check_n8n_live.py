"""Comprueba que cada decision recorre una rama y crea su accion real."""
import json
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.action_server import ACTIONS
from src.n8n import N8NWebhookClient


def check(output='test-results/n8n-live.json'):
    client = N8NWebhookClient()
    results = []
    for decision, (action, _) in ACTIONS.items():
        event = str(uuid4())
        result = client.disparar_accion({'decision':decision, 'regla_id':'CI', 'renta_estimada':700}, event_id=event)
        assert result['estado'] == 'ENVIADO_N8N', result
        assert result['respuesta_n8n']['accion'] == action
        repeat = client.disparar_accion({'decision':decision, 'regla_id':'CI','renta_estimada':700}, event_id=event)
        assert repeat['respuesta_n8n'] == result['respuesta_n8n']
        path = Path('data/acciones_n8n') / (event + '.json')
        assert path.exists(), f'No hay accion persistida: {event}'
        results.append(result)
    target = Path(output); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({'motor':'n8n real', 'datos':'fixtures sin datos personales', 'ramas':len(results), 'resultados':results}, indent=2))
    print(f'{len(results)} ramas verificadas con persistencia e idempotencia')

if __name__ == '__main__':
    check()
