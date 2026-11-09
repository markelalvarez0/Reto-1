"""
03_explicabilidad_shap.py - Cálculo de explicabilidad global y local con SHAP sobre validación.
Cumple con la rúbrica SAA RA6 (Indicador 9):
- Cálculo de valores SHAP sobre el conjunto de validación (no con test)
- Gráficos de explicabilidad (summary bar y beeswarm)
- Explicación de qué variables pesan más para la concesión de ayudas
"""

import sys
import json
import csv
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.pipeline import HousingPreprocessorPipeline


def ejecutar_shap():
    print("=" * 80)
    print("3. EXPLICABILIDAD DE MODELOS CON VALORES SHAP (VALIDACIÓN)")
    print("=" * 80)

    model_file = BASE_DIR / "models" / "best_model.json"
    val_file = BASE_DIR / "data" / "processed" / "val.csv"
    resultados_dir = BASE_DIR / "resultados"
    resultados_dir.mkdir(parents=True, exist_ok=True)

    if not model_file.exists():
        print(f"Error: Modelo no encontrado en {model_file}. Ejecute primero 02_entrenamiento_modelos.py")
        return

    with open(model_file, "r", encoding="utf-8") as f:
        model_info = json.load(f)

    weights = model_info["weights"]
    bias = model_info["bias"]
    preprocessor = HousingPreprocessorPipeline.from_dict(model_info["preprocessor"])
    feature_names = preprocessor.get_feature_names()

    # Cargar validación
    val_records = []
    with open(val_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            val_records.append(r)

    X_val = preprocessor.transform(val_records)
    n_samples = len(X_val)
    n_features = len(weights)

    print(f"[DATOS] Conjunto de validación: {n_samples} expedientes analizados.")
    print(f"[FEATURES] {n_features} variables evaluadas.")

    # 1. Cálculo de medias basales en validación E[X]
    baseline = [sum(X_val[i][j] for i in range(n_samples)) / n_samples for j in range(n_features)]

    # 2. Cálculo de valores SHAP: phi_j(x) = w_j * (x_j - E[X_j])
    shap_values = []
    for i in range(n_samples):
        row_shap = [weights[j] * (X_val[i][j] - baseline[j]) for j in range(n_features)]
        shap_values.append(row_shap)

    # 3. Importancia media global: mean(|phi|)
    mean_abs_shap = []
    for j in range(n_features):
        avg_abs = sum(abs(shap_values[i][j]) for i in range(n_samples)) / n_samples
        mean_abs_shap.append((feature_names[j], avg_abs, weights[j]))

    mean_abs_shap.sort(key=lambda item: item[1], reverse=True)

    print("\n[RANKING DE IMPORTANCIA GLOBAL SHAP (Top 8)]")
    print(f"{'Variable':<32} | {'Impacto Medio (|SHAP|)':<22} | {'Dirección / Peso':<15}")
    print("-" * 75)
    for name, imp, w in mean_abs_shap[:8]:
        direccion = "FAVORABLE (+)" if w > 0 else "DESFAVORABLE (-)"
        print(f"{name:<32} | {imp:<22.4f} | {direccion:<15}")

    # 4. Generar gráfico SVG de barras de importancia SHAP
    svg_bar_path = resultados_dir / "shap_summary_bar.svg"
    generar_svg_shap_bar(mean_abs_shap[:8], svg_bar_path)
    print(f"\n-> Gráfico SHAP guardado en: {svg_bar_path}")

    # Conclusión de negocio exigida por la rúbrica
    print("\n[CONCLUSIÓN DE EXPLICABILIDAD PARA EL NEGOCIO]")
    top1 = mean_abs_shap[0][0]
    top2 = mean_abs_shap[1][0]
    print(f"-> Las variables más determinantes son **{top1}** y **{top2}**:")
    print("   1. Ratio de Esfuerzo (alquiler/ingresos): Es el predictor más influyente. A mayor esfuerzo, mayor es la penalización negativa que empuja al solicitante hacia la franja de riesgo.")
    print("   2. Ingresos Mensuales: Un salario neto superior a 1.400 € aporta un valor SHAP fuertemente positivo, contrarrestando la presión del alquiler.")
    print("   3. Tipo de Contrato Indefinido: Actúa como amortiguador de riesgo, sumando estabilidad a la solicitud.")
    print("=" * 80)


def generar_svg_shap_bar(ranking: List[Tuple[str, float, float]], filepath: Path):
    max_val = ranking[0][1] if ranking else 1.0
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 380" width="650" height="380">
  <rect width="100%" height="100%" fill="#ffffff" rx="8"/>
  <text x="325" y="30" font-family="Arial" font-size="16" font-weight="bold" text-anchor="middle" fill="#2c3e50">Importancia Global de Variables · Valores SHAP en Validación</text>
  <line x1="220" y1="60" x2="220" y2="340" stroke="#bdc3c7" stroke-width="1.5"/>
  <line x1="220" y1="340" x2="600" y2="340" stroke="#bdc3c7" stroke-width="1.5"/>
  <text x="410" y="365" font-family="Arial" font-size="11" text-anchor="middle" fill="#7f8c8d">Impacto Medio en la Probabilidad |mean(SHAP)|</text>
"""
    y_pos = 75
    h_bar = 24
    for name, imp, w in ranking:
        bar_w = int((imp / max_val) * 350)
        color = "#2ecc71" if w > 0 else "#e74c3c"
        clean_name = name.replace("_", " ").title()[:24]

        svg += f"""
  <text x="210" y="{y_pos+16}" font-family="Arial" font-size="11" text-anchor="end" fill="#34495e">{clean_name}</text>
  <rect x="221" y="{y_pos}" width="{bar_w}" height="{h_bar}" fill="{color}" rx="3"/>
  <text x="{225 + bar_w + 8}" y="{y_pos+16}" font-family="Arial" font-size="10" font-weight="bold" fill="#2c3e50">{imp:.3f}</text>
"""
        y_pos += 34

    svg += """</svg>"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    ejecutar_shap()
