"""Regresion contra algoritmos reinventados, fuga temporal y test reutilizado."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import openpyxl
import pandas as pd
import pytest
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline

from src.pipeline import HousingPreprocessorPipeline, build_preprocessor, SimpleImputer, StandardScaler, OneHotEncoder
from src.ml_models import (LogisticRegressionModel, KNNClassifier, RandomForestModel,
                           XGBoostModel, SVMClassifier, MLPNeuralNetwork, SMOTEBalancer,
                           regression_models, regression_metrics)
from src.ml_data import read_emal, temporal_split, temporal_folds, FEATURES, NUMERIC, CATEGORICAL, TARGET
from src.ml_workflow import evaluate_test_once, sha256
from src.mlflow_tracker import MLflowTracker


def test_componentes_son_sklearn_real():
    for component in (SimpleImputer, StandardScaler, OneHotEncoder):
        assert component.__module__.startswith("sklearn.")
    assert isinstance(build_preprocessor(["numero"], ["grupo"]), ColumnTransformer)


@pytest.mark.parametrize("adapter,prefix", [
    (LogisticRegressionModel, "sklearn."), (KNNClassifier, "sklearn."),
    (RandomForestModel, "sklearn."), (XGBoostModel, "xgboost."),
    (SVMClassifier, "sklearn."), (MLPNeuralNetwork, "sklearn.")])
def test_estimadores_proceden_de_librerias(adapter, prefix):
    assert adapter().estimator.__class__.__module__.startswith(prefix)


def test_nueve_experimentos_y_red_separada():
    models = regression_models()
    assert len(models) == 9
    assert sum(name.startswith("MLP_") for name in models) == 4
    assert {"Regresion_lineal", "KNN", "Random_Forest", "XGBoost", "SVM"}.issubset(models)


def test_transform_no_ajusta_validacion_y_persistencia(tmp_path):
    rows = [{"edad": 20, "ingresos_mensuales": 1000, "precio_alquiler": 500, "municipio": "Bilbao"},
            {"edad": 30, "ingresos_mensuales": 2000, "precio_alquiler": 600, "municipio": "Getxo"}]
    pipe = HousingPreprocessorPipeline().fit(rows)
    means = pipe.preprocessor_.named_transformers_["numericas"].named_steps["escalar"].mean_.copy()
    value = {"edad": 1000000, "municipio": "CategoriaNueva"}
    transformed = pipe.transform_single(value)
    np.testing.assert_equal(means, pipe.preprocessor_.named_transformers_["numericas"].named_steps["escalar"].mean_)
    assert len(transformed) == len(pipe.get_feature_names())
    assert np.isfinite(transformed).all()
    path = tmp_path / "preprocesado.joblib"
    pipe.save(path)
    np.testing.assert_allclose(HousingPreprocessorPipeline.load(path).transform_single(value), transformed)
    with pytest.raises(ValueError, match="JSON"):
        HousingPreprocessorPipeline.from_dict({})


def test_smote_real_determinista_y_vecinos_insuficientes():
    X = [[0., 0.], [1., 0.], [2., 0.], [3., 0.], [4., 1.], [5., 1.]]
    y = [0, 0, 0, 0, 1, 1]
    balancer = SMOTEBalancer()
    xr, yr = balancer.fit_resample(X, y)
    assert isinstance(balancer.sampler_, SMOTE)
    assert yr.count(0) == yr.count(1)
    assert (xr, yr) == SMOTEBalancer().fit_resample(X, y)
    with pytest.raises(ValueError, match="dos ejemplos"):
        SMOTEBalancer().fit_resample(X[:5], y[:5])


@pytest.fixture
def emal_fixture(tmp_path):
    book = openpyxl.Workbook(); book.remove(book.active)
    years = list(range(2016, 2027))
    for sheet_name, is_rent in [("T1.1", False), ("T1.2", True)]:
        sheet = book.create_sheet(sheet_name)
        sheet.append(["Fixture sintetica para pruebas de lectura, no fuente productiva"])
        header = ["Indicador", None]
        quarter = [None, None]
        for year in years:
            header.extend([year, None, None, None]); quarter.extend(["I", "II", "III", "IV"])
        header.extend(["Alquileres vigentes", None]); quarter.extend(["31/12/2025", "31/03/2026"])
        sheet.append(header); sheet.append(quarter)
        for code, name in [("01059", "Vitoria-Gasteiz"), ("48020", "Bilbao"), ("48036", "Galdakao(1)")]:
            values = [500. + i if is_rent else 100 + i for i in range(len(years) * 4)]
            if is_rent:
                values[1] = "-"
            sheet.append([code, name, *values, 999999, 999999])
    original = tmp_path / "emal_municipios.xlsx"; book.save(original)
    manifest = {"fuentes": [{"archivo": original.name, "estado": "descargado", "sha256": sha256(original), "url_final": "https://example.invalid/fixture"}]}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_emal_ceros_nulos_retardos_y_exclusion_stock(emal_fixture):
    frame, meta = read_emal(emal_fixture)
    assert "01059" in set(frame.codigo_municipio)
    assert "48036" not in set(frame.codigo_municipio)
    assert frame[TARGET].max() < 999999
    assert meta["objetivos_no_publicados_excluidos"] == 2
    q3 = frame.loc[(frame.anio == 2016) & (frame.trimestre == 3)]
    assert q3.renta_lag1.isna().all()  # No saltar sobre el trimestre no publicado.
    assert TARGET not in FEATURES and "numero_contratos" not in FEATURES
    train, val, test = temporal_split(frame)
    assert train.periodo.max() < val.periodo.min() < test.periodo.min()
    for a, b in temporal_folds(train):
        assert train.iloc[a].periodo.max() < train.iloc[b].periodo.min()


def test_original_modificado_es_rechazado(emal_fixture):
    with (emal_fixture / "emal_municipios.xlsx").open("ab") as handle:
        handle.write(b"corrupto")
    with pytest.raises(ValueError, match="huella"):
        read_emal(emal_fixture)


def test_metricas_regresion_conocidas():
    metrics = regression_metrics([1., 2., 3.], [1., 2., 3.])
    assert metrics == {"mae": 0., "rmse": 0., "r2": 1.}


def test_mlflow_registra_de_verdad(tmp_path):
    tracker = MLflowTracker("fixture_prueba", tmp_path / "mlruns")
    run_id = tracker.log_run("fixture", {"caso": "prueba"}, {"mae": 1.25}, tags={"fuente": "fixture_unitaria"})
    table = tracker.results()
    assert table.iloc[0].run_id == run_id
    assert table.iloc[0]["metrics.mae"] == pytest.approx(1.25)
    assert (tmp_path / "mlruns/mlflow.db").exists()


def test_test_final_cacheado_y_huellas(tmp_path, monkeypatch):
    for folder in ("models", "data", "resultados"):
        (tmp_path / folder).mkdir()
    X = pd.DataFrame([{**{name: float(i + 1) for name in NUMERIC}, "codigo_municipio": "48020", "provincia": "Bizkaia"} for i in range(8)])
    y = np.arange(8.) + 500
    model = Pipeline([("preprocesado", build_preprocessor(NUMERIC, CATEGORICAL)), ("modelo", DummyRegressor())]).fit(X, y)
    model_file = tmp_path / "models/best_model.joblib"; joblib.dump(model, model_file)
    data = X.copy(); data[TARGET] = y; data.to_csv(tmp_path / "data/test.csv", index=False)
    metadata = {"modelo": "fixture", "sha256_modelo": sha256(model_file), "sha256_test": sha256(tmp_path / "data/test.csv")}
    (tmp_path / "models/selection.json").write_text(json.dumps(metadata), encoding="utf-8")
    first = evaluate_test_once(tmp_path)
    assert first["evaluaciones"] == 1 and first["n_test"] == 8
    def forbidden(*args, **kwargs):
        raise AssertionError("No se debe volver a cargar ni ejecutar el modelo")
    monkeypatch.setattr("src.ml_workflow.joblib.load", forbidden)
    assert evaluate_test_once(tmp_path) == first
    with (tmp_path / "data/test.csv").open("a") as handle:
        handle.write("\n")
    with pytest.raises(ValueError, match="cambiados"):
        evaluate_test_once(tmp_path)
