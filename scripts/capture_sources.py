"""Captura fuentes publicas originales y su trazabilidad; no fabrica reemplazos."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

INDEX = 'https://opendata.euskadi.eus/estadistica/tablas-estadisticas-de-la-estadistica-del-mercado-de-alquiler-emal-2016-2020-hasta-el-2-trimestre-de-2020/webopd00-dataset/es/'
EMAL_2025 = 'https://opendata.euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL.-Barrios-Municipios.-2016-2025_es.xlsx'
SOURCES = {
    'visesa.json': 'https://apps.visesa.eus/ws/promocion/filtro',
    'etxebide.csv': 'https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv',
    'ine_2026.xlsx': 'https://www.ine.es/daco/daco42/codmun/26codmun.xlsx',
    'ovj_salario_2024.html': 'https://www.euskadi.eus/gobierno-vasco/-/noticia/2025/el-salario-neto-medio-juventud-asalariada-18-y-34-anos-2024-incluidas-pagas-extra-asciende-1-564-euros-mensuales-ligero-incremento-respecto-2023/',
}


def discover_emal(html, base=INDEX):
    """Selecciona enlaces publicados, no supone el nombre del ultimo fichero."""
    for link in BeautifulSoup(html, 'html.parser').find_all('a', href=True):
        url = urljoin(base, link['href'])
        name = urlparse(url).path.lower()
        if 'barrios' in name and 'municipios' in name and name.endswith('.xlsx') and urlparse(url).hostname == 'opendata.euskadi.eus':
            return url
    raise ValueError('No se encuentra enlace XLSX municipal EMAL en la fuente')


def capture(destination):
    root = Path(destination); root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers['User-Agent'] = 'IABD-Reto1/1.0 (academic public-data retrieval)'
    records = []
    def download(name, url):
        record = {'archivo': name, 'url_solicitada': url, 'fecha_utc': datetime.now(timezone.utc).isoformat()}
        try:
            response = session.get(url, timeout=60)
            record.update(http_status=response.status_code, url_final=response.url)
            response.raise_for_status()
            payload = response.content
            if not payload or len(payload) > 32_000_000:
                raise ValueError('Respuesta vacia o demasiado grande')
            if name.endswith('.xlsx') and not payload.startswith(b'PK'):
                raise ValueError('La respuesta no es un libro XLSX')
            if name.endswith('.json'):
                json.loads(payload)
            (root / name).write_bytes(payload)
            record.update(estado='descargado', bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
            return response
        except (requests.RequestException, ValueError) as error:
            record.update(estado='error', error=str(error))
            return None
        finally:
            records.append(record)
    page = download('emal_catalogo.html', INDEX)
    try:
        emal_url = discover_emal(page.text) if page is not None else EMAL_2025
    except ValueError:
        emal_url = EMAL_2025
    download('emal_municipios.xlsx', emal_url)
    for name, url in SOURCES.items():
        download(name, url)
    manifest = {'tipo': 'captura_publica_original', 'fuentes': records,
                'advertencia': 'Los errores se conservan. EMAL es estadistica agregada, no anuncios individuales.'}
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='data/capturas_oficiales')
    capture(parser.parse_args().output)
