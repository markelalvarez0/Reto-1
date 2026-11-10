"""
Pruebas unitarias y de integración para el módulo MongoDB / PyMongo de SBD.
Valida carga, modelado, limpieza, consultas avanzadas, aggregations, índices y atomicidad.
"""
import pytest
from pathlib import Path
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader
from src.database.cleaning import MongoDataCleaner
from src.database.queries import MongoHousingQueries
from src.database.aggregations import MongoHousingAggregations
from src.database.indexes import MongoIndexOptimizer
from src.database.consistency import MongoConsistencyManager


@pytest.fixture(scope="module")
def mongo_env():
    """Inicializa una base de datos de pruebas en memoria con mongomock."""
    mgr = MongoDBManager(force_mock=True, db_name="test_sbd_vivienda")
    loader = MongoDBDataLoader(mgr.db, allow_demo=True)
    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    res = loader.cargar_datos_base(raw_dir)
    cleaner = MongoDataCleaner(mgr.db)
    cleaner.ejecutar_pipeline_limpieza()
    
    yield {
        "db": mgr.db,
        "is_mock": mgr.is_mock,
        "mgr": mgr
    }
    mgr.drop_database()
    mgr.close()


def test_mongo_data_loader_structure(mongo_env):
    """Verifica que las colecciones 'municipios' y 'viviendas' tienen documentos con embedding y referencing."""
    db = mongo_env["db"]
    assert db["municipios"].count_documents({}) >= 5
    assert db["viviendas"].count_documents({}) >= 10
    
    # Comprobar embedding en municipios
    bilbao = db["municipios"].find_one({"municipio": "Bilbao"})
    assert "programas_ayuda" in bilbao
    assert isinstance(bilbao["programas_ayuda"], list)
    assert len(bilbao["programas_ayuda"]) >= 1

    # Comprobar referencing en viviendas
    vivienda = db["viviendas"].find_one({"municipio": "Bilbao"})
    assert "precio_m2" in vivienda
    assert "categoria_accesibilidad" in vivienda


def test_mongo_advanced_queries(mongo_env):
    """Verifica la ejecución de las 5 consultas analíticas."""
    db = mongo_env["db"]
    queries = MongoHousingQueries(db)
    
    # Q1: Igualdad
    q1 = queries.consulta_1_alquileres_en_municipio("Bilbao")
    assert isinstance(q1, list)
    assert len(q1) > 0
    
    # Q2: Comparación
    q2 = queries.consulta_2_alquileres_asequibles_jovenes(800.0)
    assert isinstance(q2, list)
    for v in q2:
        assert v["precio"] <= 800.0

    # Q3: Combinada
    q3 = queries.consulta_3_condiciones_combinadas("Bilbao", 1000.0, 50.0)
    assert isinstance(q3, list)

    # Q4: Campos anidados
    q4 = queries.consulta_4_campos_anidados_confort(2, True)
    assert isinstance(q4, list)
    assert len(q4) > 0

    # Q5: Arrays
    q5 = queries.consulta_5_municipios_programas_array("Gaztelagun")
    assert isinstance(q5, list)
    assert len(q5) >= 3


def test_mongo_aggregation_pipelines(mongo_env):
    """Verifica los 3 pipelines de agregación ($group, $lookup/$unwind, $facet)."""
    db = mongo_env["db"]
    aggs = MongoHousingAggregations(db, include_synthetic=True)

    # Pipeline 1: Agrupación por municipio
    res_agg1 = aggs.pipeline_1_estadisticas_alquiler_por_municipio()
    assert len(res_agg1) >= 3
    for m in res_agg1:
        assert "precio_medio" in m
        assert "total_anuncios" in m

    # Pipeline 2: $lookup y $unwind
    res_agg2 = aggs.pipeline_2_cruce_esfuerzo_salarial()
    assert len(res_agg2) > 0
    primero = res_agg2[0]
    assert "tasa_esfuerzo_pct" in primero
    assert "salario_medio_joven" in primero

    # Pipeline 3: $facet
    res_agg3 = aggs.pipeline_3_facet_distribucion_y_top()
    assert "distribucion_accesibilidad" in res_agg3
    assert "top_asequibles" in res_agg3
    assert "desglose_por_tipo" in res_agg3


def test_mongo_index_optimizer(mongo_env):
    """Verifica creación de índices y comparación explain()."""
    db = mongo_env["db"]
    opt = MongoIndexOptimizer(db, is_mock=mongo_env["is_mock"])
    indices = opt.crear_indices()
    assert "indice_simple" in indices
    assert "indice_compuesto" in indices

    stats = opt.comparar_rendimiento_consulta("Bilbao", 850.0)
    assert stats["estado"] == "NO_DISPONIBLE_EN_MOCK"
    assert stats["sin_indice"] is None
    assert stats["con_indice"] is None


def test_mongo_atomic_consistency(mongo_env):
    """Verifica operaciones atómicas y justificación técnica."""
    db = mongo_env["db"]
    cons = MongoConsistencyManager(db)
    
    # Crear un registro demo para probar find_one_and_update
    db["viviendas"].insert_one({"id_origen": "test_atomico", "solicitudes_interes_joven": 0})
    res_atom = cons.registrar_interes_joven_atomico("test_atomico")
    assert res_atom["atomicidad_garantizada"] is True
    assert res_atom["solicitudes_interes_joven"] == 1

    just = cons.obtener_justificacion_tecnica()
    assert "justificacion" in just
    assert "WiredTiger" in just["justificacion"] or "atómica" in just["justificacion"]
