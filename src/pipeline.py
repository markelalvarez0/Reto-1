"""Preprocesamiento con componentes reales de scikit-learn.

El ajuste se hace exclusivamente con entrenamiento. Los JSON de la antigua
implementacion manual no son modelos sklearn y deben volver a entrenarse.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted


def build_preprocessor(numeric_features, categorical_features):
    """Construye un preprocesador nuevo: nunca comparte estado entre modelos."""
    transformers = []
    if numeric_features:
        transformers.append(("numericas", Pipeline([
            ("imputar", SimpleImputer(strategy="median", keep_empty_features=True)),
            ("escalar", StandardScaler()),
        ]), list(numeric_features)))
    if categorical_features:
        transformers.append(("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
            ("codificar", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), list(categorical_features)))
    if not transformers:
        raise ValueError("Debe especificarse al menos una variable de entrada")
    return ColumnTransformer(transformers, remainder="drop", sparse_threshold=0)


class HousingPreprocessorPipeline(TransformerMixin, BaseEstimator):
    """Interfaz compatible para los ejercicios antiguos, delegada en sklearn.

    Los perfiles sinteticos son material docente, no evidencia de viabilidad real.
    El modelo entregable de renta municipal utiliza build_preprocessor directamente.
    """
    def __init__(self):
        self.num_features = ["edad", "ingresos_mensuales", "precio_alquiler",
                             "antiguedad_laboral_meses", "ahorros_disponibles",
                             "deudas_mensuales", "ratio_esfuerzo"]
        self.cat_features = ["municipio", "tipo_contrato", "comparte_piso", "tipo_subvencion"]
        self.is_fitted = False

    def _frame(self, rows):
        frame = pd.DataFrame(rows).reindex(columns=self.num_features + self.cat_features)
        for name in self.num_features:
            frame[name] = pd.to_numeric(frame[name], errors="coerce")
        income = frame["ingresos_mensuales"].where(frame["ingresos_mensuales"] > 0)
        frame["ratio_esfuerzo"] = frame["precio_alquiler"] / income
        frame[self.num_features] = frame[self.num_features].replace([np.inf, -np.inf], np.nan)
        for name in self.cat_features:
            frame[name] = frame[name].map(
                lambda v: np.nan if pd.isna(v) or str(v).strip() == "" else str(v)
            ).astype(object)
        return frame

    def fit(self, raw_rows, y=None):
        frame = self._frame(raw_rows)
        if frame.empty:
            raise ValueError("No hay filas de entrenamiento")
        self.preprocessor_ = build_preprocessor(self.num_features, self.cat_features)
        self.preprocessor_.fit(frame)
        self.is_fitted = True
        return self

    def fit_transform(self, raw_rows, y=None, **fit_params):
        return self.fit(raw_rows, y).transform(raw_rows)

    def transform(self, raw_rows):
        check_is_fitted(self, "preprocessor_")
        return self.preprocessor_.transform(self._frame(raw_rows)).astype(float).tolist()

    def transform_single(self, record):
        return self.transform([record])[0]

    def get_feature_names(self):
        check_is_fitted(self, "preprocessor_")
        return self.preprocessor_.get_feature_names_out().tolist()

    def save(self, path):
        """Guarda el preprocesador ajustado; cargar solo artefactos de confianza."""
        check_is_fitted(self, "preprocessor_")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path):
        instance = joblib.load(path)
        if not isinstance(instance, cls):
            raise ValueError("El artefacto no contiene el preprocesador esperado")
        check_is_fitted(instance, "preprocessor_")
        return instance

    def to_dict(self):
        raise ValueError("Persistir con save()/joblib; un JSON manual no conserva el pipeline sklearn")

    @classmethod
    def from_dict(cls, data):
        raise ValueError("Modelo JSON antiguo no compatible: volver a entrenar y guardar con joblib")
