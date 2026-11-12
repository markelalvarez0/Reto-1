"""HTTP para scraping identificado, con robots, TLS y originales trazables.

La imposibilidad de verificar robots detiene el acceso al listado. No permite
redirecciones a otros dominios ni reintenta certificados sin verificación.
"""
import hashlib
import json
from pathlib import Path
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import uuid
from .models import resolver_codigo_ine


def observed_municipality(location):
    """Solo acepta el municipio publicado en la ubicación; nunca el del target."""
    # Los subtítulos actuales incluyen «Barrio (Distrito. Municipio)».
    # No dividir guiones: forman parte de Vitoria - Gasteiz y San Sebastián - Donostia.
    for part in reversed(re.split(r'[,().|]', location or '')):
        if resolver_codigo_ine(part.strip()):
            return part.strip()
    return 'No publicado'


def euro_price(text):
    """Importe español sin convertir céntimos o precios diarios en mensualidades."""
    if re.search(r'/\s*(?:dia|día|noche|semana)|\bpor\s+(?:dia|día|noche|semana)\b', text, re.I):
        return None
    match = re.search(r'(?<![-\d.,])(\d{1,3}(?:[.\s]\d{3})+(?:,\d{1,2})?|\d+(?:[,.]\d{1,2})?)\s*€', text)
    if not match:
        return None
    number = re.sub(r'\s+', '', match.group(1))
    if ',' in number:
        number = number.replace('.', '').replace(',', '.')
    elif re.fullmatch(r'\d{1,3}(?:\.\d{3})+', number):
        number = number.replace('.', '')
    value = float(number)
    return value if value > 0 else None


USER_AGENT = 'Reto1AcademicBot/1.0'


def published_rental_conditions(ad):
    """Señales textuales, no una clasificación jurídica ni garantía de uso habitual."""
    text = ' '.join((ad.titulo or '', ad.descripcion or '')).casefold()
    signals = {'temporal': r'temporal|temporada|estancias?',
               'estudiantes': r'estudiantes?|curso\s+20\d\d',
               'empresas': r'empresas?'}
    return [name for name, pattern in signals.items() if re.search(pattern, text)]


def residential_title(title):
    """Filtro conservador: no reutiliza precios de habitaciones, locales o garajes."""
    if not title or re.match(r'\s*(?:garaje|plaza|parking|local|terreno|trastero|habitaci[oó]n|nave|oficina)\b', title, re.I):
        return False
    return bool(re.search(r'\b(?:piso|casa|vivienda|apartamento|chalet|d[uú]plex|[aá]tico|estudio|loft)\b', title, re.I))


class ScrapingHTTP:
    def __init__(self, session, host, *, delay=1.5, timeout=12, archive_dir='data/scraping/sources'):
        self.session, self.host = session, host
        self.delay, self.timeout = max(1.5, delay), timeout
        self.archive_dir = Path(archive_dir)
        self.robots, self.last_request, self.last_capture = None, None, None
        self.stopped = False
        self.session.headers.update({'User-Agent': USER_AGENT})

    def _validate(self, url):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != self.host or parsed.username or parsed.password:
            raise ValueError('Solo se permite HTTPS en el dominio original del portal')

    def _request(self, url, kind):
        self._validate(url)
        if self.last_request is not None:
            wait = self.delay - (time.monotonic() - self.last_request)
            if wait > 60:
                raise RuntimeError('El crawl-delay exige esperar mas de 60 segundos; captura detenida')
            if wait > 0:
                time.sleep(wait)
        self.last_request = time.monotonic()
        response = self.session.get(url, timeout=self.timeout, verify=True, allow_redirects=False)
        data = response.content
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        name = kind + '_' + uuid.uuid4().hex + '.bin'
        path = self.archive_dir / name
        with path.open('xb') as stream:
            stream.write(data)
        record = {'archivo': name, 'url': url, 'http_status': response.status_code,
                  'fecha_utc': datetime.now(timezone.utc).isoformat(),
                  'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                  'clase': kind, 'user_agent': USER_AGENT, 'tls_verificado': True,
                  'content_type': response.headers.get('Content-Type', '')}
        # Un fichero por respuesta evita sobreescribir el manifiesto de otra ejecución.
        path.with_suffix('.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        self.last_capture = record
        if response.status_code == 429:
            self.stopped = True  # Sin nuevos intentos; no se ignora Retry-After.
        return response

    def get(self, url):
        if self.stopped:
            raise RuntimeError('Captura detenida por HTTP 429; no se reintenta este lote')
        self._validate(url)
        if self.robots is None:
            robots_url = 'https://' + self.host + '/robots.txt'
            response = self._request(robots_url, 'robots')
            if response.status_code != 200:
                raise RuntimeError('No se verifico robots.txt: HTTP ' + str(response.status_code))
            text = response.content.decode('utf-8-sig', errors='replace')
            if not re.search(r'^\s*User-agent\s*:', text, flags=re.I | re.M):
                raise RuntimeError('robots.txt no contiene directivas verificables')
            parser = RobotFileParser(robots_url)
            parser.parse(text.splitlines())
            self.robots = parser
            self.robots_capture = self.last_capture.copy()
            self.delay = max(self.delay, parser.crawl_delay(USER_AGENT) or parser.crawl_delay('*') or 0)
            rate = parser.request_rate(USER_AGENT)
            if rate and rate.requests > 0:
                self.delay = max(self.delay, rate.seconds / rate.requests)
        for _ in range(4):
            self._validate(url)
            if not self.robots.can_fetch(USER_AGENT, url):
                raise PermissionError('robots.txt no permite acceder a ' + url)
            response = self._request(url, 'listado')
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get('Location')
                if not location:
                    raise RuntimeError('Redireccion sin destino')
                url = urljoin(url, location)
                continue  # El destino vuelve a pasar dominio, robots y demora.
            response.raise_for_status()
            if response.status_code != 200 or 'html' not in response.headers.get('Content-Type', '').lower():
                raise RuntimeError('El listado no devuelve HTML HTTP 200')
            self.last_capture = {**self.last_capture, 'robots': self.robots_capture,
                                 'robots_permite': True, 'demora_segundos': self.delay}
            return response
        raise RuntimeError('Demasiadas redirecciones; no se continua la captura')


def verify_scraped_record(ad, sources_dir):
    """Revalida originales y robots antes de ingerir un anuncio capturado."""
    source = ad.get('procedencia') or {}
    host = {'Habitaclia_Scraping': 'www.habitaclia.com', 'PisosCom_Scraping': 'www.pisos.com'}[ad['fuente']]
    def verify(record, kind):
        name = record.get('archivo', '')
        path = Path(sources_dir) / name
        if not name or Path(name).name != name or path.is_symlink():
            raise ValueError('Ruta de original de scraping invalida')
        data = path.read_bytes()
        archived = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
        if not archived or any(record.get(key) != value for key, value in archived.items()):
            raise ValueError('Procedencia distinta del registro archivado')
        if (record.get('sha256') != hashlib.sha256(data).hexdigest() or record.get('bytes') != len(data)
                or record.get('http_status') != 200 or record.get('clase') != kind
                or record.get('tls_verificado') is not True or record.get('user_agent') != USER_AGENT):
            raise ValueError('Original de scraping no verificable')
        url = urlsplit(record['url'])
        if url.scheme != 'https' or url.netloc != host:
            raise ValueError('Dominio de la captura no corresponde al portal')
        return data
    verify(source, 'listado')
    robots = source.get('robots') or {}
    body = verify(robots, 'robots')
    if robots.get('url') != 'https://' + host + '/robots.txt':
        raise ValueError('URL de robots incorrecta')
    parser = RobotFileParser()
    parser.parse(body.decode('utf-8-sig', errors='replace').splitlines())
    if source.get('robots_permite') is not True or not parser.can_fetch(USER_AGENT, source['url']):
        raise ValueError('Los robots archivados no permiten esta captura')
