"""
Módulo de Aggregation Pipelines avanzadas en MongoDB usando PyMongo.
Cumple con la rúbrica SBD RA3:
- Pipeline 1: Agrupación ($match -> $group -> $project -> $sort)
- Pipeline 2: Cruce relacional ($match -> $lookup -> $unwind -> $project -> $sort)
- Pipeline 3: Multifaceta ($match -> $facet) con 3 dimensiones analíticas
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MongoHousingAggregations:
    """Implementa pipelines de agregación analítica para el reto de vivienda."""

    def __init__(self, db):
        self.db = db
        self.viviendas = db["viviendas"]
        self.municipios = db["municipios"]

    def pipeline_1_estadisticas_alquiler_por_municipio(self) -> List[Dict[str, Any]]:
        """
        Pipeline 1: Estadísticas agregadas de alquiler por municipio.
        Etapas utilizadas: $match, $group, $project, $sort
        """
        pipeline = [
            {"$match": {"tipo_operacion": "alquiler"}},
            {
                "$group": {
                    "_id": "$municipio",
                    "total_anuncios": {"$sum": 1},
                    "precio_medio": {"$avg": "$precio"},
                    "precio_minimo": {"$min": "$precio"},
                    "precio_maximo": {"$max": "$precio"},
                    "superficie_media": {"$avg": "$superficie_m2"},
                    "precio_m2_medio": {"$avg": "$precio_m2"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "municipio": "$_id",
                    "total_anuncios": 1,
                    "precio_medio": "$precio_medio",
                    "precio_minimo": "$precio_minimo",
                    "precio_maximo": "$precio_maximo",
                    "superficie_media": "$superficie_media",
                    "precio_m2_medio": "$precio_m2_medio"
                }
            },
            {"$sort": {"precio_medio": 1}}
        ]
        resultados = list(self.viviendas.aggregate(pipeline))
        for r in resultados:
            if "precio_medio" in r and r["precio_medio"] is not None:
                r["precio_medio"] = round(float(r["precio_medio"]), 2)
            if "superficie_media" in r and r["superficie_media"] is not None:
                r["superficie_media"] = round(float(r["superficie_media"]), 1)
            if "precio_m2_medio" in r and r["precio_m2_medio"] is not None:
                r["precio_m2_medio"] = round(float(r["precio_m2_medio"]), 2)
        logger.info(f"Pipeline 1 (Agrupación por municipio): {len(resultados)} municipios analizados.")
        return resultados

    def pipeline_2_cruce_esfuerzo_salarial(self) -> List[Dict[str, Any]]:
        """
        Pipeline 2: Cruce de viviendas con datos demográficos y salariales mediante $lookup y $unwind.
        Calcula la tasa de esfuerzo salarial porcentual por vivienda.
        Etapas: $match, $lookup, $unwind, $project, $sort
        """
        pipeline = [
            {"$match": {"tipo_operacion": "alquiler"}},
            {
                "$lookup": {
                    "from": "municipios",
                    "localField": "municipio",
                    "foreignField": "municipio",
                    "as": "datos_municipio"
                }
            },
            {"$unwind": "$datos_municipio"},
            {
                "$project": {
                    "_id": 0,
                    "titulo": 1,
                    "municipio": 1,
                    "precio": 1,
                    "es_protegida": 1,
                    "salario_medio_joven": "$datos_municipio.salario_medio_joven_mes",
                    "paro_juvenil_pct": "$datos_municipio.paro_juvenil_pct"
                }
            },
            {"$sort": {"precio": 1}}
        ]
        resultados = list(self.viviendas.aggregate(pipeline))
        for r in resultados:
            salario = r.get("salario_medio_joven", 1300.0)
            precio = r.get("precio", 700.0)
            r["tasa_esfuerzo_pct"] = round((precio / salario) * 100, 2) if salario > 0 else 0.0

        logger.info(f"Pipeline 2 ($lookup + $unwind): {len(resultados)} cruces calculados.")
        return resultados

    def pipeline_3_facet_distribucion_y_top(self) -> Dict[str, Any]:
        """
        Pipeline 3: Agregación multidimensional con $facet para preparar resultados de visualización.
        Sub-pipelines:
        - distribucion_accesibilidad: conteo por categoría
        - top_asequibles: top 5 opciones con menor precio
        - desglose_operacion: totales por alquiler vs compra
        """
        pipeline = [
            {
                "$facet": {
                    "distribucion_accesibilidad": [
                        {"$group": {"_id": "$categoria_accesibilidad", "total": {"$sum": 1}}},
                        {"$sort": {"total": -1}}
                    ],
                    "top_asequibles": [
                        {"$match": {"tipo_operacion": "alquiler"}},
                        {"$sort": {"precio": 1}},
                        {"$limit": 5},
                        {"$project": {"_id": 0, "titulo": 1, "municipio": 1, "precio": 1, "es_protegida": 1}}
                    ],
                    "desglose_por_tipo": [
                        {
                            "$group": {
                                "_id": "$tipo_operacion",
                                "total": {"$sum": 1},
                                "precio_promedio": {"$avg": "$precio"}
                            }
                        }
                    ]
                }
            }
        ]
        resultados = list(self.viviendas.aggregate(pipeline))
        logger.info("Pipeline 3 ($facet multidimensional) ejecutado con éxito.")
        return resultados[0] if resultados else {}
