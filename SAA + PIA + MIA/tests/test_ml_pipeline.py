"""
tests/test_ml_pipeline.py - Suite de pruebas unitarias para SAA + PIA + MIA.
Valida el preprocesador, los 5 modelos, SMOTE, MLP, el motor de reglas y la integración con n8n.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from src.pipeline import HousingPreprocessorPipeline
from src.ml_models import (
    LogisticRegressionModel,
    KNNClassifier,
    RandomForestModel,
    XGBoostModel,
    SVMClassifier,
    MLPNeuralNetwork,
    SMOTEBalancer,
    calcular_metricas
)
from src.reglas import MotorReglasVivienda
from src.n8n import N8NWebhookClient


@pytest.fixture
def sample_dataset():
    """Genera un mini conjunto representativo para pruebas rápidas."""
    train_rows = [
        {"solicitud_id": "S1", "municipio": "Bilbao", "edad": "25", "tipo_contrato": "Indefinido",
         "ingresos_mensuales": 1500.0, "precio_alquiler": 600.0, "antiguedad_laboral_meses": 24.0,
         "ahorros_disponibles": 3000.0, "comparte_piso": "No", "deudas_mensuales": 0.0,
         "tipo_subvencion": "Gaztelagun", "es_viable": 1},
        {"solicitud_id": "S2", "municipio": "Donostia-San Sebastián", "edad": None, "tipo_contrato": "Temporal",
         "ingresos_mensuales": 1100.0, "precio_alquiler": 1100.0, "antiguedad_laboral_meses": 4.0,
         "ahorros_disponibles": 400.0, "comparte_piso": "No", "deudas_mensuales": 150.0,
         "tipo_subvencion": "Gaztelagun", "es_viable": 0},
        {"solicitud_id": "S3", "municipio": "Vitoria-Gasteiz", "edad": "28", "tipo_contrato": "Indefinido",
         "ingresos_mensuales": 1400.0, "precio_alquiler": 550.0, "antiguedad_laboral_meses": 36.0,
         "ahorros_disponibles": 5000.0, "comparte_piso": "No", "deudas_mensuales": 0.0,
         "tipo_subvencion": "Gaztelagun", "es_viable": 1},
        {"solicitud_id": "S4", "municipio": "Barakaldo", "edad": "22", "tipo_contrato": "En_Practicas",
         "ingresos_mensuales": 950.0, "precio_alquiler": 700.0, "antiguedad_laboral_meses": 6.0,
         "ahorros_disponibles": 200.0, "comparte_piso": "No", "deudas_mensuales": 0.0,
         "tipo_subvencion": "Gaztelagun", "es_viable": 0},
        {"solicitud_id": "S5", "municipio": "Bilbao", "edad": "30", "tipo_contrato": "Indefinido",
         "ingresos_mensuales": 1600.0, "precio_alquiler": 800.0, "antiguedad_laboral_meses": 48.0,
         "ahorros_disponibles": 4000.0, "comparte_piso": "Si", "deudas_mensuales": 0.0,
         "tipo_subvencion": "Gaztelagun", "es_viable": 1}
    ]
    return train_rows


def test_pipeline_fit_transform_and_inference(sample_dataset):
    """Verifica que el preprocesador imputa nulos, escala numéricas y codifica categóricas."""
    pipe = HousingPreprocessorPipeline()
    X_mat = pipe.fit_transform(sample_dataset)
    assert len(X_mat) == len(sample_dataset)
    for fila in X_mat:
        for val in fila:
            assert isinstance(val, (int, float))

    caso_nuevo = {
        "solicitud_id": "NEW-1", "municipio": "Bilbao", "edad": None,
        "tipo_contrato": "Indefinido", "ingresos_mensuales": 1400.0,
        "precio_alquiler": 650.0, "antiguedad_laboral_meses": 12.0,
        "ahorros_disponibles": None, "comparte_piso": "No",
        "deudas_mensuales": 0.0, "tipo_subvencion": "Gaztelagun"
    }
    x_single = pipe.transform_single(caso_nuevo)
    assert len(x_single) == len(X_mat[0])


def test_all_five_models_execution(sample_dataset):
    """Verifica que los 5 modelos clasificadores entrenan y emiten probabilidades coherentes."""
    pipe = HousingPreprocessorPipeline()
    X = pipe.fit_transform(sample_dataset)
    y = [r["es_viable"] for r in sample_dataset]

    modelos = [
        LogisticRegressionModel(epochs=10),
        KNNClassifier(k=3),
        RandomForestModel(n_estimators=5),
        XGBoostModel(n_estimators=5),
        SVMClassifier(epochs=10)
    ]

    for m in modelos:
        m.fit(X, y)
        probs = m.predict_proba(X)
        preds = m.predict(X)
        assert len(probs) == len(X)
        assert len(preds) == len(X)
        for p in probs:
            assert 0.0 <= p <= 1.0


def test_smote_balancer(sample_dataset):
    """Verifica que SMOTE iguala el conteo de la clase minoritaria."""
    pipe = HousingPreprocessorPipeline()
    X = pipe.fit_transform(sample_dataset)
    y = [r["es_viable"] for r in sample_dataset]

    smote = SMOTEBalancer(seed=42)
    X_res, y_res = smote.fit_resample(X, y)
    assert len(y_res) >= len(y)
    assert y_res.count(0) == y_res.count(1)


def test_mlp_neural_network_activations(sample_dataset):
    """Verifica el entrenamiento de MLP con ReLU y Tanh."""
    pipe = HousingPreprocessorPipeline()
    X = pipe.fit_transform(sample_dataset)
    y = [r["es_viable"] for r in sample_dataset]

    mlp_relu = MLPNeuralNetwork(hidden_layers=(8,), activation="relu", epochs=5)
    mlp_relu.fit(X, y)
    p_relu = mlp_relu.predict_proba(X)
    assert len(p_relu) == len(X)

    mlp_tanh = MLPNeuralNetwork(hidden_layers=(8,), activation="tanh", epochs=5)
    mlp_tanh.fit(X, y)
    p_tanh = mlp_tanh.predict_proba(X)
    assert len(p_tanh) == len(X)


def test_reglas_negocio_prioridad_y_fallback():
    """El motor no transforma probabilidades sinteticas en concesiones."""
    dec = MotorReglasVivienda().evaluar({}, prob_viable=0.99)
    assert dec.decision == 'REVISION_DATOS'
    assert dec.prioridad == 100
    assert 'No concede' in dec.aviso


def test_n8n_integration():
    """La demo solo construye payloads; no simula una accion enviada."""
    client = N8NWebhookClient(demo_mode=True)
    res = client.disparar_accion({'decision': 'REVISION_DATOS'}, {'nombre': 'No transmitir'})
    assert res['estado'] == 'DEMO_NO_ENVIADO'
    assert 'nombre' not in str(res['payload_enviado'])
