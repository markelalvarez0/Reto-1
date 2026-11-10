#!/usr/bin/env python3
"""BDA: originales verificados -> HDFS -> Kafka -> MongoDB.

Modo real por defecto. --demo utiliza fixtures y simuladores explicitos.
--snapshot-dir reutiliza los originales capturados sin alterar el bloque ML.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.extraction.api_client import OpenDataEuskadiHousingClient
from src.extraction.models import HousingAd
from src.extraction.source_snapshots import prepare_snapshot, verify_snapshot
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str, allow_nan=False), encoding="utf-8")


def run_pipeline(raw_dir, output_dir, demo=False, fetch=False, *, snapshot_dir=None,
                 db_name=None, topic=None, interval_seconds=0.0):
    """Reproduce un lote identificable y acredita almacenamiento y recepcion.

    El resultado de alquiler queda vacio cuando las fuentes solo contienen
    promociones sin renta individual. No fabrica alquileres para llenar graficos.
    """
    if demo and snapshot_dir or fetch and snapshot_dir:
        raise ValueError("No mezclar captura congelada con demo ni recaptura")
    if interval_seconds < 0:
        raise ValueError("El intervalo no puede ser negativo")
    raw_dir, output_dir = Path(raw_dir).resolve(), Path(output_dir).resolve()
    raw_dir.mkdir(parents=True, exist_ok=True); output_dir.mkdir(parents=True, exist_ok=True)
    batch = uuid.uuid4().hex
    date = datetime.now(timezone.utc)
    partition = date.strftime("%Y%m%dT%H%M%S") + "_" + batch[:8]
    catalog, preparation = (prepare_snapshot(snapshot_dir, raw_dir) if snapshot_dir else (None, None))
    manager = MongoDBManager(db_name=db_name or os.getenv("MONGO_DB", "reto1_vivienda"), force_mock=demo)
    loader = MongoDBDataLoader(manager.db, allow_demo=demo, municipality_catalog=catalog)
    producer = consumer = None
    try:
        if demo:
            save(raw_dir / "vivienda_demo.json", loader._generar_catalogo_multiportal_completo())
            save(raw_dir / "municipios_demo.json", list(loader._generar_datos_municipios_base().values()))
            InMemoryKafkaBroker.reset()
        files = sorted(p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in {".json", ".csv"} and p.name.startswith(("vivienda_", "municipios_")))
        if not demo and not snapshot_dir and (fetch or not any(p.name.startswith("vivienda_") for p in files)):
            client = OpenDataEuskadiHousingClient()
            response = client._safe_get(client.api_url); response.raise_for_status()
            original = raw_dir / "sources" / f"visesa_{partition}.json"
            original.parent.mkdir(parents=True, exist_ok=True); original.write_bytes(response.content)
            result = client.parse_payload(response.json(), {**client.provenance(response), "archivo": original.name})
            if not result.items:
                raise ValueError("Visesa no devolvio registros interpretables: " + "; ".join(result.errores))
            save(raw_dir / f"vivienda_api_{partition}.json", [ad.to_dict() for ad in result.items])
            files = sorted(p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in {".json", ".csv"} and p.name.startswith(("vivienda_", "municipios_")))
        validated, municipalities, rejected, seen = [], [], 0, set()
        for path in files:
            rows = loader._leer_fichero(path)
            if path.name.startswith("municipios_"):
                municipalities.extend(rows); continue
            for row in rows:
                normalized = loader._normalizar_anuncio(row)
                if normalized is None or (not demo and normalized["es_sintetico"] is not False):
                    loader._registrar_rechazo(row, "identidad_geo_o_procedencia_no_verificada")
                    rejected += 1; continue
                key = (normalized["fuente"], normalized["id_origen"])
                if key in seen:
                    loader._registrar_rechazo(row, "identidad_duplicada_en_lote")
                    rejected += 1; continue
                seen.add(key)
                values = {**normalized, **normalized["caracteristicas"], "id": normalized["id_origen"], "lote_ingesta": batch}
                if values.get("fecha_extraccion") is None:
                    values.pop("fecha_extraccion", None)
                validated.append(HousingAd(**{key: value for key, value in values.items() if key in HousingAd.model_fields}))
        if not validated:
            raise ValueError("No hay registros validos; revisar originales y rechazos, no activar demo automaticamente")
        normalized_path = output_dir / "anuncios_normalizados.json"
        save(normalized_path, [ad.to_dict() for ad in validated])

        # Originales byte a byte y derivados separados. No modificar la captura.
        storage = [(path, "processed" if snapshot_dir else "raw", "entradas/" + path.name) for path in files]
        if snapshot_dir:
            sources = verify_snapshot(snapshot_dir)
            storage.extend((Path(snapshot_dir) / name, "raw", "originales/" + name) for name in sorted(sources))
            storage.append((Path(snapshot_dir) / "manifest.json", "raw", "originales/manifest.json"))
        else:
            storage.extend((path, "raw", "originales/" + path.name) for path in sorted((raw_dir / "sources").glob("*")) if path.is_file())
        storage.append((normalized_path, "processed", normalized_path.name))
        hdfs = HDFSClient(simulation_mode=demo, simulation_storage_dir=str(output_dir / "hdfs_demo"))
        storage_evidence = []
        for path, kind, relative in storage:
            if path.is_symlink():
                raise ValueError("No se almacenan enlaces simbolicos como originales")
            remote = f"/data/reto1/{kind}/{partition}/{relative}"
            upload = hdfs.upload_file(str(path), remote)
            if not upload.exito:
                raise RuntimeError(f"HDFS: {upload.mensaje}")
            recovered = output_dir / "recuperados" / kind / relative
            hdfs.download_file(remote, str(recovered))
            if recovered.read_bytes() != path.read_bytes() or hdfs.calculate_sha256(str(recovered)) != upload.checksum_sha256:
                raise RuntimeError(f"Integridad de recuperacion fallida: {path}")
            storage_evidence.append({**upload.model_dump(), "original_local": str(path), "clase": kind, "recuperacion_identica": True})

        loader.cargar_municipios(municipalities)
        producer = HousingKafkaProducer(topic=topic, simulation_mode=demo)
        consumer = HousingKafkaConsumer(topic=topic, group_id="reto1_lote_" + batch, simulation_mode=demo)
        published = producer.stream_ads(validated, interval_seconds=interval_seconds)
        if published != len(validated):
            raise RuntimeError("Kafka no confirmo todos los envios")
        def persist(ad, _count):
            accepted, discarded = loader.cargar_anuncios([ad.to_dict()])
            if accepted != 1 or discarded:
                raise RuntimeError(f"Persistencia fallida para {ad.id}")
        received = consumer.consume_batch(max_messages=len(validated), timeout_seconds=max(60, len(validated) * .5),
                                          on_message_callback=persist, expected_batch_id=batch)
        if {(ad.fuente, ad.id) for ad in validated} != {(ad.fuente, ad.id) for ad in received}:
            raise RuntimeError("No se recibieron las identidades del lote completo")
        persisted = manager.db.viviendas.count_documents({"lote_ingesta": batch})
        if persisted != len(validated):
            raise RuntimeError("La persistencia del lote no coincide con sus registros unicos")
        # El sobre completo, incluida procedencia, debe sobrevivir a Kafka y MongoDB.
        for ad in received:
            doc = manager.db.viviendas.find_one({"fuente": ad.fuente, "id_origen": ad.id})
            if doc["procedencia"] != ad.procedencia or doc["tipo_registro"] != ad.tipo_registro:
                raise RuntimeError("Procedencia o unidad perdidas durante el transporte")
        cleaning = MongoDataCleaner(manager.db).ejecutar_pipeline_limpieza()
        indexes = MongoIndexOptimizer(manager.db, is_mock=demo); indexes.crear_indices()
        aggregates = MongoHousingAggregations(manager.db, include_synthetic=demo)
        datasets = {"estadisticas_por_municipio": aggregates.pipeline_1_estadisticas_alquiler_por_municipio(),
                    "esfuerzo_por_vivienda": aggregates.pipeline_2_cruce_esfuerzo_salarial(),
                    "distribuciones": aggregates.pipeline_3_facet_distribucion_y_top(),
                    "indicadores_municipales": aggregates.indicadores_municipales()}
        for name, value in datasets.items():
            save(output_dir / (name + ".json"), value)
        save(output_dir / "explain.json", indexes.comparar_rendimiento_consulta())
        documents = list(manager.db.viviendas.find({"lote_ingesta": batch}, {"_id": 0}))
        save(output_dir / "catalogo_viviendas.json", documents)
        summary = list(manager.db.viviendas.aggregate([
            {"$match": {"lote_ingesta": batch, "tipo_registro": "promocion"}},
            {"$group": {"_id": {"codigo_municipio": "$codigo_municipio", "fuente": "$fuente"}, "registros_catalogo": {"$sum": 1}}},
            {"$sort": {"_id.codigo_municipio": 1, "_id.fuente": 1}},
        ]))
        save(output_dir / "promociones_por_municipio.json", summary)
        manifest = {"modo": "demo" if demo else "real", "fecha_utc": date.isoformat(), "lote_ingesta": batch,
                    "anuncios_publicados": published, "anuncios_recibidos": len(received), "registros_persistidos": persisted,
                    "unidad_recuentos": "registros, no numero de viviendas disponibles", "por_fuente": dict(Counter(ad.fuente for ad in validated)),
                    "por_tipo_registro": dict(Counter(ad.tipo_registro for ad in validated)), "rechazados": rejected,
                    "municipios_con_precios": len(datasets["estadisticas_por_municipio"]),
                    "municipios_con_salario": sum(x["anuncios_con_salario"] > 0 for x in datasets["indicadores_municipales"]),
                    "hdfs": storage_evidence, "limpieza": cleaning, "preparacion": preparation,
                    "servicios": {"hdfs": "simulado" if demo else "real", "kafka": "simulado" if demo else "real", "mongodb": "simulado" if demo else "real"},
                    "limites": "Promociones no equivalen a anuncios de alquiler. Sin precios o salarios municipales observados no se calcula esfuerzo."}
        save(output_dir / "manifest.json", manifest)
        return manifest
    finally:
        if producer: producer.close()
        if consumer: consumer.close()
        manager.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline", action="store_true", help="Alias de compatibilidad: ejecutar el pipeline")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--fetch", action="store_true", help="Recapturar Visesa: no combinar con --snapshot-dir")
    parser.add_argument("--snapshot-dir", type=Path)
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--db-name")
    parser.add_argument("--topic")
    parser.add_argument("--interval-seconds", type=float, default=0.)
    parser.add_argument("--prepare-only", action="store_true", help="Validar y normalizar originales sin servicios")
    parser.add_argument("--visual", action="store_true", help="El mapa requiere la validacion separada de SBD")
    args = parser.parse_args(argv)
    if args.visual:
        parser.error("El dashboard historico no es la salida validada del pipeline BDA. Consulte docs/BDA_ESTADO.md.")
    if not args.demo and not args.fetch and args.snapshot_dir is None and (args.prepare_only or args.raw_dir is None):
        args.snapshot_dir = ROOT / "data/capturas_oficiales"
    base = ROOT / "data/bda_demo" if args.demo else ROOT / "data/bda"
    raw, out = args.raw_dir or base / "prepared", args.output_dir or base / "processed"
    if args.prepare_only:
        if not args.snapshot_dir or args.demo or args.fetch:
            parser.error("--prepare-only requiere una captura real sin --demo ni --fetch")
        _, result = prepare_snapshot(args.snapshot_dir, raw)
    else:
        result = run_pipeline(raw, out, args.demo, args.fetch, snapshot_dir=args.snapshot_dir,
                              db_name=args.db_name, topic=args.topic, interval_seconds=args.interval_seconds)
    print(json.dumps({k: v for k, v in result.items() if k not in {"hdfs", "preparacion", "originales"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
