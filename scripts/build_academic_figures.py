"""Dibuja figuras legibles desde CSV conservados; no importa ni ejecuta modelos."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs/entrega/assets'


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 18, 'axes.labelsize': 19, 'axes.titlesize': 22})
    rows = list(csv.DictReader((ROOT/'entrega_ml/data/train.csv').open()))
    previous = [r for r in rows if r['renta_lag1']]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.scatter([float(r['renta_lag1']) for r in previous],
               [float(r['renta_media_eur']) for r in previous], alpha=.5, color='#087e83')
    ax.set(xlabel='Renta del trimestre anterior (€/mes)', ylabel='Renta actual (€/mes)',
           title='Entrenamiento EMAL: persistencia temporal')
    fig.tight_layout(); fig.savefig(ASSETS/'persistencia_train.png', dpi=180); plt.close(fig)
    rows = list(csv.DictReader((ROOT/'entrega_ml/resultados/shap_validacion.csv').open()))[:5]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    labels = [r['variable'].replace('numericas__','').replace('categoricas__','') for r in rows]
    ax.barh(labels[::-1], [float(r['media_abs_shap_eur']) for r in rows][::-1], color='#087e83')
    ax.set(xlabel='Contribución absoluta media (euros)', title='SHAP: cinco variables principales en validación')
    fig.tight_layout(); fig.savefig(ASSETS/'shap_validacion_resumen.png', dpi=180); plt.close(fig)
    selection = json.loads((ROOT/'entrega_ml/models/selection.json').read_text())
    mae = [selection['baseline_persistencia_val']['mae'], selection['mae_val']]
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.barh(['Persistencia', 'MLP dos capas'], mae, color=['#9eb4bf','#087e83'])
    ax.set(xlabel='MAE de validación (euros)', xlim=(0,28), title='Misma validación de 2024: mejora pequeña')
    for y, value in enumerate(mae):
        ax.text(value+.2,y,f'{value:.2f} €'.replace('.',','), va='center',fontsize=19)
    fig.tight_layout(); fig.savefig(ASSETS/'baseline_validacion.png',dpi=180); plt.close(fig)
    print('Figuras generadas desde train y resultados de validación conservados. Sin modelo ni test.')


if __name__ == '__main__':
    main()
