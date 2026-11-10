"""Version script del notebook 01_eda.ipynb, con datos EMAL observados."""
import os
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').exists())
sys.path.insert(0, str(ROOT))
from src.ml_data import read_emal, temporal_split
from src.ml_workflow import make_eda

def main():
    frame, metadata = read_emal(ROOT / 'data/capturas_oficiales')
    train, _, _ = temporal_split(frame)
    output = Path(os.getenv('RETO1_ARTIFACT_DIR', str(ROOT / 'entrega_ml')))
    make_eda(train, output / 'resultados')
    print(metadata)

if __name__ == '__main__':
    main()
