"""
src/extraction/models.py - Modelos de datos para anuncios y promociones de vivienda.
Soporta código INE oficial de 5 dígitos para uniones relacionales en MongoDB ($lookup)
y campos de características detalladas (fianza, ascensor, planta, transporte).
"""

from typing import Optional, List, Dict, Any
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
    "Irun": "20045" if "Irun" else "20045",
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


def resolver_codigo_ine(municipio: str) -> str:
    """Devuelve el código INE de 5 dígitos a partir del nombre del municipio."""
    if not municipio:
        return "48020"
    for nom, cod in INE_MUNICIPAL_CODES.items():
        if nom.lower() in municipio.lower() or municipio.lower() in nom.lower():
            return cod
    return "48020"


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

    def model_post_init(self, __context: Any) -> None:
        """Asigna automáticamente el código INE si no está presente."""
        if not self.codigo_municipio and self.municipio:
            self.codigo_municipio = resolver_codigo_ine(self.municipio)
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
