"""Cliente REST Visesa con contratos comprobados y respaldo CSV oficial.

Una promocion no equivale a una vivienda disponible. Los precios de locales,
garajes o unidades en venta no se convierten en rentas mensuales.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from .models import HousingAd, ExtractionResult, _normalizar_nombre_municipio
from .normalization import numero_observado


class OpenDataEuskadiHousingClient:
    DEFAULT_API_URL = "https://apps.visesa.eus/ws/promocion/filtro"
    DEFAULT_CSV_FALLBACK_URL = "https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv"

    def __init__(self, api_url: Optional[str] = None, timeout_seconds: int = 15):
        self.api_url = api_url or self.DEFAULT_API_URL
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "IABD-Reto1/1.0 (academic public-data retrieval)", "Accept": "application/json"})

    def _safe_get(self, url, **kwargs):
        """Mantiene la verificacion TLS; no oculta fallos de certificados."""
        kwargs.setdefault("timeout", self.timeout_seconds)
        return self.session.get(url, **kwargs)

    @staticmethod
    def provenance(response):
        return {"estado": "respuesta_http", "url": response.url,
                "fecha_captura": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(response.content).hexdigest()}

    def parse_payload(self, data, procedencia=None):
        """Admite el contrato publicado promociones y el contrato legado rows.

        Un contrato desconocido genera un error explicito, no cero resultados
        interpretados como una descarga correcta.
        """
        if not isinstance(data, dict):
            raise ValueError("La respuesta Visesa debe ser un objeto JSON")
        key = "promociones" if "promociones" in data else "rows"
        if key not in data or not isinstance(data[key], list):
            raise ValueError("Contrato Visesa desconocido: faltan promociones/rows")
        ads, errors = [], []
        for number, row in enumerate(data[key], 1):
            try:
                if not isinstance(row, dict):
                    raise ValueError("Registro no es un objeto")
                ad = self._parse_api_row(row)
                if ad is None:
                    raise ValueError("Falta identificador o municipio")
                ad.procedencia = {**(procedencia or {"estado": "no_acreditada"}),
                                  "fila_origen": number, "contrato": key,
                                  "unidad_observacion": "promocion"}
                if key == "promociones":
                    ad.procedencia.update(modalidad_original=row.get("modalidad"),
                                          regimen_original=row.get("regimen"),
                                          estado_original=row.get("estado"),
                                          identificador_original=str(row.get("id")))
                ads.append(ad)
            except (ValueError, TypeError) as error:
                errors.append(f"Fila {number}: {error}")
        return ExtractionResult(fuente="OpenDataEuskadi_Visesa", total_registros=len(ads), items=ads, errores=errors)

    def fetch_promotions(self):
        try:
            response = self._safe_get(self.api_url)
            response.raise_for_status()
            return self.parse_payload(response.json(), self.provenance(response))
        except (requests.RequestException, ValueError) as error:
            return self._fetch_csv_fallback([f"Visesa: {error}"])

    def _parse_api_row(self, row: Dict[str, Any]) -> Optional[HousingAd]:
        if "id" in row and "nombre_promocion" in row:
            identifier = str(row.get("id") or "").strip()
            municipality = str(row.get("municipio") or "").strip()
            if not identifier or not municipality:
                return None
            mode = _normalizar_nombre_municipio(row.get("modalidad", ""))
            operation = "alquiler" if mode == "alquiler" else ("compraventa" if mode in {"venta", "compra", "compraventa"} else "vpo")
            link = str(row.get("link_informacion") or "").strip()
            if urlparse(link).scheme not in {"https", "http"}:
                link = self.api_url
            # Las unidades anidadas mezclan viviendas, locales, garajes y trasteros.
            # El contrato no declara una renta mensual por vivienda de la promocion.
            return HousingAd(id=f"visesa_{identifier}", fuente="OpenDataEuskadi_Visesa",
                             tipo_registro="promocion", tipo_operacion=operation,
                             municipio=municipality, provincia=row.get("territorio"),
                             titulo=row.get("nombre_promocion"), direccion=row.get("domicilio"),
                             url=link, precio=None, superficie_m2=None, es_sintetico=False)

        identifier = str(row.get("idContenido") or row.get("codigoInterno") or "")
        municipality = str(row.get("poblacion") or row.get("municipio") or "").strip()
        if not identifier or not municipality:
            return None
        planned = str(row.get("fechaPrevista") or "").lower()
        operation = "alquiler" if row.get("idTipoVenta") == 7 or "alquiler" in planned or "alokairu" in planned else ("compraventa" if "compra" in planned or "cv" in planned else "vpo")
        value = next((row[k] for k in ("precioMinimo", "rentaMinima", "precioCompra", "precioAlquiler") if row.get(k) is not None), None)
        rooms = numero_observado(row.get("numeroDormitorios", row.get("numeroDormitoriosMinimo")))
        return HousingAd(id=f"visesa_{identifier}", fuente="OpenDataEuskadi_Visesa", tipo_registro="promocion",
                         tipo_operacion=operation, municipio=municipality,
                         direccion=row.get("direccion") or row.get("direccionPromocion"),
                         precio=numero_observado(value), superficie_m2=numero_observado(row.get("superficie")),
                         habitaciones=int(rooms) if rooms is not None and rooms.is_integer() else None,
                         titulo=row.get("titulo"), descripcion=row.get("texto"),
                         url=self.api_url, es_sintetico=False)

    def _fetch_csv_fallback(self, prev_errors):
        from .source_snapshots import parse_etxebide_csv
        errors = list(prev_errors)
        try:
            response = self._safe_get(self.DEFAULT_CSV_FALLBACK_URL)
            response.raise_for_status()
            ads, rejected = parse_etxebide_csv(response.content, self.provenance(response))
            errors.extend(rejected)
        except (requests.RequestException, ValueError) as error:
            ads = []
            errors.append(f"Etxebide CSV: {error}")
        return ExtractionResult(fuente="OpenDataEuskadi_Etxebide_CSV", total_registros=len(ads), items=ads, errores=errors)

    def save_to_json(self, result, filepath):
        path = Path(filepath); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

    def save_to_csv(self, result, filepath):
        path = Path(filepath); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(HousingAd.model_fields))
            writer.writeheader()
            for ad in result.items:
                row = ad.to_dict()
                row["procedencia"] = json.dumps(row["procedencia"], ensure_ascii=False)
                writer.writerow(row)
