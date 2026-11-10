"""
Módulo de consultas analíticas avanzadas en MongoDB usando PyMongo.
Cumple con la rúbrica SBD RA3:
- Consulta 1: Igualdad con proyección ordenada
- Consulta 2: Rango con operadores de comparación ($lte, $gt)
- Consulta 3: Multifiltro combinando múltiples condiciones lógicas ($and)
- Consulta 4: Acceso y filtrado por campos anidados (características del inmueble)
- Consulta 5: Búsqueda en arrays embebidos (programas de ayuda en municipios)
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MongoHousingQueries:
    """Ejecuta consultas analíticas especializadas para el reto de vivienda juvenil."""

    def __init__(self, db):
        self.db = db
        self.viviendas = db["viviendas"]
        self.municipios = db["municipios"]

    def consulta_1_alquileres_en_municipio(self, municipio: str = "Bilbao") -> List[Dict[str, Any]]:
        """Consulta 1: Filtro de igualdad y proyección con ordenación de menor a mayor precio."""
        filtro = {"municipio": municipio, "tipo_operacion": "alquiler"}
        proyeccion = {"_id": 0, "id_origen": 1, "titulo": 1, "precio": 1, "superficie_m2": 1, "municipio": 1}
        resultados = list(self.viviendas.find(filtro, proyeccion).sort("precio", 1))
        logger.info(f"Consulta 1 ({municipio}): {len(resultados)} resultados obtenidos.")
        return resultados

    def consulta_2_alquileres_asequibles_jovenes(self, precio_max: float = 750.0) -> List[Dict[str, Any]]:
        """Consulta 2: Operadores de comparación ($lte, $gt) para identificar alquileres por debajo del umbral de riesgo."""
        filtro = {
            "tipo_operacion": "alquiler",
            "precio": {"$gt": 0.0, "$lte": precio_max}
        }
        proyeccion = {"_id": 0, "titulo": 1, "municipio": 1, "precio": 1, "categoria_accesibilidad": 1}
        resultados = list(self.viviendas.find(filtro, proyeccion).sort("precio", 1))
        logger.info(f"Consulta 2 (<= {precio_max} €): {len(resultados)} viviendas asequibles.")
        return resultados

    def consulta_3_condiciones_combinadas(self, municipio: str = "Bilbao", precio_max: float = 850.0, min_m2: float = 55.0) -> List[Dict[str, Any]]:
        """Consulta 3: Combinación lógica ($and) de municipio, precio máximo y superficie mínima."""
        filtro = {
            "$and": [
                {"municipio": municipio},
                {"tipo_operacion": "alquiler"},
                {"precio": {"$lte": precio_max}},
                {"superficie_m2": {"$gte": min_m2}}
            ]
        }
        resultados = list(self.viviendas.find(filtro, {"_id": 0, "titulo": 1, "precio": 1, "superficie_m2": 1}))
        logger.info(f"Consulta 3 combinada ({municipio}): {len(resultados)} viviendas cumplen todos los criterios.")
        return resultados

    def consulta_4_campos_anidados_confort(self, min_hab: int = 2, ascensor: bool = True) -> List[Dict[str, Any]]:
        """Consulta 4: Filtrado sobre campos estructurados anidados (características)."""
        filtro = {
            "caracteristicas.habitaciones": {"$gte": min_hab},
            "caracteristicas.ascensor": ascensor
        }
        proyeccion = {
            "_id": 0,
            "titulo": 1,
            "municipio": 1,
            "precio": 1,
            "caracteristicas": 1
        }
        resultados = list(self.viviendas.find(filtro, proyeccion).limit(10))
        logger.info(f"Consulta 4 anidada (>={min_hab} hab, ascensor={ascensor}): {len(resultados)} encontrados.")
        return resultados

    def consulta_5_municipios_programas_array(self, nombre_programa: str = "Gaztelagun") -> List[Dict[str, Any]]:
        """Consulta 5: Consulta sobre arrays embebidos de programas sociales en municipios."""
        filtro = {
            "programas_ayuda": {
                "$elemMatch": {"nombre": nombre_programa}
            }
        }
        proyeccion = {
            "_id": 0,
            "municipio": 1,
            "provincia": 1,
            "salario_medio_joven_mes": 1,
            "programas_ayuda": 1
        }
        resultados = list(self.municipios.find(filtro, proyeccion))
        logger.info(f"Consulta 5 arrays (programa '{nombre_programa}'): {len(resultados)} municipios con cobertura.")
        return resultados
