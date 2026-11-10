"""Dataset observado de renta municipal EMAL; no son anuncios ni solicitantes.

Unidad: municipio/trimestre de inicio del contrato. Se excluyen stocks vigentes
actualizados por IRAV y Galdakao, cuyo perimetro cambia en la serie publicada.
Nunca se imputa el objetivo. Los retardos se calculan antes de quitar objetivos
no publicados, para que lag1 signifique exactamente el trimestre anterior.
"""
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

NUMERIC = ["anio", "trimestre", "renta_lag1", "renta_lag4", "contratos_lag1"]
CATEGORICAL = ["codigo_municipio", "provincia"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "renta_media_eur"


def _rows(book, name):
    sheet = book[name]
    sheet.reset_dimensions()
    return list(sheet.iter_rows(values_only=True))


def _number(value):
    if value is None or str(value).strip() in {"", "-", "..", "..."}:
        return np.nan
    try:
        result = float(value)
    except (TypeError, ValueError):
        return np.nan
    return result if np.isfinite(result) else np.nan


def _quarter_columns(rows):
    result, year = [], None
    for col in range(2, len(rows[1])):
        value = rows[1][col]
        if value is not None:
            text = str(value).strip()
            year = int(text) if re.fullmatch(r"20\d{2}", text) else None
        quarter = str(rows[2][col]).strip() if col < len(rows[2]) else ""
        if year is not None and quarter in {"I", "II", "III", "IV"}:
            result.append((col, year, {"I": 1, "II": 2, "III": 3, "IV": 4}[quarter]))
    if not result:
        raise ValueError("Cabeceras trimestrales EMAL no reconocidas")
    return result


def _table(book, name, value_name):
    rows = _rows(book, name)
    columns = _quarter_columns(rows)
    output = []
    for row in rows[3:]:
        if len(row) < 2 or row[0] is None or row[1] is None:
            continue
        raw = str(row[0]).strip()
        if not re.fullmatch(r"\d{4,5}", raw):
            continue
        code = raw.zfill(5)
        if code[:2] not in {"01", "20", "48"}:
            continue
        if code == "48036":
            continue  # No mezclar Galdakao anterior/posterior a la desanexion.
        for col, year, quarter in columns:
            output.append({"codigo_municipio": code, "municipio": str(row[1]).strip(),
                           "anio": year, "trimestre": quarter,
                           value_name: _number(row[col] if col < len(row) else None)})
    frame = pd.DataFrame(output)
    keys = ["codigo_municipio", "anio", "trimestre"]
    if frame.empty or frame.duplicated(keys).any():
        raise ValueError(f"Tabla {name} vacia o con claves temporales duplicadas")
    return frame


def read_emal(raw_dir):
    """Verifica originales contra manifest.json y crea variables disponibles en t-1."""
    raw_dir = Path(raw_dir)
    manifest = json.loads((raw_dir / "manifest.json").read_text(encoding="utf-8"))
    sources = {entry["archivo"]: entry for entry in manifest["fuentes"]}
    name = "emal_municipios.xlsx"
    source = sources.get(name, {})
    if source.get("estado") != "descargado":
        raise ValueError("No existe captura EMAL verificada")
    original = raw_dir / name
    if hashlib.sha256(original.read_bytes()).hexdigest() != source.get("sha256"):
        raise ValueError("La huella de EMAL no coincide con el manifiesto")
    book = openpyxl.load_workbook(original, read_only=True, data_only=True)
    try:
        rents = _table(book, "T1.2", TARGET)
        counts = _table(book, "T1.1", "numero_contratos")
    finally:
        book.close()
    keys = ["codigo_municipio", "anio", "trimestre"]
    frame = rents.merge(counts[keys + ["numero_contratos"]], on=keys, how="left", validate="one_to_one")
    frame["periodo"] = frame["anio"] * 4 + frame["trimestre"] - 1
    frame = frame.sort_values(["codigo_municipio", "periodo"]).reset_index(drop=True)
    if not frame.groupby("codigo_municipio")["periodo"].diff().dropna().eq(1).all():
        raise ValueError("Hay huecos trimestrales: reindexar antes de calcular retardos")
    group = frame.groupby("codigo_municipio", sort=False)
    frame["renta_lag1"] = group[TARGET].shift(1)
    frame["renta_lag4"] = group[TARGET].shift(4)
    frame["contratos_lag1"] = group["numero_contratos"].shift(1)
    frame["provincia"] = frame["codigo_municipio"].str[:2].map({"01": "Araba", "20": "Gipuzkoa", "48": "Bizkaia"})
    missing_target = int(frame[TARGET].isna().sum())
    frame = frame.loc[frame[TARGET].notna() & (frame[TARGET] > 0)].copy()
    frame = frame.sort_values(["periodo", "codigo_municipio"]).reset_index(drop=True)
    metadata = {"fuente": source, "unidad": "municipio/trimestre; nuevos contratos EMAL",
                "observaciones": len(frame), "municipios": int(frame.codigo_municipio.nunique()),
                "objetivos_no_publicados_excluidos": missing_target,
                "exclusion_territorial": "48036 Galdakao: cambio de perimetro",
                "advertencia": "Serie revisada en la fecha de captura; evaluacion retrospectiva, no prueba de disponibilidad historica en tiempo real. No representa anuncios individuales ni todos los municipios de Euskadi.",
                "smote": "No aplicable al objetivo continuo de renta; comparacion binaria auxiliar separada sobre subidas observadas."}
    return frame, metadata


def temporal_split(frame):
    """Entrenamiento hasta 2023, validacion 2024, test 2025 en adelante."""
    train = frame.loc[frame.anio <= 2023].copy()
    val = frame.loc[frame.anio == 2024].copy()
    test = frame.loc[frame.anio >= 2025].copy()
    if any(part.empty for part in (train, val, test)):
        raise ValueError("No hay datos para las tres particiones temporales previstas")
    if not train.periodo.max() < val.periodo.min() <= val.periodo.max() < test.periodo.min():
        raise ValueError("Las particiones temporales se solapan")
    return train, val, test


def temporal_folds(frame, n_splits=3):
    """CV de ventana creciente, sin repartir un trimestre entre train y validacion."""
    periods = np.sort(frame.periodo.unique())
    splitter = TimeSeriesSplit(n_splits=n_splits)
    return [(np.flatnonzero(frame.periodo.isin(periods[a]).to_numpy()),
             np.flatnonzero(frame.periodo.isin(periods[b]).to_numpy()))
            for a, b in splitter.split(periods)]
