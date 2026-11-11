"""Vistas observadas: HDFS -> Kafka -> MongoDB, recarga sin duplicados."""
import os
from pathlib import Path
import subprocess
import sys
import uuid
import pytest
from scripts.transport_municipal import transport
from src.database.mongo_client import MongoDBManager

pytestmark = pytest.mark.skipif(os.getenv('BDA_LIVE') != '1', reason='Requiere HDFS/Kafka/MongoDB reales')
ROOT = Path(__file__).resolve().parents[1]


def test_municipal_views_cross_real_services(tmp_path):
    database = 'reto1_municipal_transport_' + uuid.uuid4().hex
    manager = MongoDBManager(db_name=database)
    try:
        subprocess.run([sys.executable, str(ROOT / 'scripts/analyze_municipal.py'),
                        '--db-name', database, '--output-dir', str(tmp_path)], cwd=ROOT, check=True)
        for _ in range(2):
            report = transport(tmp_path, manager.db)
            assert report['recibidos'] == 5
            assert set(report['servicios'].values()) == {'real'}
            assert all(row['recuperacion_identica'] for row in report['hdfs'])
            assert manager.db.vistas_municipales.count_documents({}) == 5
        comparison = manager.db.vistas_municipales.find_one({'archivo': 'comparativa_municipal.json'})['contenido']
        assert len(comparison) == 18
        assert next(r for r in comparison if r['codigo_municipio'] == '48020')['renta_media_eur'] == 930.31
    finally:
        manager.drop_database()
        manager.close()
