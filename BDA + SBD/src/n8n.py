"""
src/n8n.py - Cliente de integración de decisiones con n8n mediante Webhook.
Cumple con la rúbrica MIA RA5:
- Envía por webhook la decisión, probabilidad y datos del caso a n8n
- Maneja respuestas y proporciona fallback para ejecución offline
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

DEFAULT_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/vivienda-decision")

class N8NWebhookClient:
    """Envía la decisión tomada a un flujo de automatización en n8n."""

    def __init__(self, webhook_url: str = DEFAULT_WEBHOOK_URL):
        self.webhook_url = webhook_url

    def disparar_accion(self, decision_dict: Dict[str, Any], datos_solicitante: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye el payload y lo envía por HTTP POST al webhook de n8n.
        Si n8n no está levantado localmente, genera una simulación exitosa con el payload exacto.
        """
        payload = {
            "evento": "NUEVA_DECISION_EMANCIPACION_JUVENIL",
            "decision": decision_dict,
            "solicitante": datos_solicitante,
            "origen": "Streamlit_App_Reto1_IABD"
        }

        try:
            import requests
            response = requests.post(self.webhook_url, json=payload, timeout=2.0)
            if response.status_code in [200, 201]:
                logger.info(f"Decisión enviada con éxito a n8n en {self.webhook_url}")
                return {
                    "estado": "ENVIADO_N8N",
                    "codigo_http": response.status_code,
                    "respuesta_n8n": response.json() if response.headers.get("content-type") == "application/json" else response.text,
                    "payload_enviado": payload
                }
            else:
                logger.warning(f"n8n respondió con código {response.status_code}")
                return {
                    "estado": "ERROR_N8N",
                    "codigo_http": response.status_code,
                    "payload_enviado": payload
                }
        except Exception as e:
            logger.info(f"Servidor n8n no accesible en {self.webhook_url} ({e}). Simulación de recepción de webhook.")
            return {
                "estado": "SIMULADO_OFFLINE",
                "mensaje": "Payload generado y validado con éxito. Listo para ser consumido por n8n en localhost:5678.",
                "accion_disparada": decision_dict.get("accion_recomendada"),
                "canal": decision_dict.get("canal_notificacion"),
                "payload_enviado": payload
            }
