"""Version script del notebook: cinco modelos oficiales y cuatro MLP, sin test."""
import os
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').exists())
sys.path.insert(0, str(ROOT))
from src.ml_workflow import train_official

def main():
    output = Path(os.getenv('RETO1_ARTIFACT_DIR', str(ROOT / 'entrega_ml')))
    print(train_official(ROOT / 'data/capturas_oficiales', output))

if __name__ == '__main__':
    main()
