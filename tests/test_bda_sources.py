"""Regresiones BDA: originales, catalogo completo, procedencia y unidades."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import mongomock
import pandas as pd
import pytest

from src.database.aggregations import MongoHousingAggregations
from src.database.data_loader import MongoDBDataLoader
from src.extraction.api_client import OpenDataEuskadiHousingClient
from src.extraction.models import HousingAd
from src.extraction.source_snapshots import (MunicipalityCatalog, parse_etxebide_csv,
                                              parse_ovj_salary, prepare_snapshot, verify_snapshot)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def snapshot(tmp_path):
    """Captura docente local: nunca se publica como evidencia de mercado real."""
    root = tmp_path / 'originales'
    root.mkdir()
    sheets = {'01': [('01', '059', '0', 'Vitoria-Gasteiz')],
              '20': [('20', '069', '7', 'Donostia/San Sebastián')],
              '48': [('48', '020', '9', 'Bilbao'), ('48', '085', '0', 'Sopela'), ('48', '029', '5', 'Etxebarri')]}
    with pd.ExcelWriter(root / 'ine_2026.xlsx', engine='openpyxl') as writer:
        for name, rows in sheets.items():
            pd.DataFrame([['Catalogo de prueba', '', '', ''], ['Provincia', '', '', ''],
                          ['CPRO', 'CMUN', 'DC', 'NOMBRE'], *rows]).to_excel(writer, sheet_name=name, header=False, index=False)
    (root / 'visesa.json').write_text(json.dumps({'rows': [
        {'idContenido': 1, 'poblacion': 'Bilbao', 'idTipoVenta': 7},
        {'idContenido': 2, 'poblacion': 'Vitoria-Gasteiz', 'idTipoVenta': 7}]}), encoding='utf-8')
    (root / 'etxebide.csv').write_bytes(('ID_PROM;Cod_Prov;CODMUNI;Municipio;Territorio;Reg Acceso;Ubicacion\r\n'
        '1;48;085;SOPELANA;BIZKAIA;Alquiler;Promoción de prueba\r\n').encode('iso-8859-1'))
    (root / 'ovj_salario_2024.html').write_text('<p>El salario neto medio de entre 18 y 34 años en 2024, incluidas las pagas extraordinarias, asciende a 1.564 euros mensuales.</p>', encoding='utf-8')
    manifest = {'tipo': 'fixture_de_prueba', 'fuentes': [
        {'archivo': path.name, 'estado': 'descargado', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
         'fecha_utc': '2026-11-10T00:00:00+00:00', 'url_solicitada': 'https://example.invalid/fixture/' + path.name}
        for path in sorted(root.iterdir())]}
    (root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return root


def test_capturas_del_repositorio_conservan_bytes_originales():
    sources = verify_snapshot(ROOT / 'data/capturas_oficiales')
    assert {'visesa.json', 'etxebide.csv', 'ine_2026.xlsx', 'ovj_salario_2024.html'} <= sources.keys()


def test_original_alterado_no_se_acepta(snapshot):
    verify_snapshot(snapshot)
    path = snapshot / 'etxebide.csv'
    path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
    with pytest.raises(ValueError, match='Integridad'):
        verify_snapshot(snapshot)


def test_catalogo_lee_tres_hojas_sin_digito_de_control(snapshot):
    catalog = MunicipalityCatalog.from_snapshot(snapshot)
    assert len(catalog.records) == 5
    assert catalog.resolve('Vitoria-Gasteiz') == '01059'
    assert catalog.resolve('San Sebastian') == '20069'
    assert catalog.resolve('BILBAO') == '48020'
    assert catalog.resolve('Bil') is None
    assert catalog.resolve('Etxebarri') == '48029'


def test_alias_ambiguo_no_elige_un_municipio():
    catalog = MunicipalityCatalog([{'codigo_municipio': '01002', 'municipio': 'A/Compartido'},
                                   {'codigo_municipio': '48085', 'municipio': 'B/Compartido'}])
    assert catalog.resolve('Compartido') is None


def test_csv_latin1_conserva_codigo_fuente(snapshot):
    ads, errors = parse_etxebide_csv((snapshot / 'etxebide.csv').read_bytes())
    assert not errors and len(ads) == 1
    assert ads[0].codigo_municipio == '48085'
    assert ads[0].procedencia['codigo_fuente'] == '48085'
    assert ads[0].procedencia['encoding'] == 'iso-8859-1'
    assert ads[0].precio is None and ads[0].tipo_registro == 'promocion'


def test_contrato_csv_desconocido_falla_explicito():
    with pytest.raises(ValueError, match='Contrato Etxebide'):
        parse_etxebide_csv(b'id;ciudad\n1;Bilbao\n')


def test_api_admite_rows_y_no_inventa_resultados():
    client = OpenDataEuskadiHousingClient()
    result = client.parse_payload({'rows': [{'idContenido': 1, 'poblacion': 'Bilbao'}]}, {'sha256': 'prueba'})
    assert result.total_registros == 1
    assert result.items[0].procedencia['contrato'] == 'rows'
    assert result.items[0].tipo_registro == 'promocion'
    with pytest.raises(ValueError, match='Contrato Visesa'):
        client.parse_payload({'respuesta_nueva': []})


def test_precio_de_garaje_no_es_alquiler_de_promocion():
    result = OpenDataEuskadiHousingClient().parse_payload({'promociones': [
        {'id': 1, 'nombre_promocion': 'Promocion de prueba', 'municipio': 'Bilbao', 'modalidad': 'Alquiler',
         'viviendas': [{'unidad_venta': 'GARAJE', 'precio': 18000}]}]})
    assert result.total_registros == 1 and result.items[0].precio is None


def test_preparacion_no_inventa_salario_municipal_y_acepta_codigo_historico(snapshot, tmp_path):
    originals = {p.name: p.read_bytes() for p in snapshot.iterdir()}
    catalog, report = prepare_snapshot(snapshot, tmp_path / 'preparados')
    assert report['registros_aceptados'] == 3 and not report['rechazos']
    assert report['salario_ovj']['valor'] == 1564
    assert report['salario_ovj']['es_salario_municipal'] is False
    ads = json.loads((tmp_path / 'preparados/vivienda_oficial.json').read_text())
    historic = next(ad for ad in ads if ad['id'] == 'etxebide_1')
    assert historic['municipio'] == 'Sopela' and historic['codigo_municipio'] == '48085'
    assert historic['procedencia']['municipio_original'] == 'SOPELANA'
    municipalities = json.loads((tmp_path / 'preparados/municipios_oficiales.json').read_text())
    assert all(row['economia_laboral']['salario_medio_joven_mes'] is None for row in municipalities)
    assert all(row['contexto_autonomico']['salario_ovj']['territorio'] == 'Euskadi' for row in municipalities)
    assert {p.name: p.read_bytes() for p in snapshot.iterdir()} == originals
    with pytest.raises(ValueError, match='fuera de los originales'):
        prepare_snapshot(snapshot, snapshot / 'derivados')


def test_ovj_no_toma_cualquier_numero_del_html():
    with pytest.raises(ValueError, match='salario OVJ'):
        parse_ovj_salary(b'<p>En 2024 se anuncian 1.564 euros mensuales</p>', {})


def test_procedencia_y_tipo_sobreviven_modelo_loader_y_csv(snapshot, tmp_path):
    catalog, _ = prepare_snapshot(snapshot, tmp_path / 'preparados')
    ad = HousingAd(id='t', fuente='fixture', municipio='Etxebarri', codigo_municipio='48029',
                   tipo_operacion='alquiler', tipo_registro='promocion', lote_ingesta='lote1', es_sintetico=False,
                   procedencia={'archivo': 'original.csv', 'sha256': 'abc', 'fila': 2})
    decoded = HousingAd.model_validate_json(ad.model_dump_json())
    db = mongomock.MongoClient().db
    loader = MongoDBDataLoader(db, municipality_catalog=catalog)
    assert loader.cargar_anuncios([decoded.to_dict()]) == (1, 0)
    doc = db.viviendas.find_one()
    assert doc['procedencia'] == {**ad.procedencia, 'estado': 'observado'}
    assert 'estado' not in ad.procedencia  # La entrada original no se modifica.
    assert doc['tipo_registro'] == 'promocion' and doc['lote_ingesta'] == 'lote1'
    row = {**ad.to_dict(), 'procedencia': json.dumps(ad.procedencia), 'archivo_origen': 'normalizado.csv'}
    normalized = loader._normalizar_anuncio(row)
    assert normalized['procedencia']['archivo'] == 'original.csv'
    assert normalized['procedencia']['archivo_normalizado'] == 'normalizado.csv'
    assert loader._normalizar_anuncio({**row, 'procedencia': '[]'}) is None
    assert loader._normalizar_anuncio({**row, 'codigo_municipio': '48020'}) is None


def test_promocion_con_precio_no_contamina_estadistica_de_anuncios():
    db = mongomock.MongoClient().db
    loader = MongoDBDataLoader(db)
    base = {'fuente': 'fixture', 'municipio': 'Bilbao', 'tipo_operacion': 'alquiler', 'es_sintetico': False}
    loader.cargar_anuncios([{**base, 'id': 'anuncio', 'precio': 700},
                            {**base, 'id': 'promo', 'precio': 100, 'tipo_registro': 'promocion'}])
    results = MongoHousingAggregations(db).pipeline_1_estadisticas_alquiler_por_municipio()
    assert results[0]['total_anuncios'] == 1 and results[0]['precio_medio'] == 700


def test_consumidor_no_reprocesa_otro_lote_como_nuevo():
    from src.kafka.consumer import HousingKafkaConsumer
    from src.kafka.producer import HousingKafkaProducer
    from src.kafka.mock_broker import InMemoryKafkaBroker
    InMemoryKafkaBroker.reset()
    producer = HousingKafkaProducer(simulation_mode=True)
    for batch in ['anterior', 'actual']:
        producer.publish_ad(HousingAd(id=batch, fuente='fixture', municipio='Bilbao', tipo_operacion='alquiler', lote_ingesta=batch))
    consumer = HousingKafkaConsumer(simulation_mode=True)
    calls = []
    rows = consumer.consume_batch(1, 1, lambda ad, n: calls.append(ad.id), expected_batch_id='actual')
    assert [ad.id for ad in rows] == ['actual'] and calls == ['actual']


def test_entrada_bda_help_no_arranca_servicios():
    result = subprocess.run([sys.executable, str(ROOT / 'BDA + SBD/main.py'), '--help'],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert '--snapshot-dir' in result.stdout and '--prepare-only' in result.stdout


def test_captura_real_se_normaliza_con_cobertura_y_procedencia(tmp_path):
    root = ROOT / 'data/capturas_oficiales'
    catalog, report = prepare_snapshot(root, tmp_path / 'normalizados')
    assert report['visesa_leidas'] > 0 and report['etxebide_leidas'] > 0
    assert set(code[:2] for code in catalog.records) == {'01', '20', '48'}
    assert len(catalog.records) > len(set(__import__('src.extraction.models', fromlist=['INE_MUNICIPAL_CODES']).INE_MUNICIPAL_CODES.values()))
    rows = json.loads((tmp_path / 'normalizados/vivienda_oficial.json').read_text())
    counts = Counter(row['fuente'] for row in rows)
    assert counts['OpenDataEuskadi_Visesa'] > 0 and counts['OpenDataEuskadi_Etxebide_CSV'] > 0
    assert all(row['tipo_registro'] == 'promocion' and row['es_sintetico'] is False for row in rows)
    assert all(row['codigo_municipio'] in catalog.records for row in rows)
    assert all(row['procedencia']['sha256'] for row in rows)


def test_recarga_municipal_no_borra_valores_observados_con_nulos():
    """Actualizar el catalogo INE no elimina medidas de otra fuente."""
    db = mongomock.MongoClient().db
    loader = MongoDBDataLoader(db)
    initial = {'codigo_municipio': '48020', 'municipio': 'Bilbao', 'es_sintetico': False,
               'economia_laboral': {'salario_medio_joven_mes': 1700, 'paro_juvenil_pct': 12},
               'poblacion_total': 300000}
    assert loader.cargar_municipios([initial]) == (1, 0)
    catalog_update = {'codigo_municipio': '48020', 'municipio': 'Bilbao', 'es_sintetico': False,
                      'economia_laboral': {'salario_medio_joven_mes': None},
                      'poblacion_total': None, 'contexto_autonomico': {'salario_ovj': {'valor': 1564}}}
    assert loader.cargar_municipios([catalog_update]) == (1, 0)
    actual = db.municipios.find_one({'codigo_municipio': '48020'})
    assert actual['economia_laboral'] == initial['economia_laboral']
    assert actual['poblacion_total'] == 300000
    assert actual['contexto_autonomico']['salario_ovj']['valor'] == 1564
    assert loader.cargar_municipios([{'municipio': 'Vitoria-Gasteiz', 'codigo_municipio': '01059',
                                     'es_sintetico': False, 'economia_laboral': {'salario_medio_joven_mes': None}}]) == (1, 0)
    assert db.municipios.find_one({'codigo_municipio': '01059'})['economia_laboral']['salario_medio_joven_mes'] is None


def test_entrada_prepare_only_usa_captura_por_defecto_con_salida_personalizada(tmp_path):
    """Elegir carpeta de salida no obliga a repetir la captura por defecto."""
    destination = tmp_path / 'salida_personalizada'
    result = subprocess.run([sys.executable, str(ROOT / 'BDA + SBD/main.py'),
                             '--prepare-only', '--raw-dir', str(destination)],
                            capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['tipo'] == 'preparacion_capturas_reales'
    assert report['registros_aceptados'] > 0
    assert (destination / 'vivienda_oficial.json').is_file()
    assert (destination / 'municipios_oficiales.json').is_file()
    assert not (destination / 'hdfs_demo').exists()
