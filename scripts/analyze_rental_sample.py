"""Comprueba la muestra archivada contra HTML y MongoDB real, sin recapturar."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from src.extraction.scraping_http import verify_scraped_record
from src.extraction.scraper import HabitacliaScraper
from src.extraction.pisos_scraper import PisosComScraper
from src.database.mongo_client import MongoDBManager
from src.database.queries import MongoHousingQueries
from src.database.consistency import MongoConsistencyManager
from src.database.indexes import MongoIndexOptimizer


def analyze(capture_dir, pipeline_dir, db_name, output_dir):
    capture_dir, pipeline_dir, output_dir = map(Path, (capture_dir, pipeline_dir, output_dir))
    capture = json.loads((capture_dir / 'informe.json').read_text(encoding='utf-8'))
    transport = json.loads((pipeline_dir / 'manifest.json').read_text(encoding='utf-8'))
    if capture['estado'] != 'captura_interpretable' or set(transport['servicios'].values()) != {'real'}:
        raise ValueError('Se requieren captura completa y transporte real')
    ads = json.loads((capture_dir / 'vivienda_scraping.json').read_text(encoding='utf-8'))
    if not ads or len({(a['fuente'], a['id']) for a in ads}) != len(ads):
        raise ValueError('Muestra vacía o identidades duplicadas')
    if capture['registros_unicos'] != len(ads) or transport['por_tipo_registro'].get('anuncio') != len(ads):
        raise ValueError('Los recuentos de captura y transporte no corresponden a la muestra')
    # Volver a interpretar solo los bytes archivados, sin nuevas peticiones HTTP.
    parsed, sources = {}, []
    for a in ads:
        verify_scraped_record(a, capture_dir / 'sources')
        name = a['procedencia']['archivo']
        if name not in parsed:
            soup = BeautifulSoup((capture_dir / 'sources' / name).read_bytes(), 'html.parser')
            current = []
            if a['fuente'] == 'Habitaclia_Scraping':
                scraper = HabitacliaScraper()
                for i, card in enumerate(soup.select('article')):
                    current.append(scraper._extract_article_data(card, '', 'alquiler', i, a['procedencia']['url']))
            else:
                scraper = PisosComScraper()
                for i, card in enumerate(soup.select('div.ad-preview')):
                    current.append(scraper._extract_card_data(card, '', None, 'alquiler', i, a['procedencia']['url']))
            parsed[name] = [item for item in current if item is not None]
            sources.append({'archivo': name, 'tarjetas': len(current),
                            'sin_tipo_o_identidad_residencial': sum(x is None for x in current),
                            'sin_precio_o_municipio': sum(x is not None and (x.precio is None or not x.codigo_municipio) for x in current),
                            'seleccionados': sum(item['procedencia']['archivo'] == name for item in ads)})
        matches = [item for item in parsed[name] if item.id == a['id']]
        if not matches or any(any(item.to_dict()[k] != a[k] for k in
            ('url', 'precio', 'codigo_municipio', 'superficie_m2', 'habitaciones', 'banos')) for item in matches):
            raise ValueError('El anuncio no coincide con su HTML: ' + a['id'])
    manager = MongoDBManager(db_name=db_name, force_mock=False)
    try:
        db = manager.db
        for a in ads:
            stored = db.viviendas.find_one({'fuente': a['fuente'], 'id_origen': a['id']})
            if stored is None or any(stored[k] != a[k] for k in ('precio', 'codigo_municipio', 'tipo_registro')):
                raise ValueError('Anuncio ausente o alterado en MongoDB: ' + a['id'])
            if stored['procedencia']['sha256'] != a['procedencia']['sha256']:
                raise ValueError('Procedencia alterada')
            if stored['procedencia'].get('condiciones_publicadas') != a['procedencia'].get('condiciones_publicadas'):
                raise ValueError('Condiciones publicadas alteradas')
        counts_before = db.viviendas.count_documents({})
        from src.database.data_loader import MongoDBDataLoader
        loader = MongoDBDataLoader(db)
        for a in ads:
            # Reentrega de los mismos anuncios con el lote persistido, sin borrar datos.
            doc = db.viviendas.find_one({'fuente': a['fuente'], 'id_origen': a['id']})
            assert loader.cargar_anuncios([{**a, 'lote_ingesta': doc['lote_ingesta']}]) == (1, 0)
        counts_after = db.viviendas.count_documents({})
        if counts_before != counts_after:
            raise ValueError('La reentrega ha duplicado registros')
        query = MongoHousingQueries(db)
        queries = {
            'alquileres_bilbao': query.consulta_1_alquileres_en_municipio(),
            'precio_hasta_750': query.consulta_2_alquileres_asequibles_jovenes(),
            'bilbao_hasta_2000_y_55m2': query.consulta_3_condiciones_combinadas(precio_max=2000),
            'dos_habitaciones_y_ascensor': query.consulta_4_campos_anidados_confort(),
            'dos_habitaciones_publicadas': query.consulta_4_campos_anidados_confort(ascensor=None),
            'senal_temporal_en_array': query.consulta_6_condiciones_publicadas(),
            'programa_gaztelagun_publicado': query.consulta_5_municipios_programas_array(),
        }
        explain = MongoIndexOptimizer(db).comparar_rendimiento_consulta(precio_max=2000)
        # Copia aislada: las 100 operaciones son una demostración, no intereses de jóvenes.
        temporary = 'reto1_atomicidad_muestra_' + uuid.uuid4().hex
        target = manager.client[temporary]
        try:
            original = db.viviendas.find_one({'fuente': ads[0]['fuente'], 'id_origen': ads[0]['id']})
            original.pop('_id')
            original['solicitudes_interes_joven'] = 0
            target.viviendas.insert_one(original)
            consistency = MongoConsistencyManager(target)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: consistency.registrar_interes_joven_atomico(ads[0]['id'], ads[0]['fuente']), range(100)))
            count = target.viviendas.find_one({})['solicitudes_interes_joven']
            if count != 100 or not all(x['atomicidad_garantizada'] for x in results):
                raise ValueError('Falló la demostración atómica')
            atomic = {'datos': 'copia aislada de un anuncio observado; operaciones de prueba',
                      'operaciones': 100, 'contador_final': count, 'coleccion_original_modificada': False}
        finally:
            manager.client.drop_database(temporary)
        comparison = json.loads((pipeline_dir / 'estadisticas_por_municipio.json').read_text(encoding='utf-8'))
        report = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'motor': 'MongoDB',
                  'anuncios': len(ads), 'por_fuente': dict(Counter(a['fuente'] for a in ads)),
                  'por_municipio_ine': dict(Counter(a['codigo_municipio'] for a in ads)),
                  'condiciones_publicadas': dict(Counter(c for a in ads for c in a['procedencia'].get('condiciones_publicadas', []))),
                  'nulos': {k: sum(a[k] is None for a in ads) for k in ('precio', 'superficie_m2', 'habitaciones', 'banos', 'descripcion')},
                  'revision_html': sources, 'comparativa': comparison,
                  'reentrega': {'antes': counts_before, 'despues': counts_after, 'duplicados_nuevos': counts_after-counts_before},
                  'atomicidad': atomic, 'consultas': {k: len(v) for k, v in queries.items()},
                  'limites': [f'Muestra de conveniencia de {len(ads)} identidades de portal; no viviendas únicas.',
                              'Anuncios mensuales con modalidades mezcladas; no equivalen a contratos EMAL ni a vivienda habitual.',
                              'La ausencia de señales textuales no acredita disponibilidad o ausencia de restricciones.',
                              'No hay salarios municipales observados: esfuerzo y asequibilidad personal permanecen nulos.',
                              'Las consultas sin resultados son resultados válidos, no datos que haya que rellenar.']}
        output_dir.mkdir(parents=True, exist_ok=True)
        payloads = {'resumen.json': report, 'consultas.json': queries, 'explain.json': explain, 'anuncios.json': ads}
        for name, data in payloads.items():
            (output_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str, allow_nan=False), encoding='utf-8')
        paths = list(capture_dir.rglob('*')) + [pipeline_dir / name for name in
            ('manifest.json', 'estadisticas_por_municipio.json', 'indicadores_municipales.json', 'distribuciones.json', 'esfuerzo_por_vivienda.json')]
        manifest = {'fuentes': [{'archivo': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths if p.is_file()],
                    'resultados': [{'archivo': name, 'sha256': hashlib.sha256((output_dir / name).read_bytes()).hexdigest()} for name in payloads]}
        (output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        return report
    finally:
        manager.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-dir', type=Path, required=True)
    parser.add_argument('--pipeline-dir', type=Path, required=True)
    parser.add_argument('--db-name', required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/analisis_anuncios')
    args = parser.parse_args()
    print(json.dumps(analyze(args.capture_dir, args.pipeline_dir, args.db_name, args.output_dir), ensure_ascii=False, indent=2))
