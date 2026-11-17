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
           title='La renta anterior es una buena referencia')
    fig.tight_layout(); fig.savefig(ASSETS/'persistencia_train.png', dpi=180); plt.close(fig)
    rows = list(csv.DictReader((ROOT/'entrega_ml/resultados/shap_validacion.csv').open()))[:5]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    readable = {'renta_lag1': 'Renta del trimestre anterior',
                'renta_lag4': 'Renta de hace un año', 'anio': 'Año',
                'contratos_lag1': 'Contratos del trimestre anterior', 'trimestre': 'Trimestre',
                'provincia_Bizkaia': 'Municipio situado en Bizkaia'}
    labels = [r['variable'].replace('numericas__','').replace('categoricas__','') for r in rows]
    labels = [readable.get(label, label) for label in labels]
    ax.barh(labels[::-1], [float(r['media_abs_shap_eur']) for r in rows][::-1], color='#087e83')
    ax.set(xlabel='Contribución absoluta media (euros)', title='SHAP: cinco variables principales en validación')
    fig.tight_layout(); fig.savefig(ASSETS/'shap_validacion_resumen.png', dpi=180); plt.close(fig)
    selection = json.loads((ROOT/'entrega_ml/models/selection.json').read_text())
    mae = [selection['baseline_persistencia_val']['mae'], selection['mae_val']]
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.barh(['Usar renta anterior', 'MLP de dos capas'], mae, color=['#9eb4bf','#087e83'])
    ax.set(xlabel='Error absoluto medio en euros (menos es mejor)', xlim=(0,28), title='Comparación con los mismos datos de 2024')
    for y, value in enumerate(mae):
        ax.text(value+.2,y,f'{value:.2f} €'.replace('.',','), va='center',fontsize=19)
    fig.tight_layout(); fig.savefig(ASSETS/'baseline_validacion.png',dpi=180); plt.close(fig)
    comparison = json.loads((ROOT/'docs/evidencias_entrega_2026-11-12/municipal/comparativa_municipal.json').read_text())
    capitals = [next(r for r in comparison if r['codigo_municipio'] == code)
                for code in ['01059', '48020', '20069']]
    fig, ax = plt.subplots(figsize=(13.5, 4.5))
    labels = ['Vitoria-Gasteiz', 'Bilbao', 'Donostia']
    values = [r['esfuerzo_escenario_pct'] for r in capitals]
    ax.barh(labels[::-1], values[::-1], color=['#123e53', '#087e83', '#43aeb0'], height=.58)
    for y, r in enumerate(capitals[::-1]):
        value = r['esfuerzo_escenario_pct']
        amount = f"{r['renta_media_eur']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ax.text(value+1, y, f'{value:.2f} %'.replace('.', ','), va='center', fontsize=22, weight='bold')
        ax.text(2, y, amount+' €/mes', va='center', fontsize=19, color='white')
    ax.set(xlim=(0,100), xlabel='Parte del ingreso común que se destina al alquiler (%)',
           title='Mismo ingreso de referencia: 1.564 €/mes')
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout(); fig.savefig(ASSETS/'esfuerzo_capitales.png',dpi=180);plt.close(fig)
    print('Figuras desde train, validación y comparación municipal conservados. Sin modelo ni test.')


if __name__ == '__main__':
    main()
