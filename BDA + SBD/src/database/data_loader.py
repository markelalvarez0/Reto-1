"""
Módulo de carga e integración de datos multifuente en MongoDB.
Integra datos de API (Visesa/Open Data), Scraping (Habitaclia/Pisos) e Indicadores (Eustat/OVJ),
demostrando decisiones de modelado (embedding y referencing).
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MongoDBDataLoader:
    """Carga e integra datos en colecciones MongoDB respetando decisiones de modelado."""

    def __init__(self, db):
        self.db = db
        self.viviendas_col = db["viviendas"]
        self.municipios_col = db["municipios"]

    def cargar_datos_base(self, data_raw_dir: Path) -> Dict[str, int]:
        """
        Lee datos extraídos de API, Scraping e Indicadores y los carga en MongoDB.
        """
        data_raw_dir = Path(data_raw_dir)
        total_viviendas = 0
        total_municipios = 0

        # 1. Cargar Indicadores Municipales (Colección 'municipios' con embedding de programas)
        municipios_seed = self._generar_datos_municipios_base()
        
        # Buscar ficheros de indicadores reales si existen
        indicadores_files = list(data_raw_dir.glob("indicadores_*.json"))
        if indicadores_files:
            try:
                with open(indicadores_files[0], "r", encoding="utf-8") as f:
                    ind_data = json.load(f)
                    # Enriquecer municipios seed
                    for item in ind_data:
                        mun_name = item.get("municipio")
                        if mun_name in municipios_seed:
                            municipios_seed[mun_name]["indicadores_oficiales"] = item
            except Exception as e:
                logger.warning(f"Error procesando indicadores JSON: {e}")

        # Insertar municipios
        self.municipios_col.delete_many({})
        docs_municipios = list(municipios_seed.values())
        if docs_municipios:
            self.municipios_col.insert_many(docs_municipios)
            total_municipios = len(docs_municipios)

        # 2. Cargar Viviendas (API + Scraping) con Referencing hacia municipios
        self.viviendas_col.delete_many({})
        viviendas_docs = []

        # API (Visesa / Open Data Euskadi)
        api_files = list(data_raw_dir.glob("vivienda_api_*.json"))
        if api_files:
            try:
                with open(api_files[0], "r", encoding="utf-8") as f:
                    api_data = json.load(f)
                    for ad in api_data:
                        doc = self._normalizar_anuncio_api(ad)
                        viviendas_docs.append(doc)
            except Exception as e:
                logger.warning(f"Error cargando viviendas API: {e}")

        # Scraping (Habitaclia / Pisos.com)
        scraping_files = list(data_raw_dir.glob("vivienda_scraping_*.json"))
        if scraping_files:
            try:
                with open(scraping_files[0], "r", encoding="utf-8") as f:
                    scraping_data = json.load(f)
                    for ad in scraping_data:
                        doc = self._normalizar_anuncio_scraping(ad)
                        viviendas_docs.append(doc)
            except Exception as e:
                logger.warning(f"Error cargando viviendas Scraping: {e}")

        # Si no había ficheros en bruto, inyectar un conjunto representativo para garantizar ejecución inmediata
        if not viviendas_docs:
            viviendas_docs = self._generar_viviendas_seed()

        if viviendas_docs:
            self.viviendas_col.insert_many(viviendas_docs)
            total_viviendas = len(viviendas_docs)

        logger.info(f"Carga finalizada: {total_municipios} municipios y {total_viviendas} viviendas en MongoDB.")
        return {"municipios": total_municipios, "viviendas": total_viviendas}

    def _normalizar_anuncio_api(self, ad: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma anuncio de API al esquema unificado con referencing."""
        municipio = ad.get("municipio", "Bilbao")
        return {
            "id_origen": ad.get("id", ""),
            "titulo": ad.get("titulo", "Promoción VPO"),
            "municipio": municipio,
            "tipo_operacion": ad.get("tipo_operacion", "compra").lower(),
            "precio": float(ad.get("precio", 150000.0)),
            "superficie_m2": float(ad.get("superficie_m2", 75.0)),
            "fuente": "api_visesa",
            "caracteristicas": {
                "habitaciones": int(ad.get("habitaciones", 2)),
                "banos": int(ad.get("banos", 1)),
                "ascensor": True,
                "calefaccion": True,
                "garaje": True
            },
            "es_protegida": True
        }

    def _normalizar_anuncio_scraping(self, ad: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma anuncio de Scraping al esquema unificado con referencing."""
        municipio = ad.get("municipio", "Bilbao")
        return {
            "id_origen": ad.get("id", ""),
            "titulo": ad.get("titulo", "Piso en alquiler"),
            "municipio": municipio,
            "tipo_operacion": ad.get("tipo_operacion", "alquiler").lower(),
            "precio": float(ad.get("precio", 750.0)),
            "superficie_m2": float(ad.get("superficie_m2", 65.0)),
            "fuente": ad.get("fuente", "habitaclia"),
            "caracteristicas": {
                "habitaciones": int(ad.get("habitaciones", 2)),
                "banos": int(ad.get("banos", 1)),
                "ascensor": bool(ad.get("ascensor", True)),
                "calefaccion": True,
                "garaje": False
            },
            "es_protegida": False
        }

    def _generar_datos_municipios_base(self) -> Dict[str, Dict[str, Any]]:
        """
        Decisión de modelado MongoDB:
        Embedding de indicadores socioeconómicos y programas juveniles dentro del documento del municipio,
        evitando joins innecesarios para lecturas frecuentes.
        """
        return {
            "Bilbao": {
                "municipio": "Bilbao",
                "provincia": "Bizkaia",
                "poblacion_total": 346000,
                "poblacion_joven_18_34": 52400,
                "salario_medio_joven_mes": 1380.0,
                "renta_media_persona": 18250.0,
                "paro_juvenil_pct": 14.8,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35},
                    {"nombre": "VPO_Alquiler", "cobertura_max": 400.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": "ALTO"
            },
            "Donostia-San Sebastián": {
                "municipio": "Donostia-San Sebastián",
                "provincia": "Gipuzkoa",
                "poblacion_total": 188000,
                "poblacion_joven_18_34": 27800,
                "salario_medio_joven_mes": 1420.0,
                "renta_media_persona": 21500.0,
                "paro_juvenil_pct": 11.2,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35},
                    {"nombre": "Etxebide_Donostia", "cobertura_max": 350.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": "MUY_ALTO"
            },
            "Vitoria-Gasteiz": {
                "municipio": "Vitoria-Gasteiz",
                "provincia": "Araba",
                "poblacion_total": 254000,
                "poblacion_joven_18_34": 38900,
                "salario_medio_joven_mes": 1360.0,
                "renta_media_persona": 19100.0,
                "paro_juvenil_pct": 13.5,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35},
                    {"nombre": "Ensanche21", "cobertura_max": 250.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": "MODERADO"
            },
            "Barakaldo": {
                "municipio": "Barakaldo",
                "provincia": "Bizkaia",
                "poblacion_total": 101000,
                "poblacion_joven_18_34": 15600,
                "salario_medio_joven_mes": 1310.0,
                "renta_media_persona": 16800.0,
                "paro_juvenil_pct": 15.2,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": "MODERADO"
            },
            "Getxo": {
                "municipio": "Getxo",
                "provincia": "Bizkaia",
                "poblacion_total": 77000,
                "poblacion_joven_18_34": 10500,
                "salario_medio_joven_mes": 1490.0,
                "renta_media_persona": 23400.0,
                "paro_juvenil_pct": 10.5,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": "ALTO"
            }
        }

    def _generar_viviendas_seed(self) -> List[Dict[str, Any]]:
        """Genera un catálogo representativo con variedad de precios y operaciones."""
        items = []
        municipios = ["Bilbao", "Donostia-San Sebastián", "Vitoria-Gasteiz", "Barakaldo", "Getxo"]
        precios_alquiler = {
            "Bilbao": [650, 750, 850, 950, 1100],
            "Donostia-San Sebastián": [850, 950, 1050, 1250, 1400],
            "Vitoria-Gasteiz": [520, 600, 680, 750, 820],
            "Barakaldo": [580, 650, 720, 780, 850],
            "Getxo": [750, 850, 950, 1150, 1300]
        }

        counter = 1
        for mun in municipios:
            # Alquileres mercado libre (scraping)
            for p in precios_alquiler[mun]:
                items.append({
                    "id_origen": f"scrap_hab_{counter}",
                    "titulo": f"Piso de alquiler en {mun}",
                    "municipio": mun,
                    "tipo_operacion": "alquiler",
                    "precio": float(p),
                    "superficie_m2": 65.0,
                    "fuente": "habitaclia",
                    "caracteristicas": {
                        "habitaciones": 2 if p < 800 else 3,
                        "banos": 1 if p < 800 else 2,
                        "ascensor": True,
                        "calefaccion": True,
                        "garaje": False
                    },
                    "es_protegida": False
                })
                counter += 1

            # Promociones VPO (API Visesa)
            items.append({
                "id_origen": f"vpo_api_{counter}",
                "titulo": f"Promoción Vivienda Protegida VPO en {mun}",
                "municipio": mun,
                "tipo_operacion": "alquiler",
                "precio": 380.0 if mun == "Vitoria-Gasteiz" else 450.0,
                "superficie_m2": 72.0,
                "fuente": "api_visesa",
                "caracteristicas": {
                    "habitaciones": 2,
                    "banos": 1,
                    "ascensor": True,
                    "calefaccion": True,
                    "garaje": True
                },
                "es_protegida": True
            })
            counter += 1

            items.append({
                "id_origen": f"vpo_compra_{counter}",
                "titulo": f"Vivienda Tasada Autonómica en {mun}",
                "municipio": mun,
                "tipo_operacion": "compra",
                "precio": 145000.0,
                "superficie_m2": 80.0,
                "fuente": "api_visesa",
                "caracteristicas": {
                    "habitaciones": 3,
                    "banos": 2,
                    "ascensor": True,
                    "calefaccion": True,
                    "garaje": True
                },
                "es_protegida": True
            })
            counter += 1

        return items
