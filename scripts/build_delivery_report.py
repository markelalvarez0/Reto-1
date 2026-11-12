"""Genera informe vigente desde artefactos verificados, sin ejecutar el modelo.

Markdown completo, PDF paginado e inventario de fuentes; sustituye el generador
histórico con métricas sintéticas. No modifica los originales ni entrega_ml/.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_project import audit


def build(output):
    """Lee informes sellados y figuras existentes; falla si su integridad cambia."""
    checks = audit()
    if not checks['ok']:
        raise ValueError('No se genera informe con integridad fallida: ' + json.dumps(checks))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    sources = []

    def read(relative):
        path = ROOT / relative
        sources.append(path)
        return path.read_text(encoding='utf-8')

    selected = json.loads(read('entrega_ml/models/selection.json'))
    sealed = json.loads(read('docs/TEST_FINAL_EMAL.json'))
    provenance = json.loads(read('entrega_ml/data/procedencia.json'))
    rows = list(csv.DictReader(read('entrega_ml/resultados/comparativa_mlflow.csv').splitlines()))
    eda = json.loads(read('entrega_ml/resultados/conclusiones_eda.json'))
    sections = [
        ('Reto 1 · Vivienda joven en Euskadi',
         'Informe técnico de la versión en desarrollo. Orientación basada en rentas municipales observadas; '
         'no concede ni deniega ayudas. La entrega integral sigue pendiente de los requisitos no acreditados.\n\n'
         'Usuario: servicios de orientación y jóvenes que comparan una referencia territorial con su presupuesto. '
         'Objetivo: automatizar referencias trazables, evitar confundir promociones con ofertas y explicar las reglas. '
         'El beneficio esperado es facilitar comparaciones; no se ha medido ahorro de tiempo ni impacto social.\n\n'
         'Arquitectura: capturas verificadas → preparación → HDFS raw/processed → Kafka → MongoDB → vistas. '
         'EMAL → división temporal → pipeline sklearn → modelo conservado → Streamlit → reglas → n8n → ficha local. '
         'Los modelos y estadísticas municipales tienen unidades diferentes de un anuncio individual.'),
        ('Datos y metodología',
         json.dumps(provenance, ensure_ascii=False, indent=2) + '\n\n'
         'Aprendizaje supervisado de regresión, IA débil especializada en una variable y un territorio. '
         'No razona sobre derechos administrativos ni representa expedientes individuales. '
         'Pipeline común: imputación, StandardScaler y OneHotEncoder dentro de cada fold temporal. '
         'Las entradas son año, trimestre, municipio/provincia y retardos observados. '
         'Galdakao se excluye por cambio territorial; los objetivos no publicados no se imputan. '
         'La evaluación es retrospectiva sobre una serie revisada.\n\n' + read('entrega_ml/resultados/diccionario.csv')),
        ('Comparación extraída de MLflow',
         'Modelo | MAE train | MAE val | RMSE val | R² val | segundos\n' + '\n'.join(
             f"{r['modelo']} | {float(r['train_mae']):.2f} | {float(r['val_mae']):.2f} | "
             f"{float(r['val_rmse']):.2f} | {float(r['val_r2']):.4f} | {float(r['tiempo_s']):.3f}" for r in rows) +
         f"\n\nGanador conservado: {selected['modelo']}. MAE de validación: {selected['mae_val']:.2f} EUR; "
         f"persistencia: {selected['baseline_persistencia_val']['mae']:.2f} EUR. La mejora es pequeña; "
         'no demuestra superioridad generalizable. No se reselecciona después de observar test. '
         'MAE mide error absoluto medio en euros; RMSE penaliza más los errores grandes. '
         'R² compara con la media, no es porcentaje de aciertos.\n\n'
         'El MLP usa sklearn (base y tres experimentos), no Keras. El enunciado pide MLP sin fijar biblioteca; '
         'los ejercicios adjuntos usan Sequential/Dense/Adam y se documentan como diferencia docente. '
         'SMOTE no corresponde a regresión; el experimento auxiliar clasifica subidas trimestrales observadas. '
         'SHAP utiliza validación y fondo de train, con interpretación no causal.'),
        ('Evaluación final conservada', json.dumps(sealed, ensure_ascii=False, indent=2) + '\n\n'
         'Esta generación solo lee el informe y la figura existentes. No importa joblib, no ejecuta inferencia '
         'sobre test ni ajusta hiperparámetros. Las reaperturas de la app reutilizan el informe sellado.'),
        ('Resultados municipales y límites', read('docs/ESTADO_ENTREGA.md')),
        ('Contratos BDA y evidencia', read('docs/BDA_ESTADO.md')),
        ('Muestra de anuncios y conclusiones', read('docs/RESULTADOS_ANUNCIOS.md')),
        ('Reglas y automatización local',
         'Prioridad descendente; primera regla aplicable. Seguridad: datos inválidos o fuera de cobertura → revisión. '
         'Después se revisan vigencia normativa, esfuerzo crítico, requisitos, documentación, alternativas, '
         'gastos de entrada y consulta informativa. Fallback: información general.\n\n'
         'Streamlit exige consentimiento y envía solo UUID, regla, decisión y referencia estimada. '
         'n8n separa ocho ramas de acción; el receptor local persiste una ficha por UUID. Repetir el mismo '
         'evento no duplica; reutilizar UUID con contenido diferente se rechaza. '
         'Solo se considera éxito con confirmación de persistencia. No se envían mensajes reales.\n\n'
         'Las reglas normativas deben contrastarse con la convocatoria aplicable; la referencia no es una '
         'resolución administrativa ni la renta media una oferta disponible.'),
        ('Reproducción y defensa', read('docs/DEFENSA.md')),
        ('Apéndice: agregaciones municipales completas',
         'Código canónico completo; no se recorta para ajustar a una página.\n\n' + read('src/municipal_analysis.py')),
        ('Apéndice: agregaciones de anuncios completas', read('src/database/aggregations.py')),
    ]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    markdown = '\n\n'.join('# ' + title + '\n\n' + body for title, body in sections)
    for name, caption in eda.items():
        if name.endswith('.png'):
            markdown += f'\n\n## {name}\n\n![{name}](../../../entrega_ml/resultados/{name})\n\n{caption}'
    (output / 'informe.md').write_text(markdown, encoding='utf-8')
    with PdfPages(output / 'informe.pdf') as pdf:
        page = 0

        def save(fig, title):
            nonlocal page
            page += 1
            fig.text(.07, .965, title, fontsize=14, weight='bold', va='top')
            fig.text(.07, .03, f'Reto 1 · Desarrollo · Fuentes verificadas · {page}', fontsize=8, color='#555555')
            pdf.savefig(fig)
            plt.close(fig)

        for title, body in sections:
            lines = []
            for line in body.splitlines():
                lines.extend(textwrap.wrap(line, width=92, replace_whitespace=False, break_long_words=True) or [''])
            for start in range(0, len(lines), 62):
                fig = plt.figure(figsize=(8.27, 11.69))
                fig.text(.07, .91, '\n'.join(lines[start:start+62]), family='DejaVu Sans Mono',
                         fontsize=8, va='top', linespacing=1.25, parse_math=False)
                save(fig, title + (' (continuación)' if start else ''))
        figures = [(ROOT / 'entrega_ml/resultados' / name, caption) for name, caption in eda.items() if name.endswith('.png')]
        figures += [(ROOT / 'entrega_ml/resultados' / name, caption) for name, caption in [
            ('shap_validacion.png', 'SHAP de validación; no causal, fondo de train.'),
            ('test_real_predicho.png', 'Figura conservada de la única evaluación final; no se recalcula.')]]
        figures += [(ROOT / 'docs/evidencias_ml/capturas' / name, 'Captura histórica conservada del bloque ML; no nueva ejecución.') for name in
                    ('mlflow-experimentos.png', 'streamlit-formulario.png', 'streamlit-modelos.png')]
        figures += [(ROOT / 'docs/evidencias_entrega_2026-11-12' / name, caption) for name, caption in [
            ('muestra_anuncios.png', '17 identidades de portal del 12 de noviembre; mezcla de modalidades y muestra de conveniencia.'),
            ('territorio.png', 'Captura de Chromium del visor con EMAL y la muestra archivada; no búsqueda en tiempo real.'),
            ('modelo.png', 'Aplicación abierta con el test conservado; no se reevalúa el holdout.')]]
        for path, caption in figures:
            sources.append(path)
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_axes((.05, .22, .9, .65))
            ax.imshow(plt.imread(path)); ax.axis('off')
            fig.text(.07, .16, textwrap.fill(caption, 90), fontsize=9, va='top')
            save(fig, path.name)
    manifest = [{'archivo': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
    (output / 'fuentes.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return output / 'informe.pdf'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/informe_entrega')
    args = parser.parse_args()
    print(build(args.output_dir))


if __name__ == '__main__':
    main()
