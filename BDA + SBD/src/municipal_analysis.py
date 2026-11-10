"""Análisis descriptivo EMAL + OVJ en MongoDB, separado del entrenamiento.

Unidad: municipio/trimestre, nunca anuncio ni hogar. El esfuerzo es un escenario
con salario autonómico de 2024, no una estimación del salario municipal.
"""
import json
import math
from pathlib import Path
import pandas as pd
from src.ml_data import read_emal
from src.extraction.source_snapshots import verify_snapshot, MunicipalityCatalog, parse_ovj_salary


def analyze(db, snapshot_dir, year=2024, quarter=4):
    """Carga idempotente por huella y exporta tres agregaciones del mismo periodo."""
    root = Path(snapshot_dir)
    sources = verify_snapshot(root)
    frame, metadata = read_emal(root)
    salary_source = sources["ovj_salario_2024.html"]
    salary = parse_ovj_salary((root / salary_source["archivo"]).read_bytes(), salary_source)
    if year != int(salary["periodo"]) or quarter not in (1, 2, 3, 4):
        raise ValueError("Comparar con el salario OVJ del mismo año: 2024, trimestre 1 a 4")
    snapshot = sources["emal_municipios.xlsx"]["sha256"]
    context_id = salary_source["sha256"]
    period = year * 4 + quarter - 1
    if frame.loc[frame.periodo.eq(period)].empty:
        raise ValueError("El trimestre elegido no tiene observaciones")
    db.contextos_ovj.update_one({"_id": context_id}, {"$set": salary}, upsert=True)
    db.rentas_emal.create_index([("captura", 1), ("codigo_municipio", 1), ("periodo", 1)], unique=True)
    selected = frame[["codigo_municipio", "municipio", "provincia", "anio", "trimestre", "periodo",
                      "renta_media_eur", "numero_contratos", "renta_lag4"]]
    for row in selected.astype(object).where(selected.notna(), None).to_dict("records"):
        identity = {"captura": snapshot, "codigo_municipio": row["codigo_municipio"], "periodo": row["periodo"]}
        db.rentas_emal.update_one(identity, {"$set": {**row, "contexto_id": context_id, "fuente": metadata["fuente"]}}, upsert=True)
    match = {"captura": snapshot, "periodo": period}
    comparison = list(db.rentas_emal.aggregate([
        {"$match": match},
        {"$lookup": {"from": "contextos_ovj", "localField": "contexto_id", "foreignField": "_id", "as": "contexto"}},
        {"$unwind": "$contexto"},
        {"$project": {"_id": 0, "codigo_municipio": 1, "municipio": 1, "provincia": 1, "anio": 1, "trimestre": 1,
            "renta_media_eur": 1, "numero_contratos": 1,
            "renta_anual_equivalente_eur": {"$multiply": ["$renta_media_eur", 12]},
            "variacion_interanual_pct": {"$cond": [{"$gt": ["$renta_lag4", 0]},
                {"$multiply": [{"$subtract": [{"$divide": ["$renta_media_eur", "$renta_lag4"]}, 1]}, 100]}, None]},
            "salario_referencia_autonomico_eur": "$contexto.valor",
            "esfuerzo_escenario_pct": {"$multiply": [{"$divide": ["$renta_media_eur", "$contexto.valor"]}, 100]},
            "diferencia_umbral_30_eur": {"$subtract": ["$renta_media_eur", {"$multiply": ["$contexto.valor", 0.3]}]},
        }},
        {"$sort": {"renta_media_eur": 1, "codigo_municipio": 1}},
    ]))
    # Media simple entre municipios: no confundirla con renta de todos los contratos.
    territory = list(db.rentas_emal.aggregate([
        {"$match": match}, {"$group": {"_id": "$provincia", "municipios": {"$sum": 1},
            "media_simple_rentas_municipales_eur": {"$avg": "$renta_media_eur"},
            "contratos_publicados": {"$sum": "$numero_contratos"}}},
        {"$sort": {"_id": 1}},
    ]))
    series = list(db.rentas_emal.aggregate([
        {"$match": {"captura": snapshot, "anio": {"$lte": year}}},
        {"$project": {"_id": 0, "codigo_municipio": 1, "municipio": 1, "anio": 1, "trimestre": 1,
                      "periodo": 1, "renta_media_eur": 1, "numero_contratos": 1}},
        {"$sort": {"periodo": 1, "codigo_municipio": 1}},
    ]))
    catalog = MunicipalityCatalog.from_snapshot(root, sources)
    points = []
    for row in json.loads((root / "visesa.json").read_text(encoding="utf-8"))["rows"]:
        code = catalog.resolve(row.get("poblacion", ""))
        try:
            lat, lon = float(row["latitud"]), float(row["longitud"])
        except (TypeError, ValueError, KeyError):
            continue
        if code and math.isfinite(lat) and math.isfinite(lon) and 42 <= lat <= 44 and -4 <= lon <= -1:
            points.append({"id_promocion": str(row.get("idPromocion")), "codigo_municipio": code,
                           "municipio": catalog.records[code]["municipio"], "lat": lat, "lon": lon})
    if len(comparison) < 3:
        raise ValueError("La comparación necesita al menos tres municipios")
    return {"comparativa_municipal": comparison, "resumen_territorial": territory,
            "serie_trimestral": series, "mapa_promociones": points,
            "metadatos": {"anio": year, "trimestre": quarter, "unidad": "municipio/trimestre",
                "fuentes": {name: sources[name] for name in ("emal_municipios.xlsx", "ovj_salario_2024.html", "visesa.json", "ine_2026.xlsx")},
                "salario": salary,
                "limites": ["El esfuerzo es un escenario con salario autonómico, no una medida de cada hogar.",
                    "La renta anual equivalente multiplica por 12 la renta mensual: no suma contratos anuales.",
                    "El umbral del 30% es analítico, no un requisito legal de subvención.",
                    "El mapa localiza promociones Visesa; no representa ofertas disponibles ni centros municipales.",
                    "La media territorial es simple entre los municipios cubiertos; no representa todos los contratos.",
                    metadata["advertencia"]]}}
