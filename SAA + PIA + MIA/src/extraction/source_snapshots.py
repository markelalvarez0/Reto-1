"""Adaptadores de capturas oficiales verificadas: INE, Etxebide, Visesa y OVJ.

Las promociones no son anuncios individuales. Un salario autonómico no se
convierte en un salario municipal. Los originales nunca se reescriben aqui.
"""
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from .models import HousingAd, INE_MUNICIPAL_CODES, _normalizar_nombre_municipio


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_snapshot(directory: str | Path) -> dict[str, dict[str, Any]]:
    """Exige identidad byte a byte con el manifiesto de la captura."""
    root = Path(directory).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    sources = {}
    for record in manifest["fuentes"]:
        if record.get("estado") != "descargado":
            continue
        name = record["archivo"]
        if Path(name).name != name or name in sources:
            raise ValueError("Nombre de original ambiguo o no permitido")
        path = root / name
        if path.is_symlink() or not path.is_file() or sha256(path) != record["sha256"]:
            raise ValueError(f"Integridad del original no verificada: {name}")
        sources[name] = dict(record)
    return sources


class MunicipalityCatalog:
    """Nomenclator INE de Euskadi, sin coincidencias parciales ni localidad por defecto."""
    def __init__(self, records, provenance=None):
        self.records = {}
        self.provenance = dict(provenance or {})
        candidates = {}
        for record in records:
            code = str(record["codigo_municipio"])
            name = record["municipio"]
            if not re.fullmatch(r"(?:01|20|48)[0-9]{3}", code) or not isinstance(name, str) or not name.strip():
                raise ValueError("Registro INE no valido")
            if code in self.records and self.records[code]["municipio"] != name:
                raise ValueError("Codigo INE duplicado con nombres diferentes")
            self.records[code] = {"codigo_municipio": code, "municipio": name,
                                  "provincia": {"01": "Araba", "20": "Gipuzkoa", "48": "Bizkaia"}[code[:2]]}
            for alias in [name, *name.split("/")]:
                key = _normalizar_nombre_municipio(alias)
                candidates.setdefault(key, set()).add(code)
        for alias, code in INE_MUNICIPAL_CODES.items():
            if code in self.records:
                candidates.setdefault(_normalizar_nombre_municipio(alias), set()).add(code)
        self.aliases = {name: next(iter(codes)) for name, codes in candidates.items() if name and len(codes) == 1}

    def resolve(self, name: str) -> str | None:
        return self.aliases.get(_normalizar_nombre_municipio(name))

    @classmethod
    def from_snapshot(cls, root, sources=None):
        """Lee las tres hojas provinciales, no solo la primera hoja del XLSX."""
        root = Path(root)
        sources = verify_snapshot(root) if sources is None else sources
        source = sources.get("ine_2026.xlsx")
        if not source:
            raise ValueError("Falta el catalogo INE verificado")
        records = []
        with pd.ExcelFile(root / source["archivo"], engine="openpyxl") as book:
            if not {"01", "20", "48"}.issubset(book.sheet_names):
                raise ValueError("Faltan hojas INE de Araba, Gipuzkoa o Bizkaia")
            for sheet in ("01", "20", "48"):
                table = pd.read_excel(book, sheet_name=sheet, header=None, dtype=str, keep_default_na=False)
                header = next((i for i in range(min(10, len(table))) if {"CPRO", "CMUN", "NOMBRE"}.issubset({str(v).strip().upper() for v in table.iloc[i]})), None)
                if header is None:
                    raise ValueError(f"Cabecera INE no reconocida en la hoja {sheet}")
                columns = [str(v).strip().upper() for v in table.iloc[header]]
                sheet_count = 0
                for row in table.iloc[header + 1:].itertuples(index=False, name=None):
                    values = dict(zip(columns, row))
                    province, municipality = str(values["CPRO"]).strip(), str(values["CMUN"]).strip()
                    if not province.isdigit() or not municipality.isdigit():
                        continue
                    if len(province) > 2 or len(municipality) > 3 or province.zfill(2) != sheet:
                        raise ValueError(f"Codigo incompatible con la hoja INE {sheet}")
                    records.append({"codigo_municipio": province.zfill(2) + municipality.zfill(3),
                                    "municipio": str(values["NOMBRE"]).strip()})
                    sheet_count += 1
                if sheet_count == 0:
                    raise ValueError(f"Hoja INE vacia: {sheet}")
        return cls(records, source)


def parse_etxebide_csv(data: bytes, provenance=None):
    """Decodifica una copia en memoria: respeta Latin-1 y Cod_Prov + CODMUNI."""
    try:
        text = data.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = data.decode("iso-8859-1")
        encoding = "iso-8859-1"
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    if not reader.fieldnames or not {"ID_PROM", "Municipio"}.issubset({name.strip() for name in reader.fieldnames}):
        raise ValueError("Contrato Etxebide no reconocido: faltan ID_PROM/Municipio")
    ads, rejected = [], []
    for number, original in enumerate(reader, 2):
        row = {str(k).strip(): v for k, v in original.items() if k is not None}
        try:
            identifier, municipality = str(row.get("ID_PROM") or "").strip(), str(row.get("Municipio") or "").strip()
            if not identifier or not municipality:
                raise ValueError("Identificador o municipio ausente")
            code = None
            province = str(row.get("Cod_Prov") or "").strip()
            local = str(row.get("CODMUNI") or "").strip()
            if province or local:
                if not re.fullmatch(r"[0-9]{1,2}", province) or not re.fullmatch(r"[0-9]{1,3}", local):
                    raise ValueError("Cod_Prov/CODMUNI no validos")
                code = province.zfill(2) + local.zfill(3)
                if code[:2] not in {"01", "20", "48"}:
                    raise ValueError("Municipio fuera del ambito de Euskadi")
            access = _normalizar_nombre_municipio(row.get("Reg Acceso", ""))
            operation = "alquiler" if "alquiler" in access else ("compraventa" if "compra" in access or "venta" in access else "vpo")
            metadata = {**(provenance or {"estado": "no_acreditada"}), "fila_origen": number,
                        "encoding": encoding, "unidad_observacion": "promocion",
                        "regimen_original": row.get("Reg Acceso"), "codigo_fuente": code,
                        "numero_viviendas_publicado": row.get("NumViviendas"),
                        "estado_obra_original": row.get("EstadoObra")}
            ads.append(HousingAd(id=f"etxebide_{identifier}", fuente="OpenDataEuskadi_Etxebide_CSV",
                                 tipo_registro="promocion", tipo_operacion=operation,
                                 municipio=municipality, codigo_municipio=code, provincia=row.get("Territorio"),
                                 direccion=row.get("Ubicacion"), titulo=f"Promocion Etxebide {identifier}",
                                 precio=None, superficie_m2=None, es_sintetico=False,
                                 url=(provenance or {}).get("url"), procedencia=metadata))
        except (ValueError, TypeError) as error:
            rejected.append(f"Etxebide fila {number}: {error}")
    return ads, rejected


def parse_ovj_salary(data: bytes, provenance: dict) -> dict:
    """Extrae el indicador de la noticia conservando territorio, edad, periodo y unidad."""
    soup = BeautifulSoup(data, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    paragraphs = [" ".join(tag.stripped_strings) for tag in soup.find_all("p")]
    candidates = [p for p in paragraphs if re.search(r"salario\s+neto\s+medio", p, re.I)
                  and re.search(r"18\s*(?:a|y)\s*34", p) and "2024" in p]
    values = {match for text in candidates for match in re.findall(r"(\d{1,3}(?:\.\d{3})+(?:,\d+)?)\s*euros\s*mensuales", text, re.I)}
    if len(values) != 1 or not any("extraordinarias" in p.lower() or "pagas extra" in p.lower() for p in candidates):
        raise ValueError("No se identifica univocamente el salario OVJ, periodo y tramo de edad")
    value = float(next(iter(values)).replace(".", "").replace(",", "."))
    return {"indicador": "salario_neto_medio_juventud_asalariada", "valor": value,
            "unidad": "EUR/mes", "periodo": "2024", "territorio": "Euskadi",
            "edad_min": 18, "edad_max": 34, "incluye_pagas_extra": True,
            "es_salario_municipal": False, "procedencia": provenance}


def prepare_snapshot(snapshot_dir, output_dir):
    """Transforma originales sin confundir las promociones con oferta individual."""
    from .api_client import OpenDataEuskadiHousingClient
    root, out = Path(snapshot_dir).resolve(), Path(output_dir).resolve()
    if out == root or out.is_relative_to(root):
        raise ValueError("Las salidas deben quedar fuera de los originales")
    sources = verify_snapshot(root)
    required = {"visesa.json", "etxebide.csv", "ine_2026.xlsx", "ovj_salario_2024.html"}
    if not required.issubset(sources):
        raise ValueError("Faltan capturas necesarias: " + ", ".join(sorted(required - sources.keys())))
    catalog = MunicipalityCatalog.from_snapshot(root, sources)

    def provenance(name):
        record = sources[name]
        return {"estado": "original_verificado", "archivo": name, "sha256": record["sha256"],
                "url": record.get("url_final", record["url_solicitada"]), "fecha_captura": record["fecha_utc"],
                "catalogo_ine_sha256": sources["ine_2026.xlsx"]["sha256"]}

    client = OpenDataEuskadiHousingClient()
    visesa = client.parse_payload(json.loads((root / "visesa.json").read_bytes()), provenance("visesa.json"))
    etxebide, errors = parse_etxebide_csv((root / "etxebide.csv").read_bytes(), provenance("etxebide.csv"))
    rejected = [{"fuente": "parseo", "motivo": message} for message in [*visesa.errores, *errors]]
    accepted, seen = [], set()
    for ad in [*visesa.items, *etxebide]:
        by_name = catalog.resolve(ad.municipio)
        by_source = ad.procedencia.get("codigo_fuente")
        if by_source:
            code = by_source if by_source in catalog.records and (by_name is None or by_name == by_source) else None
            method = "codigo_fuente_validado_INE"
        else:
            code, method = by_name, "nombre_o_alias_exacto_INE"
        if not code:
            rejected.append({"fuente": ad.fuente, "id": ad.id, "municipio": ad.municipio,
                             "codigo_fuente": by_source, "motivo": "municipio_no_resuelto_o_codigo_contradictorio"})
            continue
        key = (ad.fuente, ad.id)
        if key in seen:
            rejected.append({"fuente": ad.fuente, "id": ad.id, "motivo": "identidad_duplicada_en_captura"})
            continue
        seen.add(key)
        original_name = ad.municipio
        values = {**ad.to_dict(), **catalog.records[code], "fecha_extraccion": ad.procedencia["fecha_captura"],
                  "procedencia": {**ad.procedencia, "municipio_original": original_name, "metodo_geo": method}}
        accepted.append(HousingAd.model_validate(values).to_dict())
    reference = parse_ovj_salary((root / "ovj_salario_2024.html").read_bytes(), provenance("ovj_salario_2024.html"))
    municipalities = [{**catalog.records[code], "es_sintetico": False, "procedencia": provenance("ine_2026.xlsx"),
                       "contexto_autonomico": {"salario_ovj": reference},
                       "economia_laboral": {"salario_medio_joven_mes": None}}
                      for code in sorted({row["codigo_municipio"] for row in accepted})]
    report = {"tipo": "preparacion_capturas_reales", "visesa_leidas": visesa.total_registros,
              "etxebide_leidas": len(etxebide), "registros_aceptados": len(accepted), "rechazos": rejected,
              "municipios": len(municipalities), "catalogo_ine_municipios": len(catalog.records),
              "salario_ovj": reference, "originales": list(sources.values()),
              "limites": "Promociones, no anuncios individuales ni disponibilidad actual. El salario OVJ es autonómico, no municipal. Los campos ausentes permanecen nulos."}
    out.mkdir(parents=True, exist_ok=True)
    for name, value in [("vivienda_oficial.json", accepted), ("municipios_oficiales.json", municipalities), ("preparacion.json", report)]:
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return catalog, report
