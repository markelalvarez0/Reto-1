"""Envio real al webhook; nunca declara exito cuando la red falla."""
import os
import uuid
from urllib.parse import urlparse
import requests
from src.reglas import DECISIONES


class N8NWebhookClient:
    def __init__(self, webhook_url=None, *, demo_mode=False, timeout=10):
        self.webhook_url = webhook_url or os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/vivienda-decision')
        parsed = urlparse(self.webhook_url)
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1', 'n8n'}):
            raise ValueError('Webhook remoto debe usar HTTPS; HTTP solo para el servicio local')
        self.demo_mode, self.timeout = demo_mode, timeout

    def disparar_accion(self, decision_dict, datos_solicitante=None, *, event_id=None):
        """Minimiza datos: no envia nombre, ingresos, domicilio, email ni perfil personal."""
        decision = decision_dict.get('decision')
        if decision not in DECISIONES:
            raise ValueError('Decision no reconocida')
        event_id = str(uuid.UUID(str(event_id))) if event_id else str(uuid.uuid4())
        payload = {'event_id': event_id, 'decision': decision,
                   'regla_id': decision_dict.get('regla_id'),
                   'renta_estimada': decision_dict.get('renta_estimada'),
                   'origen': 'Streamlit_Reto1', 'version': 1}
        if self.demo_mode:
            return {'estado': 'DEMO_NO_ENVIADO', 'payload_enviado': payload}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout,
                                     headers={'Idempotency-Key': event_id})
            response.raise_for_status()
            ack = response.json()
            if ack.get('event_id') != event_id or ack.get('persistido') is not True:
                raise ValueError('Respuesta sin confirmacion de accion persistida')
            return {'estado': 'ENVIADO_N8N', 'payload_enviado': payload, 'respuesta_n8n': ack}
        except (requests.RequestException, ValueError) as error:
            return {'estado': 'ERROR_N8N', 'payload_enviado': payload, 'error': str(error)}
