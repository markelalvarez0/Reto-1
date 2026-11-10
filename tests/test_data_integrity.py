"""Regresiones de integridad: ninguna cifra inventada debe parecer observada."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import mongomock
import pytest
from bs4 import BeautifulSoup

from src.database.data_loader import MongoDBDataLoader
from src.database.cleaning import MongoDataCleaner
from src.database.aggregations import MongoHousingAggregations
from src.database.indexes import MongoIndexOptimizer
from src.database.consistency import MongoConsistencyManager
from src.extraction.normalization import numero_observado, booleano_observado
from src.extraction.multi_portal_scraper import MultiPortalHousingScraper


@pytest.fixture
def db():
    return mongomock.MongoClient()['test_integridad']


def anuncio(**overrides):
    return {'id': 'a1', 'fuente': 'fuente_observada', 'municipio': 'Bilbao', 'codigo_municipio': '48020',
            'tipo_operacion': 'alquiler', 'precio': 600., 'superficie_m2': 60., 'es_sintetico': False, **overrides}


def test_no_rellena_medidas_ausentes_y_respeta_false(db):
    doc = MongoDBDataLoader(db)._normalizar_anuncio(anuncio(precio=None, superficie_m2=None, ascensor=False, fianza_meses=0))
    assert doc['precio'] is None and doc['superficie_m2'] is None and doc['precio_m2'] is None
    assert doc['caracteristicas']['ascensor'] is False
    assert doc['caracteristicas']['fianza_meses'] == 0
    assert doc['caracteristicas']['habitaciones'] is None


@pytest.mark.parametrize('raw,expected', [('1.200,50', 1200.5), ('950,25', 950.25), ('75.5', 75.5), ('1.200', 1200.), ('NaN', None), (float('inf'), None), (True, None), ('-1', None)])
def test_numeros_observados(raw, expected):
    assert numero_observado(raw) == expected


@pytest.mark.parametrize('raw,expected', [('false', False), ('True', True), (None, None), ('desconocido', None)])
def test_booleanos_observados(raw, expected):
    assert booleano_observado(raw) is expected


def test_carga_no_borra_ni_duplica_y_conserva_intereses(db, tmp_path):
    data = [anuncio()]
    (tmp_path / 'vivienda_real.json').write_text(json.dumps(data))
    loader = MongoDBDataLoader(db)
    assert loader.cargar_datos_base(tmp_path)['viviendas'] == 1
    doc = db.viviendas.find_one()
    db.viviendas.update_one({'_id': doc['_id']}, {'$set': {'solicitudes_interes_joven': 4}})
    loader.cargar_datos_base(tmp_path)
    assert db.viviendas.count_documents({}) == 1
    assert db.viviendas.find_one()['_id'] == doc['_id']
    assert db.viviendas.find_one()['solicitudes_interes_joven'] == 4


def test_directorio_vacio_no_genera_mercado(db, tmp_path):
    assert MongoDBDataLoader(db).cargar_datos_base(tmp_path) == {'viviendas': 0, 'municipios': 0, 'rechazados': 0}
    assert db.viviendas.count_documents({}) == 0


def test_csv_preserva_ceros_ine_y_rechazos(db, tmp_path):
    (tmp_path / 'vivienda_real.csv').write_text('id;fuente;municipio;codigo_municipio;tipo_operacion;precio;superficie_m2;ascensor;es_sintetico\na;csv;Vitoria-Gasteiz;01059;alquiler;700,50;70;false;false\nb;csv;No existe;48020;alquiler;700;60;true;false\n')
    counts = MongoDBDataLoader(db).cargar_datos_base(tmp_path)
    assert counts['viviendas'] == 1 and counts['rechazados'] == 1
    assert db.viviendas.find_one()['codigo_municipio'] == '01059'
    assert db.viviendas.find_one()['caracteristicas']['ascensor'] is False
    assert db.rechazos_ingesta.count_documents({}) == 1


def test_deduplicacion_separa_fuentes(db):
    db.viviendas.insert_many([{'fuente': f, 'id_origen': '1', 'precio': 900, 'superficie_m2': 60, 'tipo_operacion': 'alquiler'} for f in ['A', 'A', 'B']])
    stats = MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    assert stats['duplicados_eliminados'] == 1
    assert db.viviendas.count_documents({}) == 2


def test_limpieza_no_imputa_precio_o_ascensor(db):
    db.viviendas.insert_one({'id_origen': '1', 'fuente': 'A', 'precio': 'sin precio', 'superficie_m2': None, 'tipo_operacion': 'ALQUILER'})
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    doc = db.viviendas.find_one()
    assert doc['precio'] is None and doc['precio_m2'] is None
    assert doc['caracteristicas']['ascensor'] is None
    assert doc['categoria_accesibilidad'] == 'SIN_DATOS'
    assert doc['valores_originales']['precio'] == 'sin precio'


def test_lookup_bilingue_calcula_en_mongodb(db):
    MongoDBDataLoader(db).cargar_anuncios([anuncio(municipio='Donostia', codigo_municipio='20069', precio=900)])
    db.municipios.insert_one({'municipio': 'San Sebastian', 'codigo_municipio': '20069', 'es_sintetico': False,
                              'economia_laboral': {'salario_medio_joven_mes': 1500.}})
    result = MongoHousingAggregations(db).pipeline_2_cruce_esfuerzo_salarial()
    assert len(result) == 1
    assert result[0]['tasa_esfuerzo_pct'] == 60.


@pytest.mark.parametrize('salary', [None, 0, -1, 'desconocido'])
def test_salario_invalido_no_se_imputa(db, salary):
    MongoDBDataLoader(db).cargar_anuncios([anuncio()])
    db.municipios.insert_one({'codigo_municipio': '48020', 'es_sintetico': False, 'salario_medio_joven_mes': salary})
    rows = MongoHousingAggregations(db).pipeline_2_cruce_esfuerzo_salarial()
    assert len(rows) == 1 and rows[0]['tasa_esfuerzo_pct'] is None


def test_no_hay_join_ni_denominador_demo(db):
    MongoDBDataLoader(db).cargar_anuncios([anuncio()])
    assert MongoHousingAggregations(db).pipeline_2_cruce_esfuerzo_salarial()[0]['tasa_esfuerzo_pct'] is None
    db.municipios.insert_one({'codigo_municipio': '48020', 'es_sintetico': True, 'salario_medio_joven_mes': 1500})
    assert MongoHousingAggregations(db).pipeline_2_cruce_esfuerzo_salarial()[0]['tasa_esfuerzo_pct'] is None


def test_estadisticas_excluyen_demo_compra_y_nulos(db):
    MongoDBDataLoader(db).cargar_anuncios([anuncio(), anuncio(id='demo', precio=1, es_sintetico=True), anuncio(id='compra', precio=300000, tipo_operacion='compraventa'), anuncio(id='nulo', precio=None)])
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    rows = MongoHousingAggregations(db).pipeline_1_estadisticas_alquiler_por_municipio()
    assert rows[0]['total_anuncios'] == 1 and rows[0]['precio_medio'] == 600
    assert MongoHousingAggregations(db).pipeline_3_facet_distribucion_y_top()['top_asequibles'][0]['precio'] == 600


def test_cinco_indicadores_y_cobertura(db):
    MongoDBDataLoader(db).cargar_anuncios([anuncio()])
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    db.municipios.insert_one({'codigo_municipio': '48020', 'es_sintetico': False, 'salario_medio_joven_mes': 2000})
    row = MongoHousingAggregations(db).indicadores_municipales()[0]
    assert row['total_anuncios'] == 1 and row['precio_medio'] == 600
    assert row['precio_m2_medio'] == 10 and row['esfuerzo_medio_pct'] == 30
    assert row['porcentaje_asequibles'] == 100 and row['anuncios_con_salario'] == 1


def test_explain_mock_no_fabrica_resultados(db):
    assert MongoIndexOptimizer(db).comparar_rendimiento_consulta()['con_indice'] is None


def test_atomicidad_concurrencia_y_timestamp(db):
    db.viviendas.insert_one({'fuente': 'demo', 'id_origen': 'contador', 'solicitudes_interes_joven': 0})
    manager = MongoConsistencyManager(db)
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda _: manager.registrar_interes_joven_atomico('contador', 'demo'), range(30)))
    doc = db.viviendas.find_one()
    assert doc['solicitudes_interes_joven'] == 30
    assert doc['ultima_consulta_timestamp'].year >= 2026


def test_scraper_no_asigna_localidad_ni_medidas_fijas():
    scraper = MultiPortalHousingScraper()
    html = '<article class="anuncio">Piso sin localidad 900 EUR</article>'
    assert scraper._parsear_html('Test', BeautifulSoup(html, 'html.parser')) == []
    scraper._source_url = 'https://example.org/alquiler/'
    payload = {'@type': 'Apartment', 'address': {'addressLocality': 'Getxo'}, 'offers': {'price': '900', 'priceCurrency': 'EUR'}, 'url': '/inmueble/1'}
    html = '<script type="application/ld+json">'+json.dumps(payload)+'</script>'
    ad = scraper._parsear_html('Test', BeautifulSoup(html, 'html.parser'))[0]
    assert ad.codigo_municipio == '48044' and ad.superficie_m2 is None and ad.ascensor is None
    assert ad.es_sintetico is False


def test_hdfs_caido_nunca_activa_emulacion_implicitamente(monkeypatch, tmp_path):
    import requests
    from src.hdfs.client import HDFSClient
    def error(*args, **kwargs):
        raise requests.ConnectionError('servicio no disponible')
    monkeypatch.setattr(requests, 'get', error)
    client = HDFSClient(simulation_mode=False, simulation_storage_dir=str(tmp_path))
    for _ in range(2):
        with pytest.raises(ConnectionError):
            client.is_live_cluster_available()


def test_kafka_caido_nunca_activa_emulacion(monkeypatch):
    import kafka
    from src.kafka.producer import HousingKafkaProducer
    def error(*args, **kwargs):
        raise RuntimeError('broker caido')
    monkeypatch.setattr(kafka, 'KafkaProducer', error)
    with pytest.raises(ConnectionError):
        HousingKafkaProducer(simulation_mode=False)


def test_callback_fallido_no_se_presenta_como_consumo_correcto():
    from src.kafka.mock_broker import InMemoryKafkaBroker
    from src.kafka.producer import HousingKafkaProducer
    from src.kafka.consumer import HousingKafkaConsumer
    from src.extraction.models import HousingAd
    InMemoryKafkaBroker.reset()
    producer = HousingKafkaProducer(simulation_mode=True)
    consumer = HousingKafkaConsumer(simulation_mode=True)
    producer.publish_ad(HousingAd(**anuncio()))
    def fallo(*args):
        raise RuntimeError('fallo persistencia')
    with pytest.raises(RuntimeError, match='persistencia'):
        consumer.consume_batch(max_messages=1, on_message_callback=fallo)


def test_pipeline_demo_integral_y_exportaciones(tmp_path):
    from scripts.run_pipeline import run_pipeline
    result = run_pipeline(tmp_path / 'raw', tmp_path / 'processed', demo=True)
    assert result['modo'] == 'demo'
    assert result['anuncios_publicados'] == result['anuncios_recibidos'] > 0
    assert all(item['modo'] == 'local_simulation' for item in result['hdfs'])
    for name in ('estadisticas_por_municipio', 'indicadores_municipales', 'distribuciones'):
        assert json.loads((tmp_path / 'processed' / f'{name}.json').read_text())
