"""Transporta vistas municipales verificadas por HDFS y Kafka hasta MongoDB.

Los mensajes son vistas agregadas, nunca anuncios individuales. Solo servicios
reales; el offset se confirma después de persistir y verificar la huella.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.database.mongo_client import MongoDBManager
from src.hdfs.client import HDFSClient

FILES = {'comparativa_municipal.json', 'resumen_territorial.json',
         'serie_trimestral.json', 'mapa_promociones.json', 'metadatos.json'}


def load_verified(folder):
    """Lee todos los bytes antes de producir efectos en servicios externos."""
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if len(manifest) != len(FILES) or {r['archivo'] for r in manifest} != FILES:
        raise ValueError('Manifiesto municipal incompleto o duplicado')
    payloads = {}
    for item in manifest:
        data = (folder / item['archivo']).read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Huella municipal incorrecta: ' + item['archivo'])
        payloads[item['archivo']] = data
    if json.loads(payloads['metadatos.json'])['motor'] != 'MongoDB':
        raise ValueError('El transporte real requiere analisis de MongoDB real')
    return payloads


def transport(folder, db, bootstrap=None, topic=None):
    """Reenvíos conservan una vista por nombre y huella; no borran otras vistas."""
    from kafka import KafkaProducer, KafkaConsumer
    payloads = load_verified(folder)
    bootstrap = bootstrap or os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic = topic or 'reto1-municipal-' + uuid.uuid4().hex
    batch = uuid.uuid4().hex
    hdfs = HDFSClient(simulation_mode=False)
    hdfs_results = []
    # Leer de HDFS antes de publicar: Kafka recibe los bytes recuperados.
    recovered = {}
    with tempfile.TemporaryDirectory() as temporary:
        for name, data in sorted(payloads.items()):
            source = Path(temporary) / name
            source.write_bytes(data)
            target = '/data/reto1/processed/municipal/' + batch + '/' + name
            uploaded = hdfs.upload_file(str(source), target)
            if not uploaded.exito or uploaded.modo != 'webhdfs_live':
                raise RuntimeError('No se acredito HDFS real')
            restored = Path(temporary) / ('recuperado_' + name)
            hdfs.download_file(target, str(restored))
            recovered[name] = restored.read_bytes()
            if recovered[name] != data:
                raise ValueError('HDFS altero los bytes: ' + name)
            hdfs_results.append({'archivo': name, 'hdfs_path': target,
                                 'sha256': hashlib.sha256(data).hexdigest(), 'recuperacion_identica': True})
    db.vistas_municipales.create_index([('archivo', 1), ('sha256', 1)], unique=True)
    producer = KafkaProducer(bootstrap_servers=bootstrap.split(','), acks='all', retries=3)
    consumer = None
    try:
        for name, data in recovered.items():
            event = {'tipo': 'vista_municipal', 'lote': batch, 'archivo': name,
                     'sha256': hashlib.sha256(data).hexdigest(), 'contenido': data.decode('utf-8')}
            producer.send(topic, key=name.encode(), value=json.dumps(event, ensure_ascii=False).encode()).get(timeout=30)
        producer.flush(timeout=30)
        consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap.split(','),
                                 group_id='municipal-' + batch, auto_offset_reset='earliest', enable_auto_commit=False)
        received = set()
        deadline = time.monotonic() + 90
        while len(received) < len(payloads) and time.monotonic() < deadline:
            for messages in consumer.poll(timeout_ms=1000).values():
                for message in messages:
                    event = json.loads(message.value)
                    if event.get('lote') != batch or event.get('tipo') != 'vista_municipal':
                        raise ValueError('Lote o tipo inesperado en el topico municipal')
                    name, data = event['archivo'], event['contenido'].encode('utf-8')
                    if name not in payloads or data != payloads[name] or hashlib.sha256(data).hexdigest() != event['sha256']:
                        raise ValueError('Kafka altero el contenido municipal')
                    key = {'archivo': name, 'sha256': event['sha256']}
                    db.vistas_municipales.update_one(key, {'$set': {'tipo': event['tipo'],
                        'contenido': json.loads(data), 'lote_ultimo': batch}}, upsert=True)
                    stored = db.vistas_municipales.find_one(key)
                    if stored['contenido'] != json.loads(data):
                        raise RuntimeError('Persistencia municipal no confirmada')
                    received.add(name)
            # Todos los mensajes del poll se han persistido antes de confirmar.
            consumer.commit()
        if received != FILES:
            raise TimeoutError('No llegaron todas las vistas municipales')
        return {'servicios': {'hdfs': 'real', 'kafka': 'real', 'mongodb': 'real'},
                'tipo': 'vistas municipales agregadas; no anuncios', 'lote': batch, 'topic': topic,
                'recibidos': len(received), 'hdfs': hdfs_results, 'offsets_tras_persistencia': True}
    finally:
        if consumer is not None:
            consumer.close(autocommit=False)
        producer.close(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--db-name', default='reto1_analisis_municipal')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    manager = MongoDBManager(db_name=args.db_name)
    try:
        result = transport(args.input_dir, manager.db)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False))
    finally:
        manager.close()


if __name__ == '__main__':
    main()
