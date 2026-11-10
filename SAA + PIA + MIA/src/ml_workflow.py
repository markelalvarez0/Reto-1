"""Flujo docente reproducible: EMAL -> EDA -> CV -> MLflow -> SHAP.

El test permanece reservado. Solo evaluate_test_once(), llamado desde Streamlit,
lo evalua y conserva un informe inmutable vinculado al modelo y al dataset.
"""
import hashlib
import json
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.ml_data import FEATURES, NUMERIC, CATEGORICAL, TARGET, read_emal, temporal_split, temporal_folds
from src.ml_models import regression_models, regression_metrics, calcular_metricas
from src.mlflow_tracker import MLflowTracker
from src.pipeline import build_preprocessor


def _json(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding="utf-8")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_eda(train, output):
    """Cinco graficos de matplotlib con conclusiones calculadas solo en train."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    notes = {}
    dictionary = pd.DataFrame({"campo": train.columns, "tipo": [str(v) for v in train.dtypes],
                               "nulos_pct_train": train.isna().mean().to_numpy() * 100})
    dictionary.to_csv(output / "diccionario.csv", index=False)
    train.groupby("anio")[NUMERIC].apply(lambda x: x.isna().mean()).to_csv(output / "patron_nulos_por_anio.csv")
    means = train.groupby("municipio")[TARGET].mean().sort_values()
    fig, ax = plt.subplots(figsize=(9, 7)); means.plot.barh(ax=ax)
    ax.set(xlabel="Renta media (EUR/mes)", title="EMAL: promedio de trimestres de entrenamiento")
    fig.tight_layout(); fig.savefig(output / "01_barras.png", dpi=140); plt.close(fig)
    notes["01_barras.png"] = f"{means.index[-1]} presenta la mayor media de train ({means.iloc[-1]:.2f} EUR). Es una media de agregados trimestrales, no ponderada por contratos."
    fig, ax = plt.subplots(); ax.hist(train[TARGET], bins=20)
    ax.set(xlabel="Renta municipal (EUR/mes)", ylabel="Municipio/trimestres", title="Distribucion del objetivo en train")
    fig.tight_layout(); fig.savefig(output / "02_histograma.png", dpi=140); plt.close(fig)
    notes["02_histograma.png"] = f"La mediana de train es {train[TARGET].median():.2f} EUR. El objetivo es una renta municipal observada, no la viabilidad de una persona."
    fig, ax = plt.subplots(); ax.boxplot(train[TARGET].dropna())
    ax.set(ylabel="EUR/mes", title="Dispersion de rentas municipales de train")
    fig.tight_layout(); fig.savefig(output / "03_boxplot.png", dpi=140); plt.close(fig)
    q1, q3 = train[TARGET].quantile([.25, .75])
    notes["03_boxplot.png"] = f"IQR = {q3-q1:.2f} EUR. No se eliminan precios altos solo por ser extremos: pueden reflejar diferencias territoriales reales."
    fig, ax = plt.subplots(); ax.scatter(train.renta_lag1, train[TARGET], alpha=.45)
    ax.set(xlabel="Renta del trimestre previo", ylabel="Renta del trimestre actual", title="Relacion temporal (train)")
    fig.tight_layout(); fig.savefig(output / "04_dispersion.png", dpi=140); plt.close(fig)
    notes["04_dispersion.png"] = f"Correlacion lag1/objetivo = {train[['renta_lag1', TARGET]].corr().iloc[0,1]:.3f}. La persistencia debe ser un baseline; correlacion no demuestra causalidad."
    corr = train[NUMERIC + [TARGET]].corr()
    fig, ax = plt.subplots(figsize=(8, 6)); image = ax.imshow(corr, vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr)), corr.columns); fig.colorbar(image, ax=ax)
    ax.set_title("Correlaciones de train")
    fig.tight_layout(); fig.savefig(output / "05_correlacion.png", dpi=140); plt.close(fig)
    notes["05_correlacion.png"] = "Los retardos recogen persistencia. Ni la renta actual, ni su precio/m2, ni una categoria derivada del objetivo se incluyen entre las entradas."
    notes["nulos"] = "Los '-' de EMAL significan no disponible/oferta insuficiente. Los retardos iniciales faltan por construccion. Se conserva el patron; las medianas y categorias se ajustan dentro de cada fold, nunca con test."
    _json(output / "conclusiones_eda.json", notes)
    return notes


def _smote_experiment(train, val, tracker, output):
    """Ampliacion: predecir subida trimestral observada, no crear perfiles ficticios.

    SMOTE se aplica solo a variables numericas escaladas dentro de cada fold.
    Las categorias se omiten en este experimento auxiliar para no interpolar OHE.
    """
    a = train.dropna(subset=["renta_lag1"]).reset_index(drop=True)
    b = val.dropna(subset=["renta_lag1"]).reset_index(drop=True)
    ya = (a[TARGET] > a.renta_lag1).astype(int)
    yb = (b[TARGET] > b.renta_lag1).astype(int)
    counts = ya.value_counts().to_dict()
    results = {"objetivo": "sube_renta_respecto_trimestre_anterior", "clases_train": counts,
               "datos": "EMAL observado; solo numericas; no solicitantes ni elegibilidad", "modelos": {}}
    if len(counts) < 2 or min(counts.values()) < 6:
        results["estado"] = "No se aplica SMOTE: insuficientes ejemplos minoritarios"
        _json(Path(output) / "comparacion_smote.json", results)
        return
    for balance in (False, True):
        steps = [("preprocesado", build_preprocessor(NUMERIC, []))]
        if balance:
            steps.append(("smote", SMOTE(random_state=42, k_neighbors=3)))
        steps.append(("modelo", LogisticRegression(max_iter=1000, random_state=42)))
        model = ImbPipeline(steps)
        start = time.perf_counter(); model.fit(a[NUMERIC], ya)
        elapsed = time.perf_counter() - start
        metrics = calcular_metricas(yb, model.predict(b[NUMERIC]), model.predict_proba(b[NUMERIC])[:, 1])
        name = "subida_con_SMOTE" if balance else "subida_sin_SMOTE"
        scalar = {f"val_{k}": v for k, v in metrics.items() if isinstance(v, (int, float))}
        run_id = tracker.log_run(name, {"smote": balance, "clases_train": counts, "objetivo": results["objetivo"]},
                                {**scalar, "tiempo_s": elapsed}, tags={"tipo": "auxiliar_clasificacion"})
        results["modelos"][name] = {"run_id": run_id, **metrics, "tiempo_s": elapsed}
    results["estado"] = "comparacion_real_en_validacion_sin_tocar_test"
    _json(Path(output) / "comparacion_smote.json", results)


def explain_validation(model, train, val, output):
    """SHAP sobre validacion, fondo de train; valores en EUR, no probabilidades."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import shap
    prep = model.named_steps["preprocesado"]
    background = prep.transform(train[FEATURES].sample(min(30, len(train)), random_state=42))
    subset = val[FEATURES].sample(min(30, len(val)), random_state=42)
    matrix = prep.transform(subset)
    names = prep.get_feature_names_out()
    explainer = shap.Explainer(model.named_steps["modelo"].predict,
                              shap.maskers.Independent(background), algorithm="permutation",
                              feature_names=names, seed=42)
    values = explainer(matrix, max_evals=4 * (2 * len(names) + 1))
    table = pd.DataFrame({"variable": names, "media_abs_shap_eur": np.abs(values.values).mean(axis=0)})
    table = table.sort_values("media_abs_shap_eur", ascending=False)
    output = Path(output)
    table.to_csv(output / "shap_validacion.csv", index=False)
    top = table.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 6)); ax.barh(top.variable, top.media_abs_shap_eur)
    ax.set(xlabel="Media de |SHAP| (EUR)", title="Explicabilidad del ganador: validacion, no test")
    fig.tight_layout(); fig.savefig(output / "shap_validacion.png", dpi=140); plt.close(fig)
    _json(output / "shap_metadatos.json", {"filas": len(subset), "indices_validacion": subset.index.tolist(),
                                          "fondo": "30 filas de entrenamiento", "algoritmo": "permutation",
                                          "unidad": "EUR de renta municipal", "causal": False})


def train_official(raw_dir, output_dir="entrega_ml"):
    """Entrena y selecciona con train/validacion; el test solo se guarda reservado."""
    out = Path(output_dir).resolve()
    if (out / "models/selection.json").exists():
        raise FileExistsError("Existe una seleccion cerrada. No sobrescribir ni reajustar tras consultar test.")
    for folder in ("data", "models", "resultados"):
        (out / folder).mkdir(parents=True, exist_ok=True)
    frame, meta = read_emal(raw_dir)
    train, val, test = temporal_split(frame)
    for name, part in (("train", train), ("val", val), ("test", test)):
        part.to_csv(out / "data" / f"{name}.csv", index=False)
    meta["particiones"] = {name: {"filas": len(part), "desde": int(part.periodo.min()), "hasta": int(part.periodo.max())}
                            for name, part in (("train", train), ("val", val), ("test", test))}
    _json(out / "data/procedencia.json", meta)
    make_eda(train, out / "resultados")
    tracker = MLflowTracker(tracking_dir=out / "mlruns")
    fitted, runs = {}, []
    grids = {"KNN": {"modelo__regressor__n_neighbors": [3, 7]},
             "Random_Forest": {"modelo__regressor__min_samples_leaf": [1, 3]},
             "XGBoost": {"modelo__regressor__max_depth": [2, 3]},
             "SVM": {"modelo__regressor__C": [1., 10.]}}
    for name, estimator in regression_models().items():
        pipeline = Pipeline([("preprocesado", build_preprocessor(NUMERIC, CATEGORICAL)),
                             ("modelo", TransformedTargetRegressor(regressor=estimator, transformer=StandardScaler()))])
        start = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            if name in grids:
                search = GridSearchCV(pipeline, grids[name], cv=temporal_folds(train),
                                      scoring="neg_mean_absolute_error", n_jobs=1, error_score="raise")
                search.fit(train[FEATURES], train[TARGET])
                pipeline = search.best_estimator_
                parameters = search.best_params_
            else:
                pipeline.fit(train[FEATURES], train[TARGET])
                parameters = estimator.get_params()
        elapsed = time.perf_counter() - start
        metrics = {"tiempo_s": elapsed}
        for split, part in (("train", train), ("val", val)):
            metrics.update({f"{split}_{k}": v for k, v in regression_metrics(part[TARGET], pipeline.predict(part[FEATURES])).items()})
        metrics["avisos_entrenamiento"] = len(caught)
        run_id = tracker.log_run(name, parameters, metrics, model=pipeline,
                                tags={"tipo": "regresion", "objetivo": TARGET})
        fitted[name] = pipeline
        runs.append({"modelo": name, "run_id": run_id, **metrics})
        print(json.dumps(runs[-1], ensure_ascii=False), flush=True)
    # La tabla de entrega procede de la consulta real a MLflow.
    tracked = tracker.results()
    tracked = tracked.loc[tracked["tags.tipo"].eq("regresion")].copy()
    columns = {"tags.mlflow.runName": "modelo", "run_id": "run_id",
               **{f"metrics.{key}": key for key in runs[0] if key not in {"modelo", "run_id"}}}
    table = tracked[list(columns)].rename(columns=columns).sort_values("val_mae")
    table.to_csv(out / "resultados/comparativa_mlflow.csv", index=False)
    winner = str(table.iloc[0].modelo)
    linear = table.loc[table.modelo.eq("Regresion_lineal")].iloc[0]
    if float(linear.val_mae) <= float(table.iloc[0].val_mae) * 1.01:
        winner = "Regresion_lineal"  # Dentro del 1% se prefiere el modelo mas sencillo.
    baseline_rows = val.dropna(subset=["renta_lag1"])
    baseline = regression_metrics(baseline_rows[TARGET], baseline_rows.renta_lag1)
    joblib.dump(fitted[winner], out / "models/best_model.joblib")
    selection = {"modelo": winner, "criterio": "MAE validacion; empate del 1% a favor de regresion lineal",
                 "mae_val": float(table.loc[table.modelo.eq(winner), "val_mae"].iloc[0]),
                 "baseline_persistencia_val": baseline, "sha256_modelo": sha256(out / "models/best_model.joblib"),
                 "sha256_test": sha256(out / "data/test.csv"), "features": FEATURES, "objetivo": TARGET,
                 "municipios": sorted(train.codigo_municipio.unique().tolist()),
                 "max_periodo_entrenamiento": int(train.periodo.max()),
                 "max_periodo_validacion": int(val.periodo.max()),
                 "test_evaluado": False, "unidad_prediccion": "renta media municipal trimestral, no precio de un anuncio individual"}
    _json(out / "models/selection.json", selection)
    explain_validation(fitted[winner], train, val, out / "resultados")
    _smote_experiment(train, val, tracker, out / "resultados")
    _json(out / "resultados/resumen.json", {"dataset": meta, "seleccion": selection,
                                          "experimentos_regresion": len(runs), "test": "reservado para Streamlit"})
    return selection


def evaluate_test_once(output_dir):
    """Evalua el ganador una unica vez y devuelve el informe cacheado en reaperturas.

    Un bloqueo de archivo evita evaluaciones concurrentes. No selecciona modelos,
    no reajusta parametros y no actualiza la imputacion con test.
    """
    out = Path(output_dir).resolve()
    selection = json.loads((out / "models/selection.json").read_text(encoding="utf-8"))
    model_hash, test_hash = sha256(out / "models/best_model.joblib"), sha256(out / "data/test.csv")
    if model_hash != selection["sha256_modelo"] or test_hash != selection["sha256_test"]:
        raise ValueError("Modelo o test cambiados despues de cerrar la seleccion")
    report = out / "resultados/test_final.json"
    if report.exists():
        result = json.loads(report.read_text(encoding="utf-8"))
        if result["sha256_modelo"] != model_hash or result["sha256_test"] != test_hash:
            raise ValueError("Informe final de otra version: no reutilizar ni reevaluar silenciosamente")
        return result
    lock = out / "resultados/.test_en_evaluacion"
    try:
        with lock.open("x", encoding="utf-8") as handle:
            handle.write(model_hash)
    except FileExistsError as exc:
        raise RuntimeError("La evaluacion esta en curso o fue interrumpida; revisar antes de repetir") from exc
    model = joblib.load(out / "models/best_model.joblib")
    test = pd.read_csv(out / "data/test.csv", dtype={"codigo_municipio": str})
    predicted = model.predict(test[FEATURES])
    result = {"modelo": selection["modelo"], "n_test": len(test),
              **regression_metrics(test[TARGET], predicted), "sha256_modelo": model_hash, "sha256_test": test_hash,
              "evaluaciones": 1, "aviso": "Holdout retrospectivo de agregados EMAL; no valida elegibilidad ni decisiones personales."}
    pd.DataFrame({"real": test[TARGET], "predicho": predicted}).to_csv(out / "resultados/predicciones_test.csv", index=False)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(); ax.scatter(test[TARGET], predicted, alpha=.6)
    low, high = float(test[TARGET].min()), float(test[TARGET].max())
    ax.plot([low, high], [low, high], linestyle="--")
    ax.set(xlabel="Renta real (EUR)", ylabel="Prediccion (EUR)", title="Test reservado: modelo previamente elegido")
    fig.tight_layout(); fig.savefig(out / "resultados/test_real_predicho.png", dpi=140); plt.close(fig)
    _json(report, result)
    lock.unlink()
    return result
