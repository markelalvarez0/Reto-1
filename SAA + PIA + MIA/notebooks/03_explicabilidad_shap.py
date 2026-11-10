"""SHAP real del ganador sobre validacion, nunca sobre test."""
import json
import os
import sys
from pathlib import Path
import joblib
import pandas as pd
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').exists())
sys.path.insert(0, str(ROOT))
from src.ml_workflow import explain_validation, sha256

def main():
    output = Path(os.getenv('RETO1_ARTIFACT_DIR', str(ROOT / 'entrega_ml')))
    selection = json.loads((output / 'models/selection.json').read_text())
    path = output / 'models/best_model.joblib'
    if sha256(path) != selection['sha256_modelo']:
        raise ValueError('Huella de modelo inesperada')
    train = pd.read_csv(output / 'data/train.csv', dtype={'codigo_municipio': str})
    val = pd.read_csv(output / 'data/val.csv', dtype={'codigo_municipio': str})
    explain_validation(joblib.load(path), train, val, output / 'resultados')

if __name__ == '__main__':
    main()
