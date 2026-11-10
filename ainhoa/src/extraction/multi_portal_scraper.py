"""
src/extraction/multi_portal_scraper.py
Scraper multicanal para los portales adicionales solicitados para Euskadi:
- EnAlquiler (Euskadi)
- Inmobiliaria Chomon (Bilbao y Bizkaia)
- Inmobiliaria Quorum (Bizkaia y Araba)
- YaEncontre (País Vasco)
- Milanuncios (Euskadi)

Cada anuncio extraído incluye municipio, código INE de 5 dígitos, precio,
superficie, fianza, ascensor y distancia al transporte.
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
import json
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from .normalization import numero_observado

from src.extraction.models import HousingAd, ExtractionResult, resolver_codigo_ine

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,eu;q=0.8,en;q=0.7",
}

# Fixtures docentes: NO son anuncios verificados y NO deben alimentar informes reales.
PORTAL_SAMPLE_DATA = {
    "EnAlquiler": [
        {"id": "enalquiler_01", "mun": "Bilbao", "barrio": "Deusto", "dir": "Avenida Lehendakari Aguirre", "precio": 790.0, "m2": 65.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 120},
        {"id": "enalquiler_02", "mun": "Barakaldo", "barrio": "Lasesarre", "dir": "Calle Murrieta", "precio": 680.0, "m2": 58.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 250},
        {"id": "enalquiler_03", "mun": "Vitoria-Gasteiz", "barrio": "Zabalgana", "dir": "Paseo de la Unesco", "precio": 710.0, "m2": 72.0, "hab": 2, "ban": 1, "fianza": 2, "asc": True, "transp": 300},
        {"id": "enalquiler_04", "mun": "Donostia-San Sebastián", "barrio": "Amara", "dir": "Avenida de Madrid", "precio": 950.0, "m2": 60.0, "hab": 2, "ban": 1, "fianza": 2, "asc": True, "transp": 150},
        {"id": "enalquiler_05", "mun": "Getxo", "barrio": "Algorta", "dir": "Calle Telletxe", "precio": 890.0, "m2": 70.0, "hab": 2, "ban": 1, "fianza": 1, "asc": False, "transp": 180},
        {"id": "enalquiler_06", "mun": "Portugalete", "barrio": "Centro", "dir": "Calle Carlos VII", "precio": 650.0, "m2": 55.0, "hab": 1, "ban": 1, "fianza": 1, "asc": True, "transp": 90},
    ],
    "Inmobiliaria_Chomon": [
        {"id": "chomon_01", "mun": "Bilbao", "barrio": "Santutxu", "dir": "Calle Zabalbide", "precio": 750.0, "m2": 62.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 100},
        {"id": "chomon_02", "mun": "Bilbao", "barrio": "Indautxu", "dir": "Calle Alameda Urquijo", "precio": 920.0, "m2": 75.0, "hab": 2, "ban": 2, "fianza": 2, "asc": True, "transp": 80},
        {"id": "chomon_03", "mun": "Barakaldo", "barrio": "Rontegui", "dir": "Calle Castilla la Mancha", "precio": 640.0, "m2": 52.0, "hab": 2, "ban": 1, "fianza": 1, "asc": False, "transp": 320},
        {"id": "chomon_04", "mun": "Basauri", "barrio": "Ariz", "dir": "Calle Valencia", "precio": 630.0, "m2": 58.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 200},
        {"id": "chomon_05", "mun": "Santurtzi", "barrio": "Mamariga", "dir": "Calle Regales", "precio": 620.0, "m2": 54.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 280},
    ],
    "Inmobiliaria_Quorum": [
        {"id": "quorum_01", "mun": "Bilbao", "barrio": "Abando", "dir": "Calle Colón de Larreátegui", "precio": 1100.0, "m2": 85.0, "hab": 3, "ban": 2, "fianza": 2, "asc": True, "transp": 60},
        {"id": "quorum_02", "mun": "Vitoria-Gasteiz", "barrio": "Lovaina", "dir": "Calle Ramiro de Maeztu", "precio": 740.0, "m2": 68.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 140},
        {"id": "quorum_03", "mun": "Vitoria-Gasteiz", "barrio": "Salburua", "dir": "Bulevar de Salburua", "precio": 690.0, "m2": 74.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 220},
        {"id": "quorum_04", "mun": "Getxo", "barrio": "Las Arenas", "dir": "Calle Mayor", "precio": 960.0, "m2": 78.0, "hab": 2, "ban": 2, "fianza": 2, "asc": True, "transp": 110},
        {"id": "quorum_05", "mun": "Durango", "barrio": "Centro", "dir": "Calle Askatasun Etorbidea", "precio": 660.0, "m2": 64.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 350},
    ],
    "YaEncontre": [
        {"id": "yaencontre_01", "mun": "Donostia-San Sebastián", "barrio": "Gros", "dir": "Calle Zabaleta", "precio": 1150.0, "m2": 70.0, "hab": 2, "ban": 1, "fianza": 2, "asc": True, "transp": 180},
        {"id": "yaencontre_02", "mun": "Irun", "barrio": "Centro", "dir": "Paseo de Colón", "precio": 690.0, "m2": 66.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 90},
        {"id": "yaencontre_03", "mun": "Errenteria", "barrio": "Galtzaraborda", "dir": "Calle Biteri", "precio": 670.0, "m2": 59.0, "hab": 2, "ban": 1, "fianza": 1, "asc": False, "transp": 210},
        {"id": "yaencontre_04", "mun": "Zarautz", "barrio": "Centro", "dir": "Calle Nafarroa", "precio": 890.0, "m2": 62.0, "hab": 2, "ban": 1, "fianza": 2, "asc": True, "transp": 250},
    ],
    "Milanuncios": [
        {"id": "milanuncios_01", "mun": "Bilbao", "barrio": "San Ignacio", "dir": "Calle Arturo Campión", "precio": 620.0, "m2": 50.0, "hab": 1, "ban": 1, "fianza": 1, "asc": True, "transp": 110},
        {"id": "milanuncios_02", "mun": "Barakaldo", "barrio": "Cruces", "dir": "Calle La Inmaculada", "precio": 590.0, "m2": 48.0, "hab": 1, "ban": 1, "fianza": 1, "asc": False, "transp": 160},
        {"id": "milanuncios_03", "mun": "Vitoria-Gasteiz", "barrio": "Judimendi", "dir": "Calle Olaguíbel", "precio": 580.0, "m2": 55.0, "hab": 2, "ban": 1, "fianza": 1, "asc": True, "transp": 200},
        {"id": "milanuncios_04", "mun": "Eibar", "barrio": "Urki", "dir": "Calle Torrekua", "precio": 540.0, "m2": 52.0, "hab": 2, "ban": 1, "fianza": 1, "asc": False, "transp": 380},
    ]
}


class MultiPortalHousingScraper:
    """Scraper modular unificado para portales inmobiliarios vascos."""

    def __init__(self, timeout: int = 10, demo_mode: bool = False):
        self.timeout = timeout
        self.demo_mode = demo_mode
        self.errores = []
        self._source_url = ""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def extraer_portal(self, nombre_portal: str, url: str) -> List[HousingAd]:
        """Respeta robots.txt; un error de red no se convierte en datos reales."""
        if self.demo_mode:
            return self._obtener_catalogo_verificado(nombre_portal)
        self._source_url = url
        try:
            origin = urlparse(url)
            robots_url = f"{origin.scheme}://{origin.netloc}/robots.txt"
            response = self.session.get(robots_url, timeout=self.timeout)
            parser = RobotFileParser()
            if response.status_code == 200:
                parser.parse(response.text.splitlines())
                if not parser.can_fetch(self.session.headers['User-Agent'], url):
                    self.errores.append(f"{nombre_portal}: robots.txt no permite esta ruta")
                    return []
            elif response.status_code != 404:
                self.errores.append(f"{nombre_portal}: robots.txt no verificable ({response.status_code})")
                return []
            time.sleep(1)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            result = self._parsear_html(nombre_portal, BeautifulSoup(response.text, 'html.parser'))
            if not result:
                self.errores.append(f"{nombre_portal}: sin anuncios estructurados verificables")
            return result
        except requests.RequestException as error:
            self.errores.append(f"{nombre_portal}: {type(error).__name__}")
            return []

    def _parsear_html(self, portal: str, soup: BeautifulSoup) -> List[HousingAd]:
        """Extrae JSON-LD publicado en HTML, sin inventar la localidad ni medidas."""
        nodes = []
        def collect(value):
            if isinstance(value, list):
                for item in value:
                    collect(item)
            elif isinstance(value, dict):
                nodes.append(value)
                for key in ('@graph', 'itemListElement', 'item', 'mainEntity', 'itemOffered'):
                    if key in value:
                        collect(value[key])
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                collect(json.loads(script.string or script.get_text()))
            except (ValueError, TypeError):
                continue
        found = {}
        for item in nodes:
            address = item.get('address')
            if not isinstance(address, dict):
                continue
            municipality = address.get('addressLocality')
            code = resolver_codigo_ine(municipality)
            offers = item.get('offers') or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if not code or not isinstance(offers, dict):
                continue
            if offers.get('priceCurrency', 'EUR') != 'EUR':
                continue
            price = numero_observado(offers.get('price'), minimo=0.01)
            detail = item.get('url') or offers.get('url')
            if not detail or price is None:
                continue
            detail = urljoin(self._source_url, str(detail))
            if urlparse(detail).scheme not in ('http', 'https'):
                continue
            floor = item.get('floorSize') or {}
            area = numero_observado(floor.get('value'), minimo=0.01) if isinstance(floor, dict) and floor.get('unitCode', 'MTK') in ('MTK', 'm2') else None
            identity = hashlib.sha256(detail.encode()).hexdigest()[:20]
            found[detail] = HousingAd(
                id=f'{portal.lower()}_{identity}', fuente=f'{portal}_Scraping', portal_origen=portal,
                tipo_operacion='alquiler', municipio=municipality, codigo_municipio=code,
                precio=price, superficie_m2=area,
                habitaciones=numero_observado(item.get('numberOfRooms'), entero=True),
                direccion=address.get('streetAddress'), titulo=item.get('name'),
                descripcion=item.get('description'), url=detail, es_sintetico=False,
            )
        return list(found.values())

    def _obtener_catalogo_verificado(self, portal: str) -> List[HousingAd]:
        """Devuelve fixtures sinteticos. El nombre se mantiene por compatibilidad."""
        items = PORTAL_SAMPLE_DATA.get(portal, [])
        resultado = []
        for d in items:
            cod_ine = resolver_codigo_ine(d["mun"])
            prov = "Bizkaia" if cod_ine.startswith("48") else ("Gipuzkoa" if cod_ine.startswith("20") else "Araba")
            
            ad = HousingAd(
                id=d["id"],
                fuente=f"{portal}_Scraping",
                portal_origen=portal,
                tipo_operacion="alquiler",
                municipio=d["mun"],
                codigo_municipio=cod_ine,
                provincia=prov,
                barrio=d.get("barrio"),
                direccion=d.get("dir"),
                precio=d["precio"],
                superficie_m2=d["m2"],
                habitaciones=d["hab"],
                banos=d["ban"],
                ascensor=d.get("asc", True),
                fianza_meses=d.get("fianza", 1),
                distancia_transporte_m=d.get("transp", 150),
                titulo=f"Piso en alquiler en {d['mun']} ({d.get('barrio', '')})",
                descripcion=f"Vivienda de {d['m2']} m² con {d['hab']} dormitorios en {d.get('dir')}. Ideal jóvenes y parejas.",
                url=None,
                es_sintetico=True
            )
            resultado.append(ad)
        return resultado

    def extraer_todos_los_portales(self) -> ExtractionResult:
        """Extrae anuncios de todos los portales inmobiliarios solicitados."""
        portales = {
            "EnAlquiler": "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html",
            "Inmobiliaria_Chomon": "https://www.chomon.net/alquiler",
            "Inmobiliaria_Quorum": "https://www.inmobiliariaquorum.com/alquiler/",
            "YaEncontre": "https://www.yaencontre.com/alquiler/viviendas/pais-vasco",
            "Milanuncios": "https://www.milanuncios.com/alquiler-de-viviendas-en-pais-vasco/"
        }

        todos = []
        for nombre, url in portales.items():
            ads = self.extraer_portal(nombre, url)
            todos.extend(ads)

        return ExtractionResult(
            fuente="MultiPortal_Euskadi",
            total_registros=len(todos),
            items=todos,
            errores=self.errores,
        )
