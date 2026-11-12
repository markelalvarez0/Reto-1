"""Streamlit: modelo completo, test sellado, reglas explicables y n8n real."""
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists())
sys.path.insert(0, str(ROOT))
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from src.ml_data import FEATURES
from src.ml_workflow import evaluate_test_once, sha256
from src.reglas import MotorReglasVivienda
from src.n8n import N8NWebhookClient

st.set_page_config(page_title="Vivienda joven Euskadi", layout="wide")
st.title("Vivienda joven en Euskadi")
st.caption("Rentas municipales observadas, prediccion y orientacion. No concede ni deniega ayudas publicas.")
OUT = Path(os.getenv("RETO1_ARTIFACT_DIR", str(ROOT / "entrega_ml"))).resolve()
selection_path = OUT / "models/selection.json"
if not selection_path.exists():
    st.warning("Todavia no hay un modelo entrenado. Ejecutar scripts/capture_sources.py y scripts/train_official.py. No se muestran metricas ficticias.")
    st.stop()
selection = json.loads(selection_path.read_text(encoding="utf-8"))
if sha256(OUT / "models/best_model.joblib") != selection["sha256_modelo"]:
    st.error("La huella del modelo no coincide con la seleccion validada.")
    st.stop()
model = joblib.load(OUT / "models/best_model.joblib")
metadata = json.loads((OUT / "data/procedencia.json").read_text(encoding="utf-8"))
st.info("Se estima la renta media de un municipio y trimestre, no el precio exacto de un piso ni el riesgo individual.")
results_tab, test_tab, case_tab = st.tabs(["Modelos y datos", "Test reservado", "Nuevo caso y accion"])

with results_tab:
    st.subheader("Comparativa de MLflow: entrenamiento y validacion")
    st.dataframe(pd.read_csv(OUT / "resultados/comparativa_mlflow.csv"), hide_index=True)
    st.write("Modelo elegido:", selection["modelo"], "Criterio:", selection["criterio"])
    st.write("Persistencia: baseline calculado donde existe renta previa:", selection["baseline_persistencia_val"])
    st.json(metadata)
    st.image(str(OUT / "resultados/shap_validacion.png"), caption="SHAP en validacion, con fondo de train; no causal.")
    with st.expander("EDA y nulos"):
        notes = json.loads((OUT / "resultados/conclusiones_eda.json").read_text(encoding="utf-8"))
        for name, note in notes.items():
            if name.endswith(".png"):
                st.image(str(OUT / "resultados" / name), caption=note)
            else:
                st.write(note)
    with st.expander("Experimento auxiliar: con y sin SMOTE"):
        st.json(json.loads((OUT / "resultados/comparacion_smote.json").read_text(encoding="utf-8")))

with test_tab:
    st.subheader("Test del modelo previamente seleccionado")
    st.write("No se usa para elegir el modelo, ajustar imputacion ni SHAP. Se evalua una vez y se conserva el informe.")
    report_path = OUT / "resultados/test_final.json"
    if report_path.exists():
        report = evaluate_test_once(OUT)
        st.success("Informe conservado: no se vuelve a ejecutar el modelo con test.")
        st.json(report)
        st.image(str(OUT / "resultados/test_real_predicho.png"))
    elif st.button("Evaluar test reservado una sola vez", key="evaluate_holdout"):
        try:
            st.json(evaluate_test_once(OUT))
            st.success("Test evaluado y sellado.")
            st.image(str(OUT / "resultados/test_real_predicho.png"))
        except (ValueError, RuntimeError, OSError) as exc:
            st.error(str(exc))

with case_tab:
    history = pd.concat([pd.read_csv(OUT / f"data/{name}.csv", dtype={"codigo_municipio": str}) for name in ("train", "val")])
    if (OUT / "resultados/test_final.json").exists():
        history = pd.concat([history, pd.read_csv(OUT / "data/test.csv", dtype={"codigo_municipio": str})])
    names = history.drop_duplicates("codigo_municipio").set_index("codigo_municipio")["municipio"].to_dict()
    code = st.selectbox("Municipio cubierto por EMAL", selection["municipios"], format_func=lambda value: names.get(value, value))
    period = int(history.periodo.max()) + 1
    local = history.loc[history.codigo_municipio.eq(code)].set_index("periodo")
    def previous(column, lag):
        key = period - lag
        return float(local.loc[key, column]) if key in local.index and pd.notna(local.loc[key, column]) else np.nan
    features = {"codigo_municipio": code, "provincia": {"01": "Araba", "20": "Gipuzkoa", "48": "Bizkaia"}[code[:2]],
                "anio": period // 4, "trimestre": period % 4 + 1,
                "renta_lag1": previous("renta_media_eur", 1), "renta_lag4": previous("renta_media_eur", 4),
                "contratos_lag1": previous("numero_contratos", 1)}
    st.write(f"Referencia que se predice: {features['anio']} T{features['trimestre']}. No es una tasacion individual.")
    st.caption("El salario neto mensual y la renta anual computable se introducen por separado.")
    with st.form("orientacion"):
        age = st.number_input("Edad", min_value=0, max_value=120, value=25)
        income = st.number_input("Ingresos netos mensuales (EUR)", min_value=0., value=0.)
        annual = st.number_input("Ingresos anuales computables documentados (EUR)", min_value=0., value=0.)
        rent = st.number_input("Tu pago mensual real de alquiler (EUR)", min_value=0., value=0.)
        total_rent = st.number_input("Renta total de la vivienda (EUR/mes)", min_value=0., value=0.)
        debts = st.number_input("Deudas mensuales (EUR)", min_value=0., value=0.)
        savings = st.number_input("Ahorro disponible (EUR)", min_value=0., value=0.)
        entry = st.number_input("Coste real de entrada, fianza y gastos (EUR)", min_value=0., value=0.)
        household = st.selectbox("Unidad solicitante", ["individual", "familiar", "numerosa"])
        shared = st.checkbox("Contrato compartido: requiere comprobar reparto y limites", value=False)
        checks = {}
        for key, label in [("residencia_6_meses", "Residencia previa acreditada"),
                           ("vivienda_habitual_libre", "Vivienda habitual de mercado libre"),
                           ("contrato_titular", "Titularidad del contrato acreditada"),
                           ("pagos_bancarios", "Pagos bancarios acreditados"),
                           ("sin_propiedad_disponible", "Sin vivienda en propiedad disponible"),
                           ("sin_parentesco", "Sin parentesco excluyente"),
                           ("sin_incompatibilidades", "Incompatibilidades comprobadas")]:
            checks[key] = st.checkbox(label, value=False, key=key)
        group800 = st.checkbox("Municipio no capital: limite de 800 EUR comprobado documentalmente", value=False)
        submit = st.form_submit_button("Predecir referencia y orientar")
    if submit:
        estimated = float(model.predict(pd.DataFrame([features])[FEATURES])[0])
        case = {"municipio": names.get(code, code), "codigo_municipio": code, "edad": age,
                "ingresos_mensuales": income, "ingresos_anuales_computables": annual,
                "unidad": household, "precio_alquiler": rent, "renta_total_vivienda": total_rent,
                "deudas_mensuales": debts, "ahorros_disponibles": savings, "coste_entrada": entry,
                "contrato_compartido": shared, "municipio_grupo_800_verificado": group800,
                "modelo_en_cobertura": bool(np.isfinite(features["renta_lag1"])), **checks}
        decision = MotorReglasVivienda().evaluar(case, renta_estimada=estimated).to_dict()
        st.session_state["decision_vivienda"] = decision
        st.session_state["event_id_vivienda"] = str(uuid.uuid4())
    if "decision_vivienda" in st.session_state:
        st.json(st.session_state["decision_vivienda"])
        st.caption("El esfuerzo declarado usa tu contrato y deudas. El esfuerzo de referencia supone pagar íntegra la renta municipal predicha. El umbral interno del 40% orienta la comparación de municipios; no decide ayudas.")
        consent = st.checkbox("Autorizo enviar SOLO decision y referencia municipal a n8n; sin salario ni datos identificativos")
        if st.button("Registrar accion en n8n", disabled=not consent):
            response = N8NWebhookClient().disparar_accion(st.session_state["decision_vivienda"], event_id=st.session_state["event_id_vivienda"])
            if response["estado"] == "ENVIADO_N8N":
                st.success("Accion confirmada por n8n")
            else:
                st.error("No se confirma el envio: no se simula un exito")
            st.json(response)
