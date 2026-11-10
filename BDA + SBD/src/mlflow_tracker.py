"""Registro real de experimentos en MLflow; no simula un servidor con JSON."""
from pathlib import Path
import math

import mlflow
import mlflow.sklearn


class MLflowTracker:
    """Almacenamiento local SQLite y artefactos MLflow reproducibles."""
    def __init__(self, experiment_name="Reto1_EMAL", tracking_dir="mlruns"):
        self.root = Path(tracking_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.tracking_uri = "sqlite:///" + (self.root / "mlflow.db").as_posix()
        mlflow.set_tracking_uri(self.tracking_uri)
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)
        self.experiment_id = (experiment.experiment_id if experiment else
                              client.create_experiment(experiment_name, artifact_location=(self.root / "artifacts").as_uri()))

    def log_run(self, name, params, metrics, model=None, artifacts=(), tags=None):
        """Registra solo medidas calculadas, con modelo y ficheros verificables."""
        mlflow.set_tracking_uri(self.tracking_uri)
        with mlflow.start_run(experiment_id=self.experiment_id, run_name=name) as run:
            mlflow.log_params({key: str(value)[:500] for key, value in params.items()})
            for key, value in metrics.items():
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError(f"Metrica no finita: {key}")
                mlflow.log_metric(key, number)
            mlflow.set_tags({"fuente": "EMAL_observado", "test_utilizado": "no", **(tags or {})})
            if model is not None:
                mlflow.sklearn.log_model(model, artifact_path="modelo", serialization_format="cloudpickle")
            for path in artifacts:
                mlflow.log_artifact(str(path))
            return run.info.run_id

    def results(self):
        """Tabla obtenida de MLflow, no de una copia de metricas escrita a mano."""
        mlflow.set_tracking_uri(self.tracking_uri)
        return mlflow.search_runs(experiment_ids=[self.experiment_id], output_format="pandas")
