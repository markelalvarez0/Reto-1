"""Indicadores desde capturas observadas: contratos, unidades e idempotencia."""
from pathlib import Path
import mongomock
import pytest
from src.municipal_analysis import analyze

ROOT = Path(__file__).resolve().parents[1]


def test_official_analysis_is_idempotent_and_keeps_regional_salary():
    db = mongomock.MongoClient().analysis
    result = analyze(db, ROOT / 'data/capturas_oficiales')
    count = db.rentas_emal.count_documents({})
    repeated = analyze(db, ROOT / 'data/capturas_oficiales')
    assert count == 768 == db.rentas_emal.count_documents({})
    assert result == repeated
    assert len(result['comparativa_municipal']) >= 3
    for row in result['comparativa_municipal']:
        assert len(row['codigo_municipio']) == 5
        assert row['anio'] == 2024 and row['trimestre'] == 4
        assert row['salario_referencia_autonomico_eur'] == 1564
        assert row['esfuerzo_escenario_pct'] == pytest.approx(100 * row['renta_media_eur'] / 1564)
        assert row['diferencia_umbral_30_eur'] == pytest.approx(row['renta_media_eur'] - .3 * 1564)
    assert result['metadatos']['salario']['es_salario_municipal'] is False
    assert db.viviendas.count_documents({}) == 0  # No convertir estadísticas en anuncios.
    assert result['mapa_promociones']


def test_mismatched_salary_period_is_rejected():
    db = mongomock.MongoClient().analysis
    with pytest.raises(ValueError, match='mismo año'):
        analyze(db, ROOT / 'data/capturas_oficiales', year=2025)
    assert db.rentas_emal.count_documents({}) == 0
