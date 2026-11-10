"""Entrena los nueve experimentos oficiales sin evaluar el test reservado."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.ml_workflow import train_official


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=ROOT / "data/capturas_oficiales")
    parser.add_argument("--output", type=Path, default=ROOT / "entrega_ml")
    args = parser.parse_args()
    result = train_official(args.raw, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
