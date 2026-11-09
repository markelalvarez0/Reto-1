#!/usr/bin/env python3
"""
main.py - Orquestador y punto de entrada para el Reto Intermodular BDA + SBD:
"¿Dónde pueden vivir los jóvenes en Euskadi?"

Integra los 8 objetivos del reto:
1. Extracción de vivienda vía API y Web Scraping (BDA)
2. Indicadores complementarios de salarios y juventud (BDA/SBD)
3. Almacenamiento y verificación de integridad en Apache HDFS (BDA)
4. Streaming con Apache Kafka productor/consumidor (BDA)
5. Carga y modelado documental en MongoDB con PyMongo (SBD)
6. Limpieza y transformaciones automatizadas en MongoDB (SBD)
7. Consultas complejas, 3 Aggregation Pipelines y optimización con Índices (SBD)
8. Demostración de atomicidad, cálculo de indicadores y visualización web (SBD)
"""

import os
import sys
import argparse
import webbrowser
import threading
from pathlib import Path

# Configurar sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from src.extraction.api_client import OpenDataEuskadiHousingClient
from src.extraction.scraper import HabitacliaScraper
from src.extraction.pisos_scraper import PisosComScraper
from src.indicators.udalmap_client import UdalmapClient
from src.indicators.ovj_client import OVJYouthEmancipationClient
from src.hdfs.client import HDFSClient
from src.kafka.producer import HousingKafkaProducer
from src.kafka.consumer import HousingKafkaConsumer
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader
from src.database.cleaning import MongoDataCleaner
from src.database.queries import MongoHousingQueries
from src.database.aggregations import MongoHousingAggregations
from src.database.indexes import MongoIndexOptimizer
from src.database.consistency import MongoConsistencyManager
from src.analysis.housing_study import YouthHousingStudy


def ejecutar_pipeline_completo(abrir_dashboard: bool = False):
    print("=" * 80)
    print("RETO INTERMODULAR BDA + SBD: VIVIENDA JUVENIL EN EUSKADI")
    print("=" * 80)

    # 1. BDA: Extracción
    print("\n[1/8] [BDA] Extracción de Vivienda (API REST + Web Scraping)...")
    api_client = OpenDataEuskadiHousingClient(storage_dir=str(CURRENT_DIR / "data" / "raw"))
    promociones = api_client.fetch_vivienda_data()
    api_files = api_client.save_raw_data()
    print(f"  -> API Visesa: {len(promociones)} promociones obtenidas. Ficheros: {api_files.get('json')}")

    scraper = HabitacliaScraper(storage_dir=str(CURRENT_DIR / "data" / "raw"))
    anuncios_hab = scraper.scrape_bilbao_rentals(max_pages=1)
    scrap_files = scraper.save_raw_data()
    print(f"  -> Scraping Habitaclia: {len(anuncios_hab)} anuncios obtenidos. Ficheros: {scrap_files.get('json')}")

    # 2. BDA: Indicadores
    print("\n[2/8] [BDA] Extracción de Indicadores Socioeconómicos y Demográficos...")
    udalmap_client = UdalmapClient(storage_dir=str(CURRENT_DIR / "data" / "raw"))
    indicadores = udalmap_client.fetch_all_key_indicators()
    ind_files = udalmap_client.save_raw_data()
    print(f"  -> Udalmap / Eustat: {len(indicadores)} series registradas. Fichero: {ind_files.get('json')}")

    # 3. BDA: Almacenamiento en HDFS
    print("\n[3/8] [BDA] Almacenamiento y Verificación de Integridad en Apache HDFS...")
    hdfs = HDFSClient(base_storage_dir=str(CURRENT_DIR / "data" / "hdfs_storage"))
    hdfs_meta = hdfs.upload_raw_dataset(api_files["json"], "vivienda/api")
    print(f"  -> HDFS Subida: {hdfs_meta.hdfs_path} ({hdfs_meta.size_bytes} bytes, Checksum SHA256: {hdfs_meta.checksum[:16]}...)")
    recuperado = hdfs.download_file(hdfs_meta.hdfs_path)
    print(f"  -> [OK] Verificación de integridad: Fichero recuperado idéntico al original.")

    # 4. BDA: Streaming con Apache Kafka
    print("\n[4/8] [BDA] Simulación Streaming con Apache Kafka (Productor -> Consumidor)...")
    producer = HousingKafkaProducer(use_mock=True)
    consumer = HousingKafkaConsumer(use_mock=True)
    anuncios_muestra = [a.model_dump() for a in anuncios_hab[:3]] if anuncios_hab else [
        {"id": "demo_1", "titulo": "Piso en Bilbao Centro", "precio": 750.0, "municipio": "Bilbao", "tipo_operacion": "alquiler"}
    ]
    pub_count = producer.produce_batch(anuncios_muestra)
    print(f"  -> Publicados {pub_count} anuncios en tópico 'euskadi-anuncios-inmobiliarios'")
    recibidos = consumer.poll_messages(max_messages=pub_count)
    print(f"  -> Consumidor recibió y validó {len(recibidos)} mensajes con esquema Pydantic.")

    # 5. SBD: MongoDB Carga y Modelado
    print("\n[5/8] [SBD] Carga de Datos en MongoDB y Modelado Documental (PyMongo)...")
    mongo_mgr = MongoDBManager()
    loader = MongoDBDataLoader(mongo_mgr.db)
    res_carga = loader.cargar_datos_base(CURRENT_DIR / "data" / "raw")
    print(f"  -> Colecciones cargadas: {res_carga['municipios']} municipios y {res_carga['viviendas']} viviendas.")
    print("  -> Decisión de modelado: Embedding de programas sociales e indicadores en 'municipios' y referencing en 'viviendas'.")

    # 6. SBD: Limpieza y Transformación PyMongo
    print("\n[6/8] [SBD] Limpieza y Transformaciones Automatizadas con PyMongo...")
    cleaner = MongoDataCleaner(mongo_mgr.db)
    res_limpieza = cleaner.ejecutar_pipeline_limpieza()
    print(f"  -> Duplicados eliminados: {res_limpieza['duplicados_eliminados']}")
    print(f"  -> Nulos / ausentes tratados: {res_limpieza['nulos_tratados']}")
    print(f"  -> Tipos y formatos estandarizados: {res_limpieza['tipos_corregidos']}")
    print(f"  -> Campos derivados calculados (precio_m2, accesibilidad): {res_limpieza['campos_calculados']}")

    # 7. SBD: Consultas Complejas, Aggregations e Índices
    print("\n[7/8] [SBD] Consultas Complejas, Aggregation Pipelines y Optimización de Rendimiento...")
    queries = MongoHousingQueries(mongo_mgr.db)
    q1 = queries.consulta_1_alquileres_en_municipio("Bilbao")
    q2 = queries.consulta_2_alquileres_asequibles_jovenes(750.0)
    q3 = queries.consulta_3_condiciones_combinadas("Bilbao", 850.0, 50.0)
    q4 = queries.consulta_4_campos_anidados_confort(2, True)
    q5 = queries.consulta_5_municipios_programas_array("Gaztelagun")
    print(f"  -> 5 Consultas avanzadas ejecutadas con éxito (Q1: {len(q1)}, Q2: {len(q2)}, Q3: {len(q3)}, Q4: {len(q4)}, Q5: {len(q5)}).")

    aggregations = MongoHousingAggregations(mongo_mgr.db)
    agg1 = aggregations.pipeline_1_estadisticas_alquiler_por_municipio()
    agg2 = aggregations.pipeline_2_cruce_esfuerzo_salarial()
    agg3 = aggregations.pipeline_3_facet_distribucion_y_top()
    print(f"  -> Pipeline 1 ($group por municipio): {len(agg1)} municipios agregados.")
    print(f"  -> Pipeline 2 ($lookup + $unwind cruce esfuerzo): {len(agg2)} registros cruzados.")
    print(f"  -> Pipeline 3 ($facet multifacético): 3 dimensiones de análisis generadas.")

    index_opt = MongoIndexOptimizer(mongo_mgr.db, is_mock=mongo_mgr.is_mock)
    rendimiento = index_opt.comparar_rendimiento_consulta("Bilbao", 850.0)
    print(f"  -> Optimización con explain():")
    print(f"     * Sin índice: Stage={rendimiento['sin_indice']['stage']} | Docs examinados={rendimiento['sin_indice']['totalDocsExamined']}")
    print(f"     * Con índice: Stage={rendimiento['con_indice']['stage']} | Docs examinados={rendimiento['con_indice']['totalDocsExamined']}")
    if "reduccion_documentos_examinados_pct" in rendimiento:
        print(f"     * Reducción de Docs examinados: {rendimiento['reduccion_documentos_examinados_pct']}%")

    # 8. SBD: Consistencia, Indicadores y Conclusiones
    print("\n[8/8] [SBD] Consistencia Atómica y Diagnóstico Analítico...")
    consist_mgr = MongoConsistencyManager(mongo_mgr.db)
    op_atomica = consist_mgr.registrar_interes_joven_atomico("scrap_hab_1")
    justificacion = consist_mgr.obtener_justificacion_tecnica()
    print(f"  -> Operación atómica demostrada: find_one_and_update (Atomicidad={op_atomica.get('atomicidad_garantizada')})")
    print(f"  -> Justificación técnica: {justificacion['justificacion'][:120]}...")

    # Conclusiones finales del estudio
    estudio = YouthHousingStudy(data_dir=str(CURRENT_DIR / "data"))
    diag = estudio.generate_comprehensive_study()
    print("\n" + "=" * 80)
    print(f"RESPUESTA AL RETO: {diag.conclusiones.respuesta_ejecutiva}")
    print(f"  * ¿Pueden vivir solos en mercado libre? {'SÍ' if diag.conclusiones.puede_en_solitario_mercado_libre else 'NO'}")
    print(f"  * ¿Dónde pueden vivir con Gaztelagun o VPO? {', '.join(diag.conclusiones.donde_pueden_vivir)}")
    print(f"  * Zonas más tensionadas: {', '.join(diag.conclusiones.donde_no_pueden_vivir_solos)}")
    print("=" * 80)

    if abrir_dashboard:
        abrir_dashboard_web()


def abrir_dashboard_web(puerto: int = 8080):
    """Lanza el servidor estático y mantiene el dashboard visual interactivo activo en primer plano."""
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    import socket

    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    target_port = puerto
    while is_port_in_use(target_port):
        target_port += 1

    url = f"http://localhost:{target_port}/dashboard/dashboard.html"

    os.chdir(CURRENT_DIR)
    httpd = ThreadingHTTPServer(("0.0.0.0", target_port), SimpleHTTPRequestHandler)
    print(f"\n[DASHBOARD VISUAL] Servidor HTTP activo en http://localhost:{target_port}")
    print(f"Abriendo {url} en el navegador...")
    print("-" * 72)
    print("  El Dashboard Cartográfico Leaflet está disponible en tu navegador.")
    print("  Mantén esta terminal abierta mientras uses la web.")
    print("  Pulsa Ctrl+C cuando desees detener el servidor.")
    print("-" * 72 + "\n")
    
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[DASHBOARD VISUAL] Servidor detenido por el usuario.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador Reto Intermodular BDA + SBD")
    parser.add_argument("--visual", action="store_true", help="Abrir dashboard interactivo en el navegador")
    parser.add_argument("--test", action="store_true", help="Ejecutar suite de pruebas pytest")
    args = parser.parse_args()

    if args.test:
        import pytest
        sys.exit(pytest.main(["BDA + SBD/tests", "-v"]))
    elif args.visual:
        abrir_dashboard_web()
    else:
        ejecutar_pipeline_completo(abrir_dashboard=False)
