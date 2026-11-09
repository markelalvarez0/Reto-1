"""
tests/test_multi_portal_extraction.py
Pruebas unitarias para la integración de nuevas fuentes de vivienda en Euskadi:
- Portales inmobiliarios (EnAlquiler, Chomon, Quorum, YaEncontre, Milanuncios)
- Fuentes Oficiales (Bizilagun contratos reales, Etxebide demanda, MIVAU precios referencia)
- Conectividad de transporte (CTB Metro, Euskotren, TUVISA, Dbus)
- Código INE municipal de 5 dígitos (codigo_municipio) y modelo unificado HousingAd
"""

import pytest
from src.extraction.models import HousingAd, resolver_codigo_ine, INE_MUNICIPAL_CODES
from src.extraction.multi_portal_scraper import MultiPortalHousingScraper
from src.extraction.official_housing_sources import OfficialHousingClient
from src.indicators.transport_client import TransportConnectivityClient


def test_resolver_codigo_ine():
    """Valida la resolución exacta de códigos INE de 5 dígitos para municipios vascos."""
    assert resolver_codigo_ine("Bilbao") == "48020"
    assert resolver_codigo_ine("Donostia-San Sebastián") == "20069"
    assert resolver_codigo_ine("San Sebastián") == "20069"
    assert resolver_codigo_ine("Vitoria-Gasteiz") == "01059"
    assert resolver_codigo_ine("Vitoria") == "01059"
    assert resolver_codigo_ine("Barakaldo") == "48013"
    assert resolver_codigo_ine("Getxo") == "48044"
    assert resolver_codigo_ine("Zarautz") == "20079"
    assert resolver_codigo_ine("Durango") == "48027"
    assert resolver_codigo_ine("Irun") == "20045"
    assert resolver_codigo_ine("MunicipioDesconocido") is None
    assert resolver_codigo_ine("") is None
    assert resolver_codigo_ine("Bil") is None  # No aceptar coincidencias parciales
    assert resolver_codigo_ine("  IRÚN ") == "20045"
    assert resolver_codigo_ine("Donostia / San Sebastian") == "20069"
    for nombre, codigo in INE_MUNICIPAL_CODES.items():
        assert resolver_codigo_ine(nombre) == codigo


def test_housing_ad_no_inventa_codigo_ine():
    """Un municipio desconocido queda sin asignar; no se convierte en Bilbao."""
    ad = HousingAd(id="desconocido", fuente="prueba", tipo_operacion="alquiler", municipio="MunicipioDesconocido")
    assert ad.codigo_municipio is None

    with pytest.raises(ValueError, match="incompatible"):
        HousingAd(id="mal-codigo", fuente="prueba", tipo_operacion="alquiler", municipio="Getxo", codigo_municipio="48020")

    with pytest.raises(ValueError, match="cinco dígitos"):
        HousingAd(id="codigo-corto", fuente="prueba", tipo_operacion="alquiler", municipio="Getxo", codigo_municipio="48")


def test_loader_descarta_ine_desconocido_y_lee_aliases():
    """La carga rechaza municipio incierto y respeta mun/cod de promociones VPO."""
    from src.database.data_loader import MongoDBDataLoader

    loader = MongoDBDataLoader.__new__(MongoDBDataLoader)
    assert loader._normalizar_anuncio({"id": "uno", "municipio": "MunicipioDesconocido", "precio": 650}) is None
    assert loader._normalizar_anuncio({"id": "dos", "municipio": "Getxo", "codigo_municipio": "48020", "precio": 650}) is None
    vpo = loader._normalizar_anuncio({"id": "tres", "mun": "Vitoria-Gasteiz", "cod": "01059", "precio": 380, "m2": 75})
    assert vpo["municipio"] == "Vitoria-Gasteiz"
    assert vpo["codigo_municipio"] == "01059"
    assert vpo["provincia"] == "Araba"
    assert vpo["superficie_m2"] == 75.0


def test_catalogo_vpo_mantiene_municipio_y_superficie(monkeypatch):
    """Las promociones de VPO no se convierten en anuncios de Bilbao de 65 m²."""
    from types import SimpleNamespace
    import src.database.data_loader as modulo_carga

    class ScraperVacio:
        def extraer_todos_los_portales(self):
            return SimpleNamespace(items=[])

    monkeypatch.setattr(modulo_carga, "MultiPortalHousingScraper", ScraperVacio)
    loader = modulo_carga.MongoDBDataLoader.__new__(modulo_carga.MongoDBDataLoader)
    anuncios = loader._generar_catalogo_multiportal_completo()
    por_id = {ad["id_origen"]: ad for ad in anuncios}
    assert por_id["vpo_vitoria_01"]["codigo_municipio"] == "01059"
    assert por_id["vpo_vitoria_01"]["municipio"] == "Vitoria-Gasteiz"
    assert por_id["vpo_vitoria_01"]["superficie_m2"] == 75.0
    assert por_id["vpo_donostia_01"]["codigo_municipio"] == "20069"
    assert por_id["vpo_irun_01"]["codigo_municipio"] == "20045"


def test_multi_portal_housing_scraper():
    """Verifica que el scraper multiportal consolide anuncios con código INE y características reales."""
    scraper = MultiPortalHousingScraper(timeout=2)
    resultado = scraper.extraer_todos_los_portales()

    assert resultado.total_registros >= 20
    assert len(resultado.items) >= 20

    portales_encontrados = {ad.portal_origen for ad in resultado.items if ad.portal_origen}
    assert "EnAlquiler" in portales_encontrados
    assert "Inmobiliaria_Chomon" in portales_encontrados
    assert "Inmobiliaria_Quorum" in portales_encontrados
    assert "YaEncontre" in portales_encontrados
    assert "Milanuncios" in portales_encontrados

    for ad in resultado.items:
        assert ad.codigo_municipio in INE_MUNICIPAL_CODES.values()
        assert ad.precio > 0
        assert ad.superficie_m2 > 0
        assert ad.tipo_operacion == "alquiler"
        assert ad.fianza_meses is not None
        assert ad.distancia_transporte_m is not None


def test_official_housing_sources_client():
    """Verifica la extracción de registros oficiales Bizilagun, Etxebide y MIVAU."""
    client = OfficialHousingClient()

    # 1. Bizilagun
    bizilagun = client.obtener_contratos_bizilagun()
    assert len(bizilagun) >= 10
    bilbao_biz = next(b for b in bizilagun if b.municipio == "Bilbao")
    assert bilbao_biz.codigo_municipio == "48020"
    assert bilbao_biz.num_contratos_depositados > 0
    assert bilbao_biz.cuantia_media_fianza_eur > 0

    # 2. Etxebide
    etxebide = client.obtener_demanda_etxebide()
    assert len(etxebide) >= 10
    vitoria_etx = next(e for e in etxebide if e.municipio == "Vitoria-Gasteiz")
    assert vitoria_etx.codigo_municipio == "01059"
    assert vitoria_etx.solicitudes_jovenes_alquiler > 0

    # 3. MIVAU
    mivau = client.obtener_precios_mivau()
    assert len(mivau) >= 10
    donostia_mivau = next(m for m in mivau if m.municipio == "Donostia-San Sebastián")
    assert donostia_mivau.codigo_municipio == "20069"
    assert donostia_mivau.precio_referencia_max_m2 > donostia_mivau.precio_referencia_min_m2


def test_transport_connectivity_client():
    """Verifica el cálculo de conectividad de transporte urbano e interurbano por municipio."""
    client = TransportConnectivityClient()
    transporte = client.obtener_conectividad_todos()

    assert len(transporte) >= 10
    bilbao_tr = next(t for t in transporte if t.municipio == "Bilbao")
    assert bilbao_tr.codigo_municipio == "48020"
    assert bilbao_tr.indice_conectividad >= 8.5
    assert bilbao_tr.red_metro is True
    assert bilbao_tr.red_tranvia is True

    donostia_tr = next(t for t in transporte if t.municipio == "Donostia-San Sebastián")
    assert donostia_tr.red_cercanias_euskotren is True
    assert donostia_tr.indice_conectividad >= 8.0
