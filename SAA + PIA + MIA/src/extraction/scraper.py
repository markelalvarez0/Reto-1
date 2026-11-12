"""
src/extraction/scraper.py - Web Scraper ético para anuncios inmobiliarios en Euskadi.

Obtiene anuncios reales de alquiler y venta en municipios vascos (Bilbao, Donostia,
Vitoria-Gasteiz) cumpliendo con robots.txt, pausas de cortesía y gestión de errores.
"""

import time
import re
import json
import csv
import os
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .models import HousingAd, ExtractionResult
from .scraping_http import ScrapingHTTP, observed_municipality, euro_price, residential_title, USER_AGENT, published_rental_conditions


class HabitacliaScraper:
    """Scraper para portales inmobiliarios enfocado en el mercado residencial de Euskadi."""

    DEFAULT_TARGETS = [
        {"municipio": "Bilbao", "tipo": "alquiler", "url": "https://www.habitaclia.com/alquiler/viviendas/bizkaia-provincia/bilbao/s"},
        {"municipio": "Donostia-San Sebastián", "tipo": "alquiler", "url": "https://www.habitaclia.com/alquiler/viviendas/gipuzkoa-provincia/donostia-san-sebastian/s"},
        {"municipio": "Vitoria-Gasteiz", "tipo": "alquiler", "url": "https://www.habitaclia.com/alquiler/viviendas/araba-alava-provincia/vitoria-gasteiz/s"},
        {"municipio": "Bilbao", "tipo": "compraventa", "url": "https://www.habitaclia.com/comprar-vivienda-en-bilbao/"}
    ]

    def __init__(self, request_delay_seconds: float = 1.5, timeout_seconds: int = 12, *, archive_dir='data/scraping/sources'):
        self.delay = request_delay_seconds
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,eu;q=0.8,en;q=0.7"
        })
        self.http = ScrapingHTTP(self.session, 'www.habitaclia.com', delay=self.delay,
                                 timeout=self.timeout, archive_dir=archive_dir)

    def _safe_get(self, url: str, **kwargs) -> requests.Response:
        """Robots y TLS obligatorios; no permite anular la politica de captura."""
        if kwargs:
            raise ValueError('No se admiten opciones que alteren la captura verificada')
        return self.http.get(url)

    def scrape_targets(self, targets: Optional[List[Dict[str, str]]] = None, max_items_per_target: int = 20) -> ExtractionResult:
        """
        Ejecuta el raspado web sobre las páginas objetivo definidas.
        Retorna un ExtractionResult consolidado con anuncios validados.
        """
        targets_to_run = targets or self.DEFAULT_TARGETS
        all_ads: List[HousingAd] = []
        errores: List[str] = []

        for target in targets_to_run:
            muni = target["municipio"]
            tipo_op = target["tipo"]
            url = target["url"]

            try:
                ads = self._scrape_page(url, muni, tipo_op, max_items=max_items_per_target)
                all_ads.extend(ads)
            except Exception as e:
                errores.append(f"Fallo al raspar {url} ({muni}): {e}")
                if self.http.robots is None or self.http.stopped:
                    break  # No repetir el mismo bloqueo de robots para cada municipio.

            time.sleep(self.delay)

        return ExtractionResult(
            fuente="Habitaclia_Scraping",
            total_registros=len(all_ads),
            items=all_ads,
            errores=errores
        )

    def _scrape_page(self, url: str, municipio: str, tipo_operacion: str, max_items: int) -> List[HousingAd]:
        """Descarga y parsea una página web individual de anuncios."""
        resp = self._safe_get(url)
        if resp.status_code == 429:
            raise RuntimeError(f"HTTP 429 Too Many Requests recibido de {url}")
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")
        articles = soup.find_all("article")
        if not articles:
            articles = soup.find_all("div", class_=re.compile(r"list-item|property-item"))

        results: List[HousingAd] = []
        for idx, art in enumerate(articles):
            if len(results) >= max_items:
                break

            ad = self._extract_article_data(art, municipio, tipo_operacion, idx, url)
            if ad and ad.codigo_municipio and ad.precio is not None:
                ad.procedencia = self.http.last_capture.copy()
                ad.procedencia['condiciones_publicadas'] = published_rental_conditions(ad)
                results.append(ad)
        if not results:
            raise ValueError('HTML sin anuncios interpretables; no se acredita una captura de mercado')
        return results

    def _extract_article_data(self, article, municipio: str, tipo_operacion: str, index: int, source_url: str) -> Optional[HousingAd]:
        """Extrae los campos individuales de un elemento HTML de anuncio."""
        title_tag = article.find(["h2", "h3"])
        link_tag = (title_tag.find("a", href=True) if title_tag else None) or article.find("a", href=True)
        titulo = title_tag.get_text(strip=True) if title_tag else None
        href = link_tag["href"] if link_tag else None
        full_url = href if (href and href.startswith("http")) else (f"https://www.habitaclia.com{href}" if href else source_url)

        data_id = article.get("data-id") or article.get("id")
        if not data_id and href:
            match_id = re.search(r"(\d+)\.htm", href)
            data_id = match_id.group(1) if match_id else hashlib.sha256(full_url.encode()).hexdigest()[:24]
        elif not data_id:
            return None  # Sin identidad de origen no se fabrica una dependiente de la hora.

        precio = None
        price_tag = article.find(class_=re.compile(r"font-2|price|precio"))
        if price_tag is None:
            price_tag = article.select_one('span.text-display-4')
        if price_tag:
            precio = euro_price(price_tag.get_text(' ', strip=True))

        superficie_m2 = None
        habitaciones = None
        banos = None

        features_tag = article.find(class_=re.compile(r"feature|details|info"))
        text_content = (features_tag.get_text(" ", strip=True) if features_tag else "") + " " + article.get_text(" ", strip=True)

        sup_match = re.search(r"(\d+(?:[\.,]\d+)?)\s*m[2²]", text_content, re.IGNORECASE)
        if sup_match:
            try:
                superficie_m2 = float(sup_match.group(1).replace(",", "."))
            except ValueError:
                pass

        hab_match = re.search(r"(\d+)\s*(?:hab|dorm)", text_content, re.IGNORECASE)
        if hab_match:
            try:
                habitaciones = int(hab_match.group(1))
            except ValueError:
                pass

        ban_match = re.search(r"(\d+)\s*baño", text_content, re.IGNORECASE)
        if ban_match:
            try:
                banos = int(ban_match.group(1))
            except ValueError:
                pass

        loc_tag = article.find(class_=re.compile(r"location|ubicacion|zone"))
        if loc_tag is None:
            loc_tag = article.select_one('p span.truncate')
        barrio = loc_tag.get_text(strip=True) if loc_tag else None
        municipio = observed_municipality(barrio)

        desc_tag = article.find(class_=re.compile(r'description|descripcion'))
        descripcion = desc_tag.get_text(strip=True) if desc_tag else None

        if not residential_title(titulo):
            return None

        clean_id = f"habitaclia_{data_id}" if not str(data_id).startswith("habitaclia_") else str(data_id)

        return HousingAd(
            id=clean_id,
            fuente="Habitaclia_Scraping",
            tipo_operacion=tipo_operacion,
            municipio=municipio,
            provincia=None,
            barrio=barrio,
            direccion=None,
            precio=precio,
            superficie_m2=superficie_m2,
            habitaciones=habitaciones,
            banos=banos,
            titulo=titulo,
            descripcion=descripcion,
            url=full_url,
            fecha_extraccion=datetime.now(timezone.utc).isoformat(),
            es_sintetico=False
        )

    def save_to_json(self, result: ExtractionResult, filepath: str) -> None:
        """Exporta el resultado a formato JSON indentado."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    def save_to_csv(self, result: ExtractionResult, filepath: str) -> None:
        """Exporta el resultado a formato CSV estructurado."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        fieldnames = [
            "id", "fuente", "tipo_operacion", "municipio", "provincia", "barrio",
            "direccion", "precio", "superficie_m2", "habitaciones", "banos",
            "titulo", "descripcion", "url", "fecha_extraccion", "es_sintetico"
        ]
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for item in result.items:
                writer.writerow(item.to_dict())
