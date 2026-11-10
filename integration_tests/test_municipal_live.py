"""Agregación EMAL/OVJ con mongod real; no modifica el modelo de ML."""
import os
from pathlib import Path
import uuid
import pytest
from src.database.mongo_client import MongoDBManager
from src.municipal_analysis import analyze


def test_municipal_analysis_live():
    uri = os.getenv('MONGO_INTEGRATION_URI')
    if not uri:
        pytest.skip('Se requiere MONGO_INTEGRATION_URI')
    manager = MongoDBManager(uri=uri, db_name='reto1_municipal_test_' + uuid.uuid4().hex)
    try:
        snapshot = Path(__file__).resolve().parents[1] / 'data/capturas_oficiales'
        first = analyze(manager.db, snapshot)
        assert analyze(manager.db, snapshot) == first
        assert manager.db.rentas_emal.count_documents({}) == 768
        assert len(first['comparativa_municipal']) == 18
        bilbao = next(r for r in first['comparativa_municipal'] if r['codigo_municipio'] == '48020')
        assert bilbao['renta_media_eur'] == pytest.approx(930.31)
        assert bilbao['esfuerzo_escenario_pct'] == pytest.approx(930.31 / 1564 * 100)
        assert len(first['resumen_territorial']) == 3
    finally:
        manager.drop_database()
        manager.close()
