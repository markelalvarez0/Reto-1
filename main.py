#!/usr/bin/env python3
"""
main.py - Orquestador y Portal Multiasignatura del Repositorio.

Permite ejecutar los retos interdisciplinares y las 5 asignaturas:
  python main.py                        -> Menú interactivo multiasignatura.
  python main.py --subject bda_sbd      -> Ejecuta el Pipeline y Dashboard de BDA + SBD.
  python main.py --subject saa_pia_mia  -> Ejecuta el Pipeline de ML y Dashboard de SAA + PIA + MIA.
  python main.py --pdf                  -> Genera el PDF técnico de entrega (Entrega_Reto1_IABD_Documentacion.pdf).
  python main.py --test                 -> Ejecuta la suite completa de 29 pruebas con pytest.
"""

import os
import sys
import argparse
import subprocess

# Configurar salida segura en UTF-8 en Windows
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BDA_SBD_DIR = os.path.join(ROOT_DIR, "BDA + SBD")
SAA_PIA_MIA_DIR = os.path.join(ROOT_DIR, "SAA + PIA + MIA")

for p in [BDA_SBD_DIR, SAA_PIA_MIA_DIR, ROOT_DIR]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)


def print_banner():
    print("=" * 80)
    print("  REPOSITORIO ACADÉMICO MULTIDISCIPLINAR - CURSO DE IA Y BIG DATA (2026-27)")
    print("=" * 80)
    print("  Módulos y Asignaturas Disponibles:")
    print("    [1] BDA + SBD     : Reto ¿Dónde pueden vivir los jóvenes en Euskadi?")
    print("                        (API, Scraping, HDFS, Kafka, MongoDB y Dashboard Leaflet)")
    print("    [2] SAA + PIA + MIA : Reto De la Predicción a la Acción: Vivienda y Emancipación")
    print("                        (EDA, 5 Modelos ML, MLP, SMOTE, MLflow, SHAP, 6 Reglas y Streamlit)")
    print("    [3] Generar PDF   : Compila 'Entrega_Reto1_IABD_Documentacion.pdf'")
    print("    [4] Tests Unitarios: Ejecuta las 29 pruebas automatizadas con pytest")
    print("=" * 80 + "\n")


def run_bda_sbd(args_list=None):
    """Ejecuta el orquestador de BDA + SBD."""
    script = os.path.join(BDA_SBD_DIR, "main.py")
    cmd = [sys.executable, script] + (args_list or [])
    return subprocess.call(cmd, cwd=BDA_SBD_DIR)


def run_saa_pia_mia():
    """Ejecuta el pipeline de ML y abre la aplicación Streamlit de SAA + PIA + MIA."""
    print("[SAA + PIA + MIA] Ejecutando análisis exploratorio y entrenamiento de modelos...")
    eda_script = os.path.join(SAA_PIA_MIA_DIR, "notebooks", "01_eda.py")
    train_script = os.path.join(SAA_PIA_MIA_DIR, "notebooks", "02_entrenamiento_modelos.py")
    shap_script = os.path.join(SAA_PIA_MIA_DIR, "notebooks", "03_explicabilidad_shap.py")
    
    subprocess.call([sys.executable, eda_script], cwd=SAA_PIA_MIA_DIR)
    subprocess.call([sys.executable, train_script], cwd=SAA_PIA_MIA_DIR)
    subprocess.call([sys.executable, shap_script], cwd=SAA_PIA_MIA_DIR)
    
    print("\n[SAA + PIA + MIA] Abriendo aplicación interactiva...")
    app_script = os.path.join(SAA_PIA_MIA_DIR, "app", "streamlit_app.py")
    return subprocess.call([sys.executable, app_script], cwd=SAA_PIA_MIA_DIR)


def generate_pdf():
    """Genera el informe de entrega en PDF."""
    pdf_script = os.path.join(ROOT_DIR, "scripts", "generate_delivery_pdf.py")
    return subprocess.call([sys.executable, pdf_script], cwd=ROOT_DIR)


def run_all_tests():
    """Ejecuta los tests de BDA + SBD y SAA + PIA + MIA."""
    import pytest
    print("\n>>> Ejecutando pruebas unitarias de BDA + SBD...")
    code1 = pytest.main(["BDA + SBD/tests", "-v"])
    print("\n>>> Ejecutando pruebas unitarias de SAA + PIA + MIA...")
    code2 = pytest.main(["tests/test_ml_pipeline.py", "-v"])
    return code1 or code2


def main():
    parser = argparse.ArgumentParser(
        description="Portal de Ejecución Multiasignatura - IA y Big Data"
    )
    parser.add_argument(
        "--subject",
        choices=["bda_sbd", "saa_pia_mia", "bda", "sbd", "saa", "pia", "mia", "ainhoa"],
        help="Asignatura o reto intermodular a ejecutar."
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Genera el PDF con toda la documentación y explicaciones de implementación."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Ejecuta la suite de pruebas completa con pytest (29 tests)."
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Ejecuta el pipeline de datos en BDA + SBD."
    )
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Abre el dashboard interactivo de BDA + SBD o SAA + PIA + MIA."
    )

    args, unknown = parser.parse_known_args()

    if args.pdf:
        generate_pdf()
        return

    if args.test:
        sys.exit(run_all_tests())

    if args.subject in ["bda_sbd", "bda", "sbd", "ainhoa"]:
        passthrough = []
        if args.pipeline:
            passthrough.append("--pipeline")
        if args.visual:
            passthrough.append("--visual")
        passthrough.extend(unknown)
        sys.exit(run_bda_sbd(passthrough))

    if args.subject in ["saa_pia_mia", "saa", "pia", "mia"]:
        sys.exit(run_saa_pia_mia())

    # Si no se pasan argumentos, mostrar banner y opciones interactivas
    print_banner()
    print("Opciones de ejecución rápida:")
    print("  1) python main.py --subject bda_sbd --pipeline   (Ejecutar Pipeline BDA + SBD)")
    print("  2) python main.py --subject bda_sbd --visual     (Abrir Dashboard Cartográfico Leaflet)")
    print("  3) python main.py --subject saa_pia_mia          (Entrenar Modelos y Dashboard Streamlit)")
    print("  4) python main.py --pdf                          (Generar PDF de Entrega)")
    print("  5) python main.py --test                         (Ejecutar los 29 Tests Unitarios)")
    print("\nPara ejecutar todo de inmediato, elija una de las opciones anteriores.")


if __name__ == "__main__":
    main()
