"""Originales API EMAL → HDFS → Kafka → colección rentas_api. No toca ML."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.capture_emal_api import verified
from src.hdfs.client import HDFSClient
from src.database.mongo_client import MongoDBManager


def transport(folder, db):
    """Reentrega idempotente por municipio/periodo/huella, offset tras persistencia."""
    from kafka import KafkaProducer, KafkaConsumer
    folder=Path(folder);rows=verified(folder);batch=uuid.uuid4().hex
    hdfs=HDFSClient(simulation_mode=False);files=[];recovered=None
    with tempfile.TemporaryDirectory() as scratch:
        for file in sorted(folder.iterdir()):
            if not file.is_file() or file.is_symlink():raise ValueError('Original no regular')
            remote='/data/reto1/raw/api_rentas/'+batch+'/'+file.name
            result=hdfs.upload_file(str(file),remote)
            if not result.exito or result.modo!='webhdfs_live':raise RuntimeError('HDFS real requerido')
            target=Path(scratch)/file.name;hdfs.download_file(remote,str(target))
            if target.read_bytes()!=file.read_bytes():raise ValueError('Recuperacion distinta')
            files.append({'archivo':file.name,'hdfs':remote,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
            if file.name=='rentas_api.json':recovered=json.loads(target.read_bytes())
    if recovered!=rows:raise ValueError('Derivados recuperados distintos')
    bootstrap=os.getenv('KAFKA_BOOTSTRAP_SERVERS','localhost:9092');topic='reto1-api-rentas-'+batch
    db.rentas_api.create_index([('codigo_municipio',1),('anio',1),('trimestre',1),('sha256',1)],unique=True)
    producer=KafkaProducer(bootstrap_servers=bootstrap.split(','),acks='all')
    consumer=None;seen=set()
    try:
        for row in recovered:producer.send(topic,value=json.dumps(row,ensure_ascii=False).encode()).get(timeout=20)
        producer.flush()
        consumer=KafkaConsumer(topic,bootstrap_servers=bootstrap.split(','),group_id=batch,
                               auto_offset_reset='earliest',enable_auto_commit=False)
        deadline=time.monotonic()+60
        while len(seen)<len(rows) and time.monotonic()<deadline:
            for messages in consumer.poll(timeout_ms=1000,max_records=1).values():
                for message in messages:
                    row=json.loads(message.value)
                    if row not in rows:raise ValueError('Evento ajeno o alterado')
                    key={k:row[k] for k in ('codigo_municipio','anio','trimestre')};key['sha256']=row['procedencia']['sha256']
                    db.rentas_api.update_one(key,{'$set':row},upsert=True)
                    stored=db.rentas_api.find_one(key)
                    if any(stored[k]!=v for k,v in row.items()):raise ValueError('Persistencia no confirmada')
                    consumer.commit();seen.add(row['codigo_municipio'])
        if len(seen)!=3:raise RuntimeError('Transporte incompleto')
        return {'servicios':{'hdfs':'real','kafka':'real','mongodb':'real'},'recibidos':len(seen),
                'documentos_coleccion':db.rentas_api.count_documents({}), 'coleccion':'rentas_api',
                'offsets_tras_persistencia':True,'archivos':files,'datos':rows,
                'limite':'Estadísticas de precios agregados por municipio/trimestre; no anuncios. No modifica el Excel, el modelo o el test.'}
    finally:
        if consumer is not None:consumer.close(autocommit=False)
        producer.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--db-name',default='reto1_api_rentas');p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();m=MongoDBManager(db_name=a.db_name)
    try:
        result=transport(a.input_dir,m.db);a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
    finally:m.close()
