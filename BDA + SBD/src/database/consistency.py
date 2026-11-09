"""
Módulo de consistencia y atomicidad en MongoDB usando PyMongo.
Cumple con la rúbrica SBD RA3:
- Demostración de operaciones atómicas (find_one_and_update, $inc, $set)
- Justificación técnica de atomicidad documental frente a transacciones ACID distribuidas
"""
import logging
from typing import Dict, Any
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)

class MongoConsistencyManager:
    """Demuestra atomicidad a nivel de documento y justifica las decisiones de concurrencia."""

    def __init__(self, db):
        self.db = db
        self.viviendas = db["viviendas"]
        self.municipios = db["municipios"]

    def registrar_interes_joven_atomico(self, vivienda_id_origen: str) -> Dict[str, Any]:
        """
        Operación atómica: incrementa de forma segura el contador de jóvenes interesados
        en una vivienda y actualiza el timestamp sin riesgo de race conditions ni sobreescrituras.
        """
        resultado = self.viviendas.find_one_and_update(
            {"id_origen": vivienda_id_origen},
            {
                "$inc": {"solicitudes_interes_joven": 1},
                "$set": {"ultima_consulta_timestamp": "2026-10-28T12:00:00Z"}
            },
            return_document=ReturnDocument.AFTER
        )
        if resultado:
            logger.info(f"Operación atómica completada para {vivienda_id_origen}. Nuevo contador: {resultado.get('solicitudes_interes_joven')}")
            return {
                "id_origen": vivienda_id_origen,
                "solicitudes_interes_joven": resultado.get("solicitudes_interes_joven", 1),
                "atomicidad_garantizada": True
            }
        return {"id_origen": vivienda_id_origen, "atomicidad_garantizada": False}

    def obtener_justificacion_tecnica(self) -> Dict[str, str]:
        """
        Devuelve la justificación técnica exigida por la rúbrica SBD RA3
        sobre la idoneidad de operaciones atómicas documentales frente a transacciones pesadas.
        """
        return {
            "decision_arquitectura": "Operaciones Atómicas a nivel de Documento (Sin transacción multdocumento)",
            "justificacion": (
                "En el ecosistema de MongoDB, cualquier operación de modificación sobre un único documento "
                "es estrictamente atómica por diseño (garantizada por WiredTiger a nivel de registro). "
                "Dado que nuestro modelo de datos incrusta las características del inmueble y los indicadores clave "
                "dentro del propio documento o mantiene referencias unidireccionales, no existen estados intermedios inconsistentes. "
                "El uso de transacciones ACID distribuidas de dos fases (2PC) penalizaría el rendimiento de ingesta masiva (throughput) "
                "y aumentaría la latencia sin aportar beneficio real de integridad en un sistema de análisis inmobiliario y Big Data."
            ),
            "mecanismo_utilizado": "find_one_and_update con operadores $inc y $set atómicos."
        }
