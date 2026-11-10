#!/usr/bin/env python3
"""CSV/API -> originales HDFS -> Kafka -> MongoDB -> indicadores JSON.

Modo real por defecto; --demo selecciona fixtures y servicios simulados.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.extraction.api_client import OpenDataEuskadiHousingClient
from src.extraction.models import HousingAd
from src.database.mongo_client import MongoDBManager
from src.database.data_loader import MongoDBDataLoader
from src.database.cleaning import MongoDataCleaner
from src.database.aggregations import MongoHousingAggregations
from src.database.indexes import MongoIndexOptimizer
from src.kafka.producer import HousingKafkaProducer
from src.kafka.consumer import HousingKafkaConsumer
from src.kafka.mock_broker import InMemoryKafkaBroker
from src.hdfs.client import HDFSClient


def save(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str, allow_nan=False), encoding='utf-8')


def run_pipeline(raw_dir, output_dir, demo=False, fetch=False):
    """Ejecuta el flujo y comprueba cada etapa; no declara exitos ficticios."""
    raw_dir, output_dir = Path(raw_dir), Path(output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc)
    partition = timestamp.strftime('%Y%m%dT%H%M%S')
    manager = MongoDBManager(force_mock=demo)
    loader = MongoDBDataLoader(manager.db, allow_demo=demo)
    producer = consumer = None
    try:
        if demo:
            save(raw_dir / 'vivienda_demo.json', loader._generar_catalogo_multiportal_completo())
            save(raw_dir / 'municipios_demo.json', list(loader._generar_datos_municipios_base().values()))
            InMemoryKafkaBroker.reset()
        files = sorted(p for p in raw_dir.glob('*') if p.suffix.lower() in {'.json', '.csv'} and p.name.startswith(('vivienda_', 'municipios_')))
        if not demo and (fetch or not any(p.name.startswith('vivienda_') for p in files)):
            client = OpenDataEuskadiHousingClient()
            # Retain response bytes before normalizing to HousingAd.
            response = client._safe_get(client.api_url)
            response.raise_for_status()
            original = raw_dir / 'sources' / f'visesa_{partition}.json'
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes(response.content)
            payload = response.json()
            ads = [client._parse_api_row(row) for row in payload.get('rows', [])]
            path = raw_dir / f'vivienda_api_{partition}.json'
            save(path, [ad.to_dict() for ad in ads if ad is not None])
            files = sorted(set(files + [path, original]))
        if not files:
            raise ValueError('No hay archivos de vivienda ni municipios; no se generan datos por defecto')

        # Stage 1/2: source adapters, validation and municipal indicators.
        validated, municipalities, rejected = [], [], 0
        for path in files:
            if path.parent.name == 'sources':
                continue
            rows = list(loader._leer_fichero(path))
            if path.name.startswith('municipios_'):
                municipalities.extend(rows)
                continue
            for row in rows:
                normalized = loader._normalizar_anuncio(row)
                if normalized is None or (not demo and normalized['es_sintetico'] is not False):
                    loader._registrar_rechazo(row, 'identidad_geo_o_procedencia_no_verificada')
                    rejected += 1
                    continue
                values = {**normalized, **normalized['caracteristicas'], 'id': normalized['id_origen']}
                if values.get('fecha_extraccion') is None:
                    values.pop('fecha_extraccion', None)
                validated.append(HousingAd(**{key: value for key, value in values.items() if key in HousingAd.model_fields}))
        if not validated:
            raise ValueError('No hay anuncios validos; consulte rechazos_ingesta y los originales')
        normalized_path = output_dir / 'anuncios_normalizados.json'
        save(normalized_path, [ad.to_dict() for ad in validated])

        # Stage 3: retain original bytes AND normalized records, verifying recovery.
        hdfs = HDFSClient(simulation_mode=demo, simulation_storage_dir=str(output_dir / 'hdfs_demo'))
        storage_evidence = []
        for path in [*files, normalized_path]:
            kind = 'processed' if path == normalized_path else 'raw'
            remote = f'/data/reto1/{kind}/{partition}/{path.name}'
            upload = hdfs.upload_file(str(path), remote)
            if not upload.exito:
                raise RuntimeError(f'Fallo HDFS: {upload.mensaje}')
            recovered = output_dir / 'recuperados' / kind / path.name
            hdfs.download_file(remote, str(recovered))
            if hdfs.calculate_sha256(str(recovered)) != upload.checksum_sha256:
                raise RuntimeError(f'Integridad SHA-256 fallida: {path.name}')
            storage_evidence.append(upload.model_dump())

        # Stage 4/5: housing reaches MongoDB through the consumer callback.
        loader.cargar_municipios(municipalities)
        consumer = HousingKafkaConsumer(simulation_mode=demo)
        producer = HousingKafkaProducer(simulation_mode=demo)
        published = producer.stream_ads(validated, interval_seconds=0)
        if published != len(validated):
            raise RuntimeError('Kafka no confirmo todos los envios')
        def persist(ad, _count):
            accepted, discarded = loader.cargar_anuncios([ad.to_dict()])
            if accepted != 1 or discarded:
                raise RuntimeError(f'Persistencia fallida para evento {ad.id}')
        received = consumer.consume_batch(max_messages=len(validated), timeout_seconds=30, on_message_callback=persist)
        if {(ad.fuente, ad.id) for ad in validated} != {(ad.fuente, ad.id) for ad in received}:
            raise RuntimeError('No se recibieron los eventos esperados; no se marca el flujo completo como valido')
        cleaning = MongoDataCleaner(manager.db).ejecutar_pipeline_limpieza()
        indexes = MongoIndexOptimizer(manager.db, is_mock=demo)
        indexes.crear_indices()
        statistics = indexes.comparar_rendimiento_consulta()
        aggregates = MongoHousingAggregations(manager.db, include_synthetic=demo)
        datasets = {
            'estadisticas_por_municipio': aggregates.pipeline_1_estadisticas_alquiler_por_municipio(),
            'esfuerzo_por_vivienda': aggregates.pipeline_2_cruce_esfuerzo_salarial(),
            'distribuciones': aggregates.pipeline_3_facet_distribucion_y_top(),
            'indicadores_municipales': aggregates.indicadores_municipales(),
        }
        for name, data in datasets.items():
            save(output_dir / f'{name}.json', data)
        save(output_dir / 'explain.json', statistics)
        save(output_dir / 'catalogo_viviendas.json', list(manager.db.viviendas.find({}, {'_id': 0})))
        manifest = {
            'modo': 'demo' if demo else 'real', 'fecha_utc': timestamp.isoformat(),
            'anuncios_publicados': published, 'anuncios_recibidos': len(received), 'rechazados': rejected,
            'municipios_con_precios': len(datasets['estadisticas_por_municipio']),
            'municipios_con_salario': sum(x['anuncios_con_salario'] > 0 for x in datasets['indicadores_municipales']),
            'hdfs': storage_evidence, 'limpieza': cleaning,
            'limites': 'Demo no describe el mercado real. Los nulos no son ceros. La ausencia de salario impide calcular esfuerzo.',
        }
        save(output_dir / 'manifest.json', manifest)
        return manifest
    finally:
        if producer:
            producer.close()
        if consumer:
            consumer.close()
        manager.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--fetch', action='store_true', help='Actualiza la API aunque haya archivos locales')
    parser.add_argument('--raw-dir', type=Path)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    base = ROOT / 'data' / 'demo' if args.demo else ROOT / 'data'
    result = run_pipeline(args.raw_dir or (base / 'raw'), args.output_dir or (base / 'processed'), args.demo, args.fetch)
    print(json.dumps({key: value for key, value in result.items() if key != 'hdfs'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
