"""
src/indicators/transport_client.py
Módulo de indicadores de transporte y conectividad municipal para Euskadi:
- Consorcio de Transportes de Bizkaia (CTB): Red de Metro Bilbao y Bizkaibus.
- Euskotren: Conectividad ferroviaria y tranviaria entre territorios.
- TUVISA (Vitoria-Gasteiz) y Dbus (Donostia): Cobertura urbana.

Genera el 'Indice de Conectividad y Transporte' (1 a 10) para cada municipio,
clave para evaluar la viabilidad de independizarse en municipios metropolitanos.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

from src.extraction.models import resolver_codigo_ine


class ConectividadTransporteMunicipal(BaseModel):
    codigo_municipio: str
    municipio: str
    provincia: str
    red_metro: bool = False
    red_cercanias_euskotren: bool = False
    red_tranvia: bool = False
    lineas_autobus_interurbano: int = 1
    frecuencia_pico_minutos: int = 15
    tiempo_centro_capital_minutos: int = 10
    indice_conectividad: float = Field(..., ge=1.0, le=10.0, description="Índice de 1 a 10")
    observaciones: str


DATOS_CONECTIVIDAD_EUSKADI = [
    {
        "cod": "48020", "mun": "Bilbao", "prov": "Bizkaia",
        "metro": True, "tren": True, "tranvia": True, "buses": 42,
        "frec": 3, "tiempo": 0, "indice": 10.0,
        "obs": "Intermodal Abando y San Mamés. Cobertura plena de Metro Bilbao L1 y L2, Tranvía y Bilbobus."
    },
    {
        "cod": "48013", "mun": "Barakaldo", "prov": "Bizkaia",
        "metro": True, "tren": True, "tranvia": False, "buses": 18,
        "frec": 5, "tiempo": 12, "indice": 9.2,
        "obs": "Metro Bilbao Línea 2 (4 estaciones), Cercanías Renfe C1 y C2, y líneas de Bizkaibus."
    },
    {
        "cod": "20069", "mun": "Donostia-San Sebastián", "prov": "Gipuzkoa",
        "metro": True, "tren": True, "tranvia": False, "buses": 35,
        "frec": 6, "tiempo": 0, "indice": 9.5,
        "obs": "Topo Euskotren (Topo de San Sebastián), Cercanías Renfe y red urbana de Dbus."
    },
    {
        "cod": "01059", "mun": "Vitoria-Gasteiz", "prov": "Araba",
        "metro": False, "tren": True, "tranvia": True, "buses": 24,
        "frec": 7, "tiempo": 0, "indice": 8.9,
        "obs": "Tranvía de Vitoria (Ibaiondo/Abetxuko/Salburua/Zabalgana), BEI eléctrico y TUVISA."
    },
    {
        "cod": "48044", "mun": "Getxo", "prov": "Bizkaia",
        "metro": True, "tren": False, "tranvia": False, "buses": 14,
        "frec": 5, "tiempo": 22, "indice": 8.8,
        "obs": "Metro Bilbao Línea 1 (6 estaciones de Areeta a Bidezabal) y Bizkaibus."
    },
    {
        "cod": "20045", "mun": "Irun", "prov": "Gipuzkoa",
        "metro": True, "tren": True, "tranvia": False, "buses": 12,
        "frec": 10, "tiempo": 25, "indice": 8.4,
        "obs": "Euskotren (Línea E2 Topo), Renfe Cercanías C1 y Lurraldebus."
    },
    {
        "cod": "48078", "mun": "Portugalete", "prov": "Bizkaia",
        "metro": True, "tren": True, "tranvia": False, "buses": 11,
        "frec": 5, "tiempo": 18, "indice": 8.9,
        "obs": "Metro Bilbao Línea 2, Cercanías C1 y Puente Bizkaia."
    },
    {
        "cod": "48082", "mun": "Santurtzi", "prov": "Bizkaia",
        "metro": True, "tren": True, "tranvia": False, "buses": 10,
        "frec": 5, "tiempo": 22, "indice": 8.6,
        "obs": "Metro Bilbao Línea 2, Cercanías C1 y Bizkaibus."
    },
    {
        "cod": "48015", "mun": "Basauri", "prov": "Bizkaia",
        "metro": True, "tren": True, "tranvia": False, "buses": 12,
        "frec": 5, "tiempo": 10, "indice": 9.0,
        "obs": "Metro Bilbao Línea 2 (Basauri y Ariz) y Cercanías Renfe C3."
    },
    {
        "cod": "20067", "mun": "Errenteria", "prov": "Gipuzkoa",
        "metro": True, "tren": True, "tranvia": False, "buses": 10,
        "frec": 10, "tiempo": 15, "indice": 8.5,
        "obs": "Euskotren Topo (frecuencias cada 7,5 min en punta) y Cercanías Renfe."
    },
    {
        "cod": "20079", "mun": "Zarautz", "prov": "Gipuzkoa",
        "metro": False, "tren": True, "tranvia": False, "buses": 8,
        "frec": 15, "tiempo": 30, "indice": 7.5,
        "obs": "Euskotren E1 Bilbao-Donostia y Lurraldebus."
    },
    {
        "cod": "48027", "mun": "Durango", "prov": "Bizkaia",
        "metro": False, "tren": True, "tranvia": False, "buses": 9,
        "frec": 15, "tiempo": 35, "indice": 7.6,
        "obs": "Euskotren E1 Bilbao-Donostia y Bizkaibus por autopista."
    }
]


class TransportConnectivityClient:
    """Cliente de evaluación de transporte y movilidad juvenil."""

    def obtener_conectividad_todos(self) -> List[ConectividadTransporteMunicipal]:
        return [
            ConectividadTransporteMunicipal(
                codigo_municipio=d["cod"],
                municipio=d["mun"],
                provincia=d["prov"],
                red_metro=d["metro"],
                red_cercanias_euskotren=d["tren"],
                red_tranvia=d["tranvia"],
                lineas_autobus_interurbano=d["buses"],
                frecuencia_pico_minutos=d["frec"],
                tiempo_centro_capital_minutos=d["tiempo"],
                indice_conectividad=d["indice"],
                observaciones=d["obs"]
            )
            for d in DATOS_CONECTIVIDAD_EUSKADI
        ]

    def obtener_conectividad_municipio(self, codigo_municipio: str) -> ConectividadTransporteMunicipal:
        for c in self.obtener_conectividad_todos():
            if c.codigo_municipio == codigo_municipio:
                return c
        return ConectividadTransporteMunicipal(
            codigo_municipio=codigo_municipio,
            municipio="Municipio Vasco",
            provincia="Bizkaia",
            red_metro=False,
            red_cercanias_euskotren=False,
            red_tranvia=False,
            lineas_autobus_interurbano=3,
            frecuencia_pico_minutos=30,
            tiempo_centro_capital_minutos=45,
            indice_conectividad=6.0,
            observaciones="Conexión por Bizkaibus/Lurraldebus/Álavabus regular."
        )
