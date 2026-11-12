"""Fixtures explícitos: controles de acceso, originales y captura incompleta."""
import hashlib
import json
from unittest.mock import Mock
import pytest
import requests
from bs4 import BeautifulSoup
from src.extraction.scraping_http import ScrapingHTTP, euro_price, verify_scraped_record
from src.extraction.scraper import HabitacliaScraper
from src.extraction.pisos_scraper import PisosComScraper
from scripts.capture_rentals import capture
from src.indicators.udalmap_client import UdalmapClient


def response(data, status=200, content_type='text/plain', **headers):
    result = requests.Response()
    result.status_code, result._content = status, data
    result.headers.update({'Content-Type': content_type, **headers})
    return result


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr('src.extraction.scraping_http.time.sleep', lambda seconds: None)
    session = Mock(headers={})
    return ScrapingHTTP(session, 'portal.test', archive_dir=tmp_path)


@pytest.mark.parametrize('robots', [
    response(b'Forbidden', 403), response(b'not found', 404),
    response(b'<html>captcha</html>', content_type='text/html'),
    response(b'redirect', 302, Location='/robots2.txt'),
])
def test_unverifiable_robots_never_downloads_listings(client, robots):
    client.session.get.return_value = robots
    with pytest.raises(RuntimeError):
        client.get('https://portal.test/alquiler/')
    assert client.session.get.call_count == 1


def test_disallowed_listing_is_not_requested(client):
    client.session.get.return_value = response(b'User-agent: *\nDisallow: /alquiler/\n')
    with pytest.raises(PermissionError):
        client.get('https://portal.test/alquiler/')
    assert client.session.get.call_count == 1


def test_tls_failure_is_not_retried_without_verification(client):
    client.session.get.side_effect = requests.exceptions.SSLError('fixture certificado no confiable')
    with pytest.raises(requests.exceptions.SSLError):
        client.get('https://portal.test/alquiler/')
    assert client.session.get.call_count == 1
    assert client.session.get.call_args.kwargs['verify'] is True


def test_rate_limit_stops_further_requests(client):
    client.session.get.side_effect = [response(b'User-agent: *\nAllow: /\n'),
                                      response(b'fixture limit',429,**{'Retry-After':'120'})]
    with pytest.raises(requests.HTTPError):
        client.get('https://portal.test/alquiler/')
    with pytest.raises(RuntimeError, match='429'):
        client.get('https://portal.test/alquiler/otra-ciudad')
    assert client.session.get.call_count == 2


@pytest.mark.parametrize('destination', ['https://elsewhere.test/page', '/privado/listado'])
def test_redirect_rechecks_origin_and_robots(client, destination):
    client.session.get.side_effect = [
        response(b'User-agent: *\nDisallow: /privado\n'),
        response(b'redirect', 302, Location=destination),
    ]
    with pytest.raises((ValueError, PermissionError)):
        client.get('https://portal.test/alquiler/')
    assert client.session.get.call_count == 2


def test_archives_exact_bytes_and_attaches_robots_hash(client):
    raw = b'<html>fixture\r\n950 \xe2\x82\xac/mes</html>\r\n'
    client.session.get.side_effect = [response(b'User-agent: *\nCrawl-delay: 3\nAllow: /\n'),
                                      response(raw, content_type='text/html')]
    client.get('https://portal.test/alquiler/')
    meta = client.last_capture
    assert (client.archive_dir / meta['archivo']).read_bytes() == raw
    assert meta['sha256'] == hashlib.sha256(raw).hexdigest()
    assert meta['robots_permite'] and meta['demora_segundos'] >= 3
    assert meta['robots']['clase'] == 'robots'
    assert all(c.kwargs['verify'] is True and c.kwargs['allow_redirects'] is False
               for c in client.session.get.call_args_list)


@pytest.mark.parametrize('text,expected', [('1.250,50 €/mes',1250.5), ('950,50 €',950.5),
                                        ('1.250 €',1250), ('950.50 €',950.5),
                                        ('50 €/ día',None), ('100 €/semana',None), ('Consultar',None)])
def test_price_preserves_units_and_cents(text, expected):
    assert euro_price(text) == expected


@pytest.mark.parametrize('kind', ['habitaclia','pisos'])
def test_parser_keeps_observed_location_and_rejects_garage(kind):
    def parse(location, title='Piso en alquiler'):
        card = BeautifulSoup(f'<article data-id="123"><h2><a href="/piso-123.html">{title}</a></h2>'
                             f'<span class="price">1.250,50 €/mes</span><span class="location">{location}</span></article>', 'html.parser').article
        if kind == 'habitaclia':
            return HabitacliaScraper()._extract_article_data(card,'Bilbao','alquiler',0,'https://www.habitaclia.com/')
        return PisosComScraper()._extract_card_data(card,'Bilbao','Bizkaia','alquiler',0,'https://www.pisos.com/')
    ad = parse('Centro, Vitoria-Gasteiz')
    assert ad.codigo_municipio == '01059' and ad.precio == 1250.5
    assert parse('Ubicación desconocida').codigo_municipio is None
    assert parse('Centro, Bilbao', 'Garaje en alquiler') is None


def test_blocked_capture_has_no_ingestible_file(tmp_path, monkeypatch):
    def blocked(*args, **kwargs):
        raise requests.exceptions.ProxyError('fixture: CONNECT 403')
    monkeypatch.setattr(requests.Session, 'get', blocked)
    folder = tmp_path / 'failed'
    result = capture(folder)
    assert result['estado'] == 'incompleta' and result['registros_unicos'] == 0
    assert not (folder / 'vivienda_scraping.json').exists()
    assert all(r['errores'] for r in result['portales'].values())
    assert json.loads((folder / 'informe.json').read_text()) == result
    with pytest.raises(FileExistsError):
        capture(folder)


def test_udalmap_does_not_disable_tls_on_certificate_failure():
    client = UdalmapClient()
    client.session.get = Mock(side_effect=requests.exceptions.SSLError('fixture CA invalida'))
    with pytest.raises(requests.exceptions.SSLError):
        client._safe_get('https://api.euskadi.eus/fixture')
    assert client.session.get.call_count == 1
    assert client.session.get.call_args.kwargs['verify'] is True


def test_interpretable_capture_preserves_provenance_without_official_changes(tmp_path, monkeypatch):
    html = ('<article data-id="fixture-123"><h2><a href="/piso-123.html">Piso en alquiler</a></h2>'
            '<span class="price">1.250,50 €/mes</span><span class="location">Abando, Bilbao</span></article>').encode()
    def get(session, url, **kwargs):
        assert kwargs['verify'] is True
        if url.endswith('/robots.txt'):
            return response(b'User-agent: *\nAllow: /\n')
        return response(html, content_type='text/html')
    monkeypatch.setattr(requests.Session, 'get', get)
    monkeypatch.setattr('src.extraction.scraping_http.time.sleep', lambda seconds: None)
    folder = tmp_path / 'capture'
    result = capture(folder)
    assert result['estado'] == 'captura_interpretable'
    ads = json.loads((folder / 'vivienda_scraping.json').read_text())
    assert len(ads) == 2  # Un registro único por portal, aunque reaparezca en otro listado.
    for ad in ads:
        assert ad['codigo_municipio'] == '48020' and ad['precio'] == 1250.5
        source = ad['procedencia']
        assert (folder / 'sources' / source['archivo']).read_bytes() == html
        assert source['robots_permite']
        verify_scraped_record(ad, folder / 'sources')
    original = folder / 'sources' / ads[0]['procedencia']['archivo']
    original.write_bytes(html.replace(b'1.250,50', b'9.999,99'))
    with pytest.raises(ValueError, match='no verificable'):
        verify_scraped_record(ads[0], folder / 'sources')


@pytest.mark.parametrize('cls', [HabitacliaScraper, PisosComScraper])
def test_html_without_ads_is_not_a_success(cls, tmp_path, monkeypatch):
    scraper = cls(archive_dir=tmp_path)
    scraper.session.get = Mock(side_effect=[response(b'User-agent: *\nAllow: /\n'),
                                            response(b'<html>captcha</html>', content_type='text/html')])
    monkeypatch.setattr('src.extraction.scraping_http.time.sleep', lambda seconds: None)
    result = scraper.scrape_targets([cls.DEFAULT_TARGETS[0]])
    assert not result.items and result.errores


@pytest.mark.parametrize('location,code', [
    ('Lovaina (Vitoria - Gasteiz)', '01059'),
    ('Parte Vieja (San Sebastián - Donostia)', '20069'),
    ('Abando (Distrito Abando. Bilbao)', '48020'),
    ('Distrito Bilbao (Municipio desconocido)', None),
])
def test_current_published_location_format(location, code):
    from src.extraction.scraping_http import observed_municipality
    from src.extraction.models import resolver_codigo_ine
    assert resolver_codigo_ine(observed_municipality(location)) == code


def test_habitaclia_current_markup_uses_property_link_not_agency():
    card = BeautifulSoup('''<article><span class="text-display-4">1.250,50 €/mes</span>
        <a href="/inmobiliaria/fixture/">Agencia fixture</a>
        <h3><a href="/alquiler/viviendas/fixture-id/d">Piso con ascensor</a></h3>
        <p><span class="truncate">Centro, Bilbao</span></p>
        <div aria-label="Características del anuncio">72 m² 2 hab. 1 baño</div></article>''', 'html.parser').article
    ad = HabitacliaScraper()._extract_article_data(card, 'Vitoria', 'alquiler', 0, 'https://www.habitaclia.com/listado')
    assert ad.url.endswith('/alquiler/viviendas/fixture-id/d')
    assert ad.codigo_municipio == '48020' and ad.precio == 1250.5
    assert ad.superficie_m2 == 72 and ad.habitaciones == 2
    assert ad.descripcion is None  # La ubicación no es una descripción.


def test_pisos_current_markup_selects_whole_card_and_retains_conditions(tmp_path, monkeypatch):
    # Fixture estructural explícito, no un anuncio real ni una captura del portal.
    html = '''<div class="ad-preview" id="fixture-1">
        <div class="ad-preview__top"><a href="/foto/">Foto</a></div>
        <div class="ad-preview__info"><div class="ad-preview__price"><span>950 €</span><span>/mes</span></div>
        <a class="ad-preview__title" href="/alquilar/fixture-1/">Piso en Centro</a>
        <p class="ad-preview__subtitle">Centro (San Sebastián - Donostia)</p>
        <div class="ad-preview__description">Alquiler temporal para estudiantes. 60 m² 2 habs.</div></div></div>'''.encode()
    scraper = PisosComScraper(archive_dir=tmp_path)
    scraper.session.get = Mock(side_effect=[response(b'User-agent: *\nAllow: /\n'), response(html, content_type='text/html')])
    monkeypatch.setattr('src.extraction.scraping_http.time.sleep', lambda seconds: None)
    ads = scraper._scrape_page('https://www.pisos.com/alquiler/fixture/', 'Bilbao', 'Bizkaia', 'alquiler', 3)
    assert len(ads) == 1  # Nunca un anuncio por cada subelemento __info / __price.
    ad = ads[0]
    assert ad.codigo_municipio == '20069' and ad.provincia == 'Gipuzkoa'
    assert ad.url == 'https://www.pisos.com/alquilar/fixture-1/'
    assert ad.precio == 950 and ad.superficie_m2 == 60
    assert ad.procedencia['condiciones_publicadas'] == ['temporal', 'estudiantes']
    verify_scraped_record(ad.to_dict(), tmp_path)
