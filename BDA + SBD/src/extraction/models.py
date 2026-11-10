"""
src/extraction/models.py - Modelos de datos para anuncios y promociones de vivienda.
Soporta código INE oficial de 5 dígitos para uniones relacionales en MongoDB ($lookup)
y campos de características detalladas (fianza, ascensor, planta, transporte).
"""

import re
import unicodedata
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone

# Nomenclátor oficial de códigos INE de 5 dígitos de municipios de Euskadi
INE_MUNICIPAL_CODES = {
    "Bilbao": "48020",
    "Barakaldo": "48013",
    "Donostia-San Sebastián": "20069",
    "Donostia / San Sebastián": "20069",
    "Donostia": "20069",
    "San Sebastián": "20069",
    "Vitoria-Gasteiz": "01059",
    "Vitoria": "01059",
    "Getxo": "48044",
    "Irun": "20045",
    "Irún": "20045",
    "Portugalete": "48078",
    "Santurtzi": "48082",
    "Basauri": "48015",
    "Errenteria": "20067",
    "Rentería": "20067",
    "Zarautz": "20079",
    "Durango": "48027",
    "Eibar": "20030",
    "Arrasate / Mondragón": "20055",
    "Arrasate": "20055",
    "Mondragón": "20055",
    "Bermeo": "48017",
    "Gernika-Lumo": "48046",
    "Amurrio": "01002",
    "Laudio / Llodio": "01036",
    "Llodio": "01036",
    "Leioa": "48054",
    "Sestao": "48084",
    "Galdakao": "48036",
    "Hernani": "20040",
    "Tolosa": "20071"
}


def _normalizar_nombre_municipio(nombre: str) -> str:
    """Normaliza tildes y separadores sin aceptar coincidencias parciales."""
    if not isinstance(nombre, str):
        return ""
    sin_tildes = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", sin_tildes.casefold()))


_ALIASES_INE = {
    _normalizar_nombre_municipio(nombre): codigo
    for nombre, codigo in INE_MUNICIPAL_CODES.items()
}


def resolver_codigo_ine(municipio: str) -> Optional[str]:
    """Resuelve un nombre conocido; un municipio desconocido devuelve None.

    El catálogo es un subconjunto de municipios vascos y no debe servir para
    inventar la localización de un anuncio cuando aún no está en él.
    """
    clave = _normalizar_nombre_municipio(municipio)
    return _ALIASES_INE.get(clave) if clave else None


class HousingAd(BaseModel):
    """
    Modelo unificado para un anuncio o promoción inmobiliaria en Euskadi.
    Conserva los campos reales obtenidos e incorpora el código INE municipal.
    """
    id: str = Field(..., description="Identificador único del anuncio o promoción")
    fuente: str = Field(..., description="Nombre de la fuente (p. ej. 'Habitaclia', 'EnAlquiler', 'Chomon', 'Quorum', 'Pisos.com', 'OpenData_Visesa')")
    portal_origen: Optional[str] = Field(None, description="Portal de origen específico")
    tipo_operacion: str = Field(..., description="Tipo de régimen: 'alquiler', 'compraventa', 'aroc' o 'vpo'")
    municipio: str = Field(..., description="Municipio de Euskadi")
    codigo_municipio: Optional[str] = Field(None, description="Código INE de 5 dígitos (clave común MongoDB)")
    provincia: Optional[str] = Field(None, description="Territorio histórico (Bizkaia, Gipuzkoa, Araba)")
    barrio: Optional[str] = Field(None, description="Barrio o zona del municipio")
    direccion: Optional[str] = Field(None, description="Dirección o ubicación pública de la vivienda")
    precio: Optional[float] = Field(None, description="Precio en euros (€/mes en alquiler o € total en compra)")
    superficie_m2: Optional[float] = Field(None, description="Superficie útil o construida en m²")
    habitaciones: Optional[int] = Field(None, description="Número de dormitorios")
    banos: Optional[int] = Field(None, description="Número de baños")
    planta: Optional[str] = Field(None, description="Altura o planta del inmueble")
    ascensor: Optional[bool] = Field(None, description="Si dispone de ascensor")
    fianza_meses: Optional[int] = Field(None, description="Meses de fianza requerida")
    distancia_transporte_m: Optional[int] = Field(None, description="Distancia estimada en metros al transporte público")
    titulo: Optional[str] = Field(None, description="Título del anuncio o nombre de la promoción")
    descripcion: Optional[str] = Field(None, description="Descripción original del anuncio")
    url: Optional[str] = Field(None, description="Enlace público al anuncio o expediente")
    fecha_extraccion: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Fecha y hora de obtención en formato ISO 8601"
    )
    es_sintetico: bool = Field(False, description="Flag que identifica si el dato es de respaldo o en vivo")

    tipo_registro: Literal["anuncio", "promocion"] = "anuncio"
    procedencia: Dict[str, Any] = Field(default_factory=dict, description="Origen, fecha y huella del registro")
    lote_ingesta: Optional[str] = Field(None, description="Identificador de la ejecucion; no modifica el ID de origen")

    def model_post_init(self, __context: Any) -> None:
        """Completa el INE conocido, sin inventar códigos municipales."""
        codigo_esperado = resolver_codigo_ine(self.municipio)
        if self.codigo_municipio is None:
            self.codigo_municipio = codigo_esperado
        elif not re.fullmatch(r"\d{5}", self.codigo_municipio):
            raise ValueError("codigo_municipio debe contener exactamente cinco dígitos")
        elif codigo_esperado and self.codigo_municipio != codigo_esperado:
            raise ValueError(
                f"Código INE {self.codigo_municipio} incompatible con {self.municipio!r}"
            )
        if not self.portal_origen:
            self.portal_origen = self.fuente.split("_")[0]

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ExtractionResult(BaseModel):
    """Contenedor de resultados de una operación de extracción."""
    fuente: str
    total_registros: int
    fecha_ejecucion: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    items: List[HousingAd]
    errores: List[str] = Field(default_factory=list)
