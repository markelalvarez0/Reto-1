"""Exporta comparación municipal desde originales verificados y MongoDB."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.database.mongo_client import MongoDBManager
from src.municipal_analysis import analyze


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot-dir', type=Path, default=ROOT / 'data/capturas_oficiales')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/analisis_municipal')
    parser.add_argument('--db-name', default='reto1_analisis_municipal')
    parser.add_argument('--quarter', type=int, choices=[1, 2, 3, 4], default=4)
    parser.add_argument('--simulate-db', action='store_true', help='Solo desarrollo: datos observados, base en memoria identificada')
    args = parser.parse_args(argv)
    manager = MongoDBManager(db_name=args.db_name, force_mock=args.simulate_db)
    try:
        result = analyze(manager.db, args.snapshot_dir, quarter=args.quarter)
        result['metadatos']['motor'] = 'mongomock' if manager.is_mock else 'MongoDB'
        args.output_dir.mkdir(parents=True, exist_ok=True)
        manifest = []
        for name, value in result.items():
            path = args.output_dir / (name + '.json')
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
            manifest.append({'archivo': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(json.dumps({'municipios': len(result['comparativa_municipal']), 'motor': result['metadatos']['motor'],
                          'periodo': '2024 T' + str(args.quarter), 'salidas': str(args.output_dir)}, ensure_ascii=False))
    finally:
        manager.close()


if __name__ == '__main__':
    main()
