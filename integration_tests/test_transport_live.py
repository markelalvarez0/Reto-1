"""HDFS y Kafka reales: fixtures explicitos, recuperacion SHA y entrega a MongoDB."""
import json
import os
from pathlib import Path
import time
import uuid
import pytest
from src.hdfs.client import HDFSClient
from src.kafka.producer import HousingKafkaProducer
from src.kafka.consumer import HousingKafkaConsumer
from src.extraction.models import HousingAd
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader

pytestmark=pytest.mark.skipif(os.getenv('TRANSPORT_LIVE')!='1',reason='Requiere servicios reales preparados')


def test_hdfs_original_y_procesado_reales(tmp_path):
    hdfs=HDFSClient(simulation_mode=False)
    evidence=[]
    for kind,payload in [('raw',b'id;codigo_municipio\n1;01059\n'),('processed',b'{"id":"1","codigo_municipio":"01059"}')]:
        path=tmp_path/kind;path.write_bytes(payload)
        remote=f'/data/reto1/{kind}/{uuid.uuid4().hex}/datos'
        response=hdfs.upload_file(str(path),remote)
        assert response.exito and response.modo=='webhdfs_live'
        recovered=tmp_path/(kind+'_recuperado')
        hdfs.download_file(remote,str(recovered))
        assert recovered.read_bytes()==payload
        assert hdfs.calculate_sha256(str(recovered))==response.checksum_sha256
        evidence.append(response.model_dump())
    out=Path('test-results');out.mkdir(exist_ok=True)
    (out/'hdfs-live.json').write_text(json.dumps({'datos':'fixtures','recuperaciones':evidence},indent=2))


def test_kafka_real_persiste_en_mongodb_sin_mock():
    from kafka import KafkaAdminClient
    error=None
    for _ in range(30):
        try:
            admin=KafkaAdminClient(bootstrap_servers='localhost:9092',request_timeout_ms=5000)
            admin.list_topics();admin.close();break
        except Exception as exc:
            error=exc;time.sleep(2)
    else:raise RuntimeError('Kafka no disponible') from error
    token=uuid.uuid4().hex
    manager=MongoDBManager(db_name='reto1_transporte_'+token,force_mock=False)
    loader=MongoDBDataLoader(manager.db)
    producer=HousingKafkaProducer(topic='reto1_ci_'+token,simulation_mode=False)
    consumer=HousingKafkaConsumer(topic='reto1_ci_'+token,group_id='reto1_ci_'+token,simulation_mode=False)
    try:
        ads=[HousingAd(id=str(i),fuente='fixture_ci',municipio='Bilbao',tipo_operacion='alquiler',precio=600+i,es_sintetico=True) for i in range(5)]
        assert producer.simulation_mode is False and consumer.simulation_mode is False
        assert producer.stream_ads(ads,interval_seconds=0)==5
        def persist(ad,count):
            assert loader.cargar_anuncios([ad.to_dict()])==(1,0)
        received=consumer.consume_batch(max_messages=5,timeout_seconds=45,on_message_callback=persist)
        assert [ad.id for ad in received]==[str(i) for i in range(5)]
        assert manager.db.viviendas.count_documents({})==5
        out=Path('test-results');out.mkdir(exist_ok=True)
        (out/'kafka-live.json').write_text(json.dumps({'servicio':'Apache Kafka real -> MongoDB real','datos':'fixtures_ci_sinteticos','enviados':5,'recibidos':len(received),'persistidos':manager.db.viviendas.count_documents({}),'orden_misma_clave_ine':True},indent=2))
    finally:
        producer.close();consumer.close();manager.drop_database();manager.close()
