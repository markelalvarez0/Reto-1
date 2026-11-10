import pytest
from scripts.capture_sources import discover_emal


def test_enlace_emal_publicado():
    html = '<a href="/datos/EMAL.-Barrios-Municipios.-2016-2026_es.xlsx">Datos</a>'
    assert discover_emal(html) == 'https://opendata.euskadi.eus/datos/EMAL.-Barrios-Municipios.-2016-2026_es.xlsx'


def test_enlace_ajeno_no_es_fuente_oficial():
    with pytest.raises(ValueError):
        discover_emal('<a href="https://example.com/Barrios-Municipios.xlsx">X</a>')


def test_sin_enlaces_no_inventa_url():
    with pytest.raises(ValueError):
        discover_emal('<html>Sin datos</html>')
