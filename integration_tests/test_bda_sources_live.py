"""Capturas oficiales reales -> HDFS real -> Kafka real -> MongoDB real.

No prueba disponibilidad actual de las promociones ni oferta del mercado libre.
"""
from collections import Counter
import json
import os
from pathlib import Path
import time
import uuid

import pytest

from scripts.run_pipeline import run_pipeline
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader
from src.extraction.source_snapshots import verify_snapshot

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(os.getenv('BDA_LIVE') != '1', reason='Requiere HDFS, Kafka y MongoDB reales')


def test_capturas_reales_atraviesan_todo_el_pipeline(tmp_path):
    from kafka import KafkaAdminClient
    for attempt in range(30):
        try:
            admin = KafkaAdminClient(bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'), request_timeout_ms=5000)
            admin.list_topics(); admin.close()
            break
        except Exception:
            if attempt == 29:
                raise
            time.sleep(2)
    snapshot = ROOT / 'data/capturas_oficiales'
    sources = verify_snapshot(snapshot)
    token = uuid.uuid4().hex
    database, topic = 'reto1_bda_ci_' + token, 'reto1_bda_ci_' + token
    manager = MongoDBManager(db_name=database, force_mock=False)
    try:
        # Fixture adicional de almacenamiento: NO es una captura de un portal.
        extra = tmp_path / 'prepared/sources/fixture_integridad.html'
        extra.parent.mkdir(parents=True)
        extra.write_bytes(b'<html>fixture declarado\r\n</html>\r\n')
        result = run_pipeline(tmp_path / 'prepared', tmp_path / 'processed', snapshot_dir=snapshot,
                              db_name=database, topic=topic, interval_seconds=0.005)
        assert result['modo'] == 'real'
        assert set(result['servicios'].values()) == {'real'}
        assert result['anuncios_publicados'] == result['anuncios_recibidos'] == result['registros_persistidos'] > 0
        assert result['por_tipo_registro'] == {'promocion': result['registros_persistidos']}
        assert result['por_fuente']['OpenDataEuskadi_Visesa'] > 0
        assert result['por_fuente']['OpenDataEuskadi_Etxebide_CSV'] > 0
        assert all(item['recuperacion_identica'] and item['modo'] == 'webhdfs_live' for item in result['hdfs'])
        originals_in_hdfs = {Path(item['original_local']).name for item in result['hdfs'] if item['clase'] == 'raw'}
        assert set(sources) | {'manifest.json'} <= originals_in_hdfs
        assert 'fixture_integridad.html' in originals_in_hdfs
        documents = list(manager.db.viviendas.find({}, {'_id': 0}))
        assert len(documents) == result['registros_persistidos']
        codes = {doc['codigo_municipio'] for doc in documents}
        assert len(codes) == manager.db.municipios.count_documents({})
        assert all(doc['es_sintetico'] is False for doc in documents)
        assert all(doc['lote_ingesta'] == result['lote_ingesta'] for doc in documents)
        assert all(doc['procedencia']['sha256'] == sources[doc['procedencia']['archivo']]['sha256'] for doc in documents)
        assert all(doc['economia_laboral']['salario_medio_joven_mes'] is None for doc in manager.db.municipios.find())
        assert all(doc['contexto_autonomico']['salario_ovj']['es_salario_municipal'] is False for doc in manager.db.municipios.find())
        assert result['municipios_con_precios'] == 0 and result['municipios_con_salario'] == 0
        assert json.loads((tmp_path / 'processed/estadisticas_por_municipio.json').read_text()) == []
        summaries = json.loads((tmp_path / 'processed/promociones_por_municipio.json').read_text())
        assert sum(row['registros_catalogo'] for row in summaries) == len(documents)
        assert verify_snapshot(snapshot) == sources

        # Cargar de nuevo las mismas identidades no duplica ni borra contadores.
        from src.extraction.source_snapshots import MunicipalityCatalog
        loader = MongoDBDataLoader(manager.db, municipality_catalog=MunicipalityCatalog.from_snapshot(snapshot))
        first = documents[0]
        key = {'fuente': first['fuente'], 'id_origen': first['id_origen']}
        manager.db.viviendas.update_one(key, {'$set': {'solicitudes_interes_joven': 3}})
        assert loader.cargar_anuncios(documents) == (len(documents), 0)
        assert manager.db.viviendas.count_documents({}) == len(documents)
        assert manager.db.viviendas.find_one(key)['solicitudes_interes_joven'] == 3

        evidence = Path('evidencia_bda_integracion')
        evidence.mkdir(exist_ok=True)
        report = {
            'run': os.getenv('GITHUB_RUN_ID'), 'commit_base': os.getenv('GITHUB_SHA'),
            'propuesta_sha': os.getenv('BDA_CANDIDATE_TREE'),
            'datos': 'registros de capturas oficiales verificados; HTML auxiliar etiquetado como fixture',
            'archivos_auxiliares_fixture': ['fixture_integridad.html; solo prueba almacenamiento, no anuncios'],
            'servicios': result['servicios'], 'lote_ingesta': result['lote_ingesta'],
            'enviados': result['anuncios_publicados'], 'recibidos': result['anuncios_recibidos'],
            'persistidos': result['registros_persistidos'], 'por_fuente': result['por_fuente'],
            'municipios': len(codes), 'catalogo_ine_municipios': result['preparacion']['catalogo_ine_municipios'],
            'promociones_por_municipio_y_fuente': summaries,
            'rechazos_preparacion': result['preparacion']['rechazos'],
            'rechazos_ingesta': result['rechazados'], 'procedencia_conservada': True,
            'recarga_idempotente': True, 'contador_interes_conservado': True,
            'salario_referencia': result['preparacion']['salario_ovj'],
            'salarios_municipales_inventados': False, 'originales': list(sources.values()),
            'hdfs': [{k: v for k, v in item.items() if k != 'original_local'} for item in result['hdfs']],
            'limites': result['limites'],
            'scraping_portales_validado': False,
            'indicadores_mercado_libre_completos': False,
        }
        (evidence / 'resumen.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({k: v for k, v in report.items() if k not in {'originales', 'hdfs', 'promociones_por_municipio_y_fuente', 'rechazos_preparacion'}}, ensure_ascii=False, indent=2))
    finally:
        manager.drop_database()
        manager.close()
