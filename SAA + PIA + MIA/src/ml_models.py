"""Estimadores oficiales, metricas sklearn y balanceo imbalanced-learn.

Las clases de compatibilidad devuelven una lista de probabilidades de clase 1.
No implementan algoritmos a mano. Para nuevos experimentos se usan las factorias
que devuelven los estimadores nativos. No entrenar sobre test ni remuestrearlo.
"""
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             mean_absolute_error, mean_squared_error,
                             precision_score, recall_score, r2_score, roc_auc_score)
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import SVC, SVR
from sklearn.utils.validation import check_is_fitted
from xgboost import XGBClassifier, XGBRegressor


def calcular_metricas(y_real, y_pred, y_prob=None):
    """Metricas binarias observadas; clase positiva 1, orden de matriz [0, 1]."""
    truth, pred = np.asarray(y_real), np.asarray(y_pred)
    if truth.size == 0 or len(truth) != len(pred):
        raise ValueError("Etiquetas vacias o longitudes diferentes")
    if not set(np.unique(truth)).issubset({0, 1}) or not set(np.unique(pred)).issubset({0, 1}):
        raise ValueError("Se esperan etiquetas binarias 0/1")
    tn, fp, fn, tp = confusion_matrix(truth, pred, labels=[0, 1]).ravel()
    result = {
        "accuracy": float(accuracy_score(truth, pred)),
        "precision": float(precision_score(truth, pred, zero_division=0)),
        "recall": float(recall_score(truth, pred, zero_division=0)),
        "f1": float(f1_score(truth, pred, zero_division=0)),
        "matriz_confusion": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
    }
    if y_prob is not None and len(np.unique(truth)) == 2:
        result["roc_auc"] = float(roc_auc_score(truth, y_prob))
    return result


def regression_metrics(y_real, y_pred):
    """MAE/RMSE expresados en la unidad del objetivo; R2 sin unidad."""
    return {"mae": float(mean_absolute_error(y_real, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_real, y_pred))),
            "r2": float(r2_score(y_real, y_pred))}


class _BinaryAdapter:
    def fit(self, X, y):
        X, y = np.asarray(X, dtype=float), np.asarray(y)
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("El entrenamiento binario requiere clases 0 y 1")
        self.estimator.fit(X, y)
        return self

    def predict_proba(self, X):
        check_is_fitted(self.estimator)
        positive = list(self.estimator.classes_).index(1)
        return self.estimator.predict_proba(np.asarray(X, dtype=float))[:, positive].tolist()

    def predict(self, X, threshold=0.5):
        if not 0 <= threshold <= 1:
            raise ValueError("Umbral fuera de [0, 1]")
        return (np.asarray(self.predict_proba(X)) >= threshold).astype(int).tolist()


class LogisticRegressionModel(_BinaryAdapter):
    def __init__(self, epochs=1000, reg_l2=1.0, seed=42):
        self.estimator = LogisticRegression(max_iter=epochs, C=1.0 / max(reg_l2, 1e-9), random_state=seed)


class KNNClassifier(_BinaryAdapter):
    def __init__(self, k=5):
        self.estimator = KNeighborsClassifier(n_neighbors=k)


class RandomForestModel(_BinaryAdapter):
    def __init__(self, n_estimators=100, seed=42, **kwargs):
        self.estimator = RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=1, **kwargs)


class XGBoostModel(_BinaryAdapter):
    def __init__(self, n_estimators=100, lr=0.05, seed=42, **kwargs):
        self.estimator = XGBClassifier(n_estimators=n_estimators, learning_rate=lr, random_state=seed,
                                       n_jobs=1, tree_method="hist", eval_metric="logloss", **kwargs)


class SVMClassifier(_BinaryAdapter):
    def __init__(self, C=1.0, epochs=1000, seed=42, **kwargs):
        self.estimator = SVC(C=C, probability=True, max_iter=epochs, random_state=seed, **kwargs)


class MLPNeuralNetwork(_BinaryAdapter):
    def __init__(self, hidden_layers=(16,), lr=0.001, epochs=200, activation="relu", alpha=0.0001, seed=42):
        self.estimator = MLPClassifier(hidden_layer_sizes=hidden_layers, learning_rate_init=lr,
                                       max_iter=epochs, activation=activation, alpha=alpha, random_state=seed)


class SMOTEBalancer:
    """Adaptador docente de SMOTE real. Usar solo en entrenamiento o dentro de CV."""
    def __init__(self, k_neighbors=5, seed=42):
        if k_neighbors < 1:
            raise ValueError("k_neighbors debe ser positivo")
        self.k_neighbors, self.seed = k_neighbors, seed

    def fit_resample(self, X, y):
        X, y = np.asarray(X, dtype=float), np.asarray(y)
        classes, counts = np.unique(y, return_counts=True)
        if len(classes) != 2:
            raise ValueError("SMOTE requiere dos clases en este adaptador")
        if counts[0] == counts[1]:
            return X.tolist(), y.tolist()
        if min(counts) < 2:
            raise ValueError("SMOTE necesita al menos dos ejemplos minoritarios; no se inventan vecinos")
        self.sampler_ = SMOTE(k_neighbors=min(self.k_neighbors, int(min(counts)) - 1), random_state=self.seed)
        xr, yr = self.sampler_.fit_resample(X, y)
        return xr.tolist(), yr.tolist()


def regression_models(seed=42):
    """Cinco familias obligatorias y MLP base + tres experimentos separados."""
    return {
        "Regresion_lineal": LinearRegression(),
        "KNN": KNeighborsRegressor(n_neighbors=7, weights="distance"),
        "Random_Forest": RandomForestRegressor(n_estimators=150, min_samples_leaf=3, random_state=seed, n_jobs=1),
        "XGBoost": XGBRegressor(n_estimators=150, max_depth=3, learning_rate=0.05, objective="reg:squarederror", random_state=seed, n_jobs=1, tree_method="hist"),
        "SVM": SVR(C=10, epsilon=0.05),
        "MLP_base": MLPRegressor(hidden_layer_sizes=(32,), max_iter=1000, random_state=seed),
        "MLP_2_capas": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=seed),
        "MLP_tanh": MLPRegressor(hidden_layer_sizes=(32,), activation="tanh", max_iter=1000, random_state=seed),
        "MLP_regularizada": MLPRegressor(hidden_layer_sizes=(32,), alpha=0.01, max_iter=1000, random_state=seed),
    }
