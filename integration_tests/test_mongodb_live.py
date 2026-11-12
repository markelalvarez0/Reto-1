"""Pruebas contra mongod real. Los registros son fixtures, no datos de mercado."""
import json
import os
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader
from src.database.cleaning import MongoDataCleaner
from src.database.aggregations import MongoHousingAggregations
from src.database.indexes import MongoIndexOptimizer
from src.database.consistency import MongoConsistencyManager
from src.database.queries import MongoHousingQueries


@pytest.fixture
def db():
    uri = os.environ.get('MONGO_INTEGRATION_URI')
    if not uri:
        pytest.skip('Se requiere MONGO_INTEGRATION_URI para probar un mongod real')
    manager = MongoDBManager(uri=uri, db_name='reto1_ci_' + uuid.uuid4().hex)
    assert manager.is_mock is False
    yield manager.db
    manager.drop_database()
    manager.close()


def rows():
    return [{'id': str(i), 'fuente': 'fixture_ci', 'municipio': 'Bilbao' if i < 10 else 'Getxo',
             'codigo_municipio': '48020' if i < 10 else '48044', 'tipo_operacion': 'alquiler',
             'precio': 600 + i, 'superficie_m2': 60, 'es_sintetico': False} for i in range(100)]


def test_carga_limpieza_e_idempotencia_real(db):
    loader = MongoDBDataLoader(db)
    loader.cargar_anuncios(rows()); loader.cargar_anuncios(rows())
    assert db.viviendas.count_documents({}) == 100
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    doc = db.viviendas.find_one({'id_origen': '0'})
    assert doc['precio_m2'] == 10 and doc['caracteristicas']['ascensor'] is None


def test_tres_agregaciones_y_cruce_ine_real(db):
    loader = MongoDBDataLoader(db)
    loader.cargar_anuncios(rows())
    loader.cargar_municipios([{'municipio': 'BILBAO', 'codigo_municipio': '48020', 'es_sintetico': False,
                               'economia_laboral': {'salario_medio_joven_mes': 1500.}}])
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    aggs = MongoHousingAggregations(db)
    assert len(aggs.pipeline_1_estadisticas_alquiler_por_municipio()) == 2
    efforts = aggs.pipeline_2_cruce_esfuerzo_salarial()
    assert efforts[0]['tasa_esfuerzo_pct'] == 40
    assert len([row for row in efforts if row['tasa_esfuerzo_pct'] is None]) == 90
    assert len(aggs.pipeline_3_facet_distribucion_y_top()['top_asequibles']) == 5
    assert len(aggs.indicadores_municipales()) == 2


def test_explain_real_sin_eliminar_indices(db):
    MongoDBDataLoader(db).cargar_anuncios(rows())
    db.viviendas.create_index('fuente', name='indice_ajeno')
    measured = MongoIndexOptimizer(db).comparar_rendimiento_consulta()
    assert measured['estado'] == 'MEDIDO_EN_MONGODB'
    assert measured['sin_indice']['stage'] == 'COLLSCAN'
    assert measured['con_indice']['stage'] == 'IXSCAN'
    assert measured['con_indice']['totalDocsExamined'] < measured['sin_indice']['totalDocsExamined']
    assert measured['sin_indice']['nReturned'] == measured['con_indice']['nReturned'] == 10
    assert 'indice_ajeno' in db.viviendas.index_information()
    out = Path(os.getenv('EVIDENCE_DIR', 'test-results')); out.mkdir(exist_ok=True)
    measured['tipo_datos'] = 'fixtures_ci_no_mercado'
    (out / 'mongo_explain_real.json').write_text(json.dumps(measured, indent=2, default=str))


def test_atomicidad_concurrente_real(db):
    db.viviendas.insert_one({'fuente': 'ci', 'id_origen': 'contador', 'solicitudes_interes_joven': 0})
    manager = MongoConsistencyManager(db)
    with ThreadPoolExecutor(max_workers=8) as pool:
        result = list(pool.map(lambda _: manager.registrar_interes_joven_atomico('contador', 'ci'), range(100)))
    assert all(row['atomicidad_garantizada'] for row in result)
    assert db.viviendas.find_one()['solicitudes_interes_joven'] == 100


def test_crud_comprobado_real(db):
    record = {'fuente': 'ci', 'id_origen': 'crud', 'precio': 600}
    identity = db.viviendas.insert_one(record).inserted_id
    assert db.viviendas.find_one({'_id': identity})['precio'] == 600
    assert db.viviendas.update_one({'_id': identity}, {'$set': {'precio': 700}}).modified_count == 1
    assert db.viviendas.find_one({'_id': identity})['precio'] == 700
    assert db.viviendas.delete_one({'_id': identity}).deleted_count == 1
    assert db.viviendas.find_one({'_id': identity}) is None


def test_nulos_reales_no_se_transforman_en_asequibilidad(db):
    db.viviendas.insert_one({'id_origen': 'nulo', 'fuente': 'ci', 'tipo_operacion': 'alquiler', 'precio': 'sin precio'})
    MongoDataCleaner(db).ejecutar_pipeline_limpieza()
    assert db.viviendas.find_one()['categoria_accesibilidad'] == 'SIN_DATOS'


def test_consultas_separan_anuncios_de_promociones_y_fixtures(db):
    base = {'municipio': 'Bilbao', 'tipo_operacion': 'alquiler', 'precio': 700,
            'superficie_m2': 60, 'es_sintetico': False, 'tipo_registro': 'anuncio',
            'caracteristicas': {'habitaciones': 2, 'ascensor': True},
            'procedencia': {'condiciones_publicadas': ['temporal']}}
    # Todos son fixtures declarados; es_sintetico=False ejercita el filtro de producción.
    db.viviendas.insert_many([
        {**base, 'id_origen': 'observado_fixture'},
        {**base, 'id_origen': 'promocion_fixture', 'tipo_registro': 'promocion'},
        {**base, 'id_origen': 'demo_fixture', 'es_sintetico': True},
        {**base, 'id_origen': 'sin_precio_fixture', 'precio': None},
    ])
    queries = MongoHousingQueries(db)
    for result in (queries.consulta_1_alquileres_en_municipio(),
                   queries.consulta_2_alquileres_asequibles_jovenes(),
                   queries.consulta_3_condiciones_combinadas(),
                   queries.consulta_4_campos_anidados_confort(),
                   queries.consulta_6_condiciones_publicadas()):
        assert len(result) == 1
    db.viviendas.update_one({'id_origen': 'observado_fixture'}, {'$set': {'caracteristicas.ascensor': None}})
    assert queries.consulta_4_campos_anidados_confort() == []
    assert len(queries.consulta_4_campos_anidados_confort(ascensor=None)) == 1
