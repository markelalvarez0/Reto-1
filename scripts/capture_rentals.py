"""Captura acotada de listados con robots, TLS y originales; sin datos de relleno.

Salida 0 solo si los dos portales solicitados aportan anuncios interpretables.
La captura parcial se conserva con estado explícito y salida 2; no es entrega
completa ni autorización para ignorar condiciones de uso de los portales.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extraction.scraper import HabitacliaScraper
from src.extraction.pisos_scraper import PisosComScraper


def capture(output, portal='ambos', limit=10):
    if not 1 <= limit <= 20:
        raise ValueError('Limite entre 1 y 20 anuncios por listado')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    classes = {'habitaclia': HabitacliaScraper, 'pisos': PisosComScraper}
    selected = classes if portal == 'ambos' else {portal: classes[portal]}
    reports, ads, seen = {}, [], set()
    for name, cls in selected.items():
        scraper = cls(archive_dir=output / 'sources')
        targets = [t for t in scraper.DEFAULT_TARGETS if t['tipo'] == 'alquiler']
        result = scraper.scrape_targets(targets, max_items_per_target=limit)
        reports[name] = {'registros': result.total_registros, 'errores': result.errores,
                         'listados_solicitados': [t['url'] for t in targets]}
        for item in result.items:
            key = item.fuente, item.id
            if key not in seen:
                ads.append(item.to_dict()); seen.add(key)
    complete = all(r['registros'] > 0 and not r['errores'] for r in reports.values())
    report = {'fecha_utc': datetime.now(timezone.utc).isoformat(),
              'estado': 'captura_interpretable' if complete else 'incompleta',
              'portales': reports, 'registros_unicos': len(ads),
              'limites': ['Muestra de listados, no censo ni garantía de disponibilidad.',
                          'Las condiciones temporal/estudiantes/empresas son señales textuales; su ausencia no acredita vivienda habitual.',
                          'Revisar condiciones de uso antes de ejecutar; robots no equivale a licencia.',
                          'No modifica fuentes oficiales ni el modelo o su test.']}
    def write(name, data):
        (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    write('informe.json', report)
    # Una captura fallida no deja un fichero listo para ingerir con cero registros.
    if complete:
        write('vivienda_scraping.json', ads)
    elif ads:
        write('candidatos_parciales.json', ads)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portal', choices=['ambos', 'habitaclia', 'pisos'], default='ambos')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/scraping' / ('captura_' + uuid.uuid4().hex))
    parser.add_argument('--max-items', type=int, choices=range(1, 21), default=10)
    args = parser.parse_args(argv)
    result = capture(args.output_dir, args.portal, args.max_items)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['estado'] == 'captura_interpretable' else 2


if __name__ == '__main__':
    raise SystemExit(main())
