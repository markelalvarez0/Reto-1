"""Carga idempotente de datos observados. Los ejemplos requieren allow_demo=True."""
import csv
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.extraction.models import resolver_codigo_ine
from src.extraction.normalization import numero_observado, booleano_observado, primer_valor
from src.extraction.multi_portal_scraper import MultiPortalHousingScraper

logger = logging.getLogger(__name__)
PROVINCIAS = {"48": "Bizkaia", "20": "Gipuzkoa", "01": "Araba"}


class MongoDBDataLoader:
    """Carga CSV/JSON sin borrar colecciones ni completar precios desconocidos."""

    def __init__(self, db, allow_demo: bool = False, municipality_catalog=None):
        self.db = db
        self.viviendas_col = db["viviendas"]
        self.municipios_col = db["municipios"]
        self.rechazos_col = db["rechazos_ingesta"]
        self.allow_demo = allow_demo
        self.municipality_catalog = municipality_catalog

    def _codigo_municipio(self, name):
        """El catalogo completo se inyecta solo tras verificar la captura INE."""
        catalog = getattr(self, "municipality_catalog", None)
        return catalog.resolve(name) if catalog is not None else resolver_codigo_ine(name)

    @staticmethod
    def _leer_fichero(path: Path):
        if path.suffix.lower() == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                sample = stream.read(8192); stream.seek(0)
                delimiter = ";" if sample.splitlines() and sample.splitlines()[0].count(";") > sample.splitlines()[0].count(",") else ","
                yield from csv.DictReader(stream, delimiter=delimiter)
        else:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            rows = payload.get("items", payload.get("registros", [])) if isinstance(payload, dict) else payload
            if not isinstance(rows, list):
                raise ValueError(f"{path.name}: se esperaba una lista de registros")
            yield from rows

    def cargar_datos_base(self, data_raw_dir: Path) -> Dict[str, int]:
        """Lee vivienda_*.csv/json y municipios_*.csv/json. Demo nunca es implicita."""
        root = Path(data_raw_dir)
        counts = {"viviendas": 0, "municipios": 0, "rechazados": 0}
        municipality_rows = []
        housing_rows = []
        for path in sorted(root.glob("*")):
            if path.suffix.lower() not in {".csv", ".json"}:
                continue
            if not path.name.startswith(("vivienda_", "municipios_")):
                continue
            target = municipality_rows if path.name.startswith("municipios_") else housing_rows
            for row in self._leer_fichero(path):
                if not isinstance(row, dict):
                    raise ValueError(f"Registro no tabular en {path.name}")
                row = dict(row)
                row["archivo_origen"] = path.name
                target.append(row)
        if self.allow_demo and not municipality_rows:
            municipality_rows = list(self._generar_datos_municipios_base().values())
        counts["municipios"], rejected = self.cargar_municipios(municipality_rows)
        counts["rechazados"] += rejected
        if self.allow_demo and not housing_rows:
            housing_rows = self._generar_catalogo_multiportal_completo()
        counts["viviendas"], rejected = self.cargar_anuncios(housing_rows)
        counts["rechazados"] += rejected
        return counts

    def cargar_municipios(self, rows):
        """Carga los indicadores por codigo INE sin modificar viviendas."""
        accepted = rejected = 0
        for row in rows:
            code = self._codigo_municipio(row.get("municipio", ""))
            origin = row.get("codigo_municipio")
            if not code or (origin and origin != code):
                rejected += 1
                self._registrar_rechazo(row, "municipio_o_codigo_invalido")
                continue
            clean = {key: value for key, value in row.items() if key != "_id"}
            clean["codigo_municipio"] = code
            clean["es_sintetico"] = booleano_observado(row.get("es_sintetico"))
            for name in ("salario_medio_joven_mes", "poblacion_total", "paro_juvenil_pct"):
                if name in clean:
                    clean[name] = numero_observado(clean[name])
            # Actualizar subcampos evita borrar indicadores de otras fuentes.
            # Un valor ausente solo se inicializa al crear el municipio.
            fields = {}
            for key, value in clean.items():
                if isinstance(value, dict):
                    fields.update({f"{key}.{name}": item for name, item in value.items()})
                else:
                    fields[key] = value
            observed = {key: value for key, value in fields.items() if value is not None}
            absent = {key: None for key, value in fields.items() if value is None}
            update = {"$set": observed}
            if absent:
                update["$setOnInsert"] = absent
            self.municipios_col.update_one({"codigo_municipio": code}, update, upsert=True)
            accepted += 1
        return accepted, rejected

    def _registrar_rechazo(self, row: Dict[str, Any], motivo: str) -> None:
        """Registro estable de rechazo; el original permanece tambien en raw/HDFS."""
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()
        self.rechazos_col.update_one({"huella": digest}, {"$set": {"motivo": motivo, "registro": row}}, upsert=True)

    def cargar_anuncios(self, rows) -> tuple[int, int]:
        """Persistencia compartida por carga de ficheros y consumidor Kafka."""
        accepted = rejected = 0
        for raw in rows:
            doc = self._normalizar_anuncio(raw)
            if doc is None:
                self._registrar_rechazo(raw, "identidad_o_municipio_invalido")
                rejected += 1
                continue
            key = {"fuente": doc["fuente"], "id_origen": doc["id_origen"]}
            self.viviendas_col.update_one(key, {"$set": doc}, upsert=True)
            accepted += 1
        return accepted, rejected

    def _normalizar_anuncio(self, ad: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """No infiere precio, area, ascensor ni fianza a partir de su ausencia."""
        mun = primer_valor(ad.get("municipio"), ad.get("mun"))
        code = self._codigo_municipio(mun)
        supplied = primer_valor(ad.get("codigo_municipio"), ad.get("cod"))
        if not code or (supplied is not None and (not isinstance(supplied, str) or not re.fullmatch(r"[0-9]{5}", supplied) or supplied != code)):
            logger.warning("Registro %s: municipio/INE no reconocido o contradictorio", ad.get("id"))
            return None
        identity = primer_valor(ad.get("id_origen"), ad.get("id"))
        if identity is None:
            return None
        caracteristicas = ad.get("caracteristicas") or {}
        if not isinstance(caracteristicas, dict):
            caracteristicas = {}
        price = numero_observado(ad.get("precio"), minimo=0.01)
        area = numero_observado(primer_valor(ad.get("superficie_m2"), ad.get("m2")), minimo=0.01)
        source = ad.get("fuente") or "fuente_no_documentada"
        synthetic = booleano_observado(ad.get("es_sintetico"))
        provenance = ad.get("procedencia") or {}
        try:
            if isinstance(provenance, str):
                provenance = json.loads(provenance)
            if not isinstance(provenance, dict):
                raise ValueError("Procedencia no es un objeto JSON")
            provenance = dict(provenance)
        except (ValueError, TypeError):
            logger.warning("Registro %s: procedencia no valida", identity)
            return None
        record_type = ad.get("tipo_registro") or "anuncio"
        if record_type not in {"anuncio", "promocion"}:
            logger.warning("Registro %s: unidad de observacion no reconocida", identity)
            return None
        provenance.setdefault("estado", "demo" if synthetic is True else "observado" if synthetic is False else "no_verificado")
        if ad.get("archivo_origen"):
            provenance.setdefault("archivo", ad["archivo_origen"])
            provenance["archivo_normalizado"] = ad["archivo_origen"]
        def feature(name):
            return primer_valor(caracteristicas.get(name), ad.get(name))
        operation = str(ad.get("tipo_operacion") or "desconocida").strip().lower()
        return {
            "id_origen": str(identity), "fuente": source,
            "municipio": mun, "codigo_municipio": code,
            "provincia": PROVINCIAS[code[:2]],
            "titulo": ad.get("titulo"), "barrio": ad.get("barrio"), "direccion": ad.get("direccion"),
            "tipo_operacion": operation, "precio": price, "superficie_m2": area,
            "precio_m2": price / area if price is not None and area is not None else None,
            "portal_origen": ad.get("portal_origen") or source,
            "url": ad.get("url"), "fecha_extraccion": ad.get("fecha_extraccion"),
            "es_sintetico": synthetic, "procedencia": provenance,
            "tipo_registro": record_type, "lote_ingesta": ad.get("lote_ingesta"),
            "caracteristicas": {
                **{name: numero_observado(feature(name), entero=True) for name in ("habitaciones", "banos", "fianza_meses", "distancia_transporte_m")},
                "ascensor": booleano_observado(feature("ascensor")),
            },
            "es_protegida": booleano_observado(ad.get("es_protegida")) if "es_protegida" in ad else operation in {"vpo", "aroc"},
        }

    def _generar_catalogo_multiportal_completo(self) -> List[Dict[str, Any]]:
        """Fixtures didacticos declarados como sinteticos, sin peticiones a portales."""
        scraper = MultiPortalHousingScraper(demo_mode=True)
        res = scraper.extraer_todos_los_portales()
        rows = [ad.to_dict() for ad in res.items]
        for identity, mun, code, price, area in [
            ("vpo_bilbao_01", "Bilbao", "48020", 450, 72),
            ("vpo_vitoria_01", "Vitoria-Gasteiz", "01059", 380, 75),
            ("vpo_donostia_01", "Donostia-San Sebasti\u00e1n", "20069", 520, 68),
            ("vpo_barakaldo_01", "Barakaldo", "48013", 420, 70),
            ("vpo_getxo_01", "Getxo", "48044", 480, 70),
            ("vpo_irun_01", "Irun", "20045", 410, 65),
        ]:
            rows.append({"id": identity, "mun": mun, "cod": code, "precio": price, "m2": area,
                         "tipo_operacion": "alquiler", "fuente": "demo_vpo", "es_protegida": True, "es_sintetico": True})
        return [doc for row in rows if (doc := self._normalizar_anuncio(row)) is not None]

    def _generar_datos_municipios_base(self) -> Dict[str, Dict[str, Any]]:
        """
        Modelado de datos para los municipios vascos representativos,
        unificados por su código INE oficial de 5 dígitos.
        """
        municipios_lista = [
            ("Bilbao", "48020", "Bizkaia", 346000, 52400, 1380.0, 18250.0, 14.8, "ALTO"),
            ("Donostia-San Sebastián", "20069", "Gipuzkoa", 188000, 27800, 1420.0, 21500.0, 11.2, "MUY_ALTO"),
            ("Vitoria-Gasteiz", "01059", "Araba", 254000, 38900, 1360.0, 19100.0, 13.5, "MODERADO"),
            ("Barakaldo", "48013", "Bizkaia", 101000, 15600, 1310.0, 16800.0, 15.2, "MODERADO"),
            ("Getxo", "48044", "Bizkaia", 77000, 10500, 1490.0, 23400.0, 10.5, "ALTO"),
            ("Irun", "20045", "Gipuzkoa", 62000, 8900, 1330.0, 17200.0, 14.1, "MODERADO"),
            ("Portugalete", "48078", "Bizkaia", 45000, 6200, 1290.0, 16100.0, 15.8, "MODERADO"),
            ("Santurtzi", "48082", "Bizkaia", 46000, 6500, 1280.0, 15900.0, 16.0, "MODERADO"),
            ("Basauri", "48015", "Bizkaia", 40000, 5800, 1300.0, 16500.0, 14.9, "MODERADO"),
            ("Errenteria", "20067", "Gipuzkoa", 39000, 5400, 1310.0, 16900.0, 13.8, "ALTO"),
            ("Zarautz", "20079", "Gipuzkoa", 23000, 3200, 1440.0, 21800.0, 9.8, "MUY_ALTO"),
            ("Durango", "48027", "Bizkaia", 30000, 4400, 1350.0, 18400.0, 12.4, "MODERADO"),
        ]

        base = {}
        for mun, cod, prov, pob_tot, pob_jov, sal_jov, renta, paro, tension in municipios_lista:
            base[mun] = {
                "municipio": mun,
                "codigo_municipio": cod,
                "provincia": prov,
                "poblacion_total": pob_tot,
                "poblacion_joven_18_34": pob_jov,
                "salario_medio_joven_mes": sal_jov,
                "renta_media_persona": renta,
                "paro_juvenil_pct": paro,
                "programas_ayuda": [
                    {"nombre": "Gaztelagun", "cobertura_max": 300.0, "requisito_edad_max": 35},
                    {"nombre": "Emantzipa", "cobertura_max": 300.0, "requisito_edad_max": 30},
                    {"nombre": "VPO_Alquiler_Alokabide", "cobertura_max": 400.0, "requisito_edad_max": 35}
                ],
                "nivel_tension_inmobiliaria": tension
            }

        for doc in base.values():
            doc["es_sintetico"] = True
            doc["procedencia"] = {"estado": "demo", "fuente": "fixture_docente", "ano_referencia": 2025}
        return base
