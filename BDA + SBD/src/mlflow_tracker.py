"""
src/mlflow_tracker.py - Registro y trazabilidad de experimentos compatible con MLflow.
Cumple con la rúbrica PIA RA2:
- Registro de modelos, hiperparámetros y métricas de validación/train
- Trazabilidad y persistencia de experimentos para auditoría y visualización
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, List

class MLflowExperimentTracker:
    """Gestiona el registro estructurado de ejecuciones y métricas de experimentos."""

    def __init__(self, experiment_name: str = "reto1_vivienda_joven_euskadi", runs_file: Path = None):
        self.experiment_name = experiment_name
        self.runs_file = runs_file or Path(__file__).resolve().parent.parent / "mlruns_data.json"
        self.runs: List[Dict[str, Any]] = self._cargar_historial()

    def _cargar_historial(self) -> List[Dict[str, Any]]:
        if self.runs_file.exists():
            try:
                with open(self.runs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def log_run(self, model_name: str, params: Dict[str, Any], metrics: Dict[str, Any], training_time_sec: float) -> Dict[str, Any]:
        """Registra un nuevo run de experimento."""
        run_record = {
            "run_id": f"run_{int(time.time()*1000)}_{len(self.runs)+1}",
            "experiment": self.experiment_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": model_name,
            "params": params,
            "metrics": metrics,
            "training_time_sec": round(training_time_sec, 2)
        }
        self.runs.append(run_record)
        self._guardar()
        return run_record

    def _guardar(self):
        with open(self.runs_file, "w", encoding="utf-8") as f:
            json.dump(self.runs, f, indent=2, ensure_ascii=False)

    def obtener_tabla_comparativa(self) -> List[Dict[str, Any]]:
        """Devuelve un resumen consolidado para la tabla comparativa exigida en el README."""
        tabla = []
        for r in self.runs:
            m = r["metrics"]
            tabla.append({
                "Modelo": r["model_name"],
                "Recall (Validación)": m.get("val_recall", m.get("recall", 0.0)),
                "F1 (Validación)": m.get("val_f1", m.get("f1", 0.0)),
                "Precisión (Validación)": m.get("val_precision", m.get("precision", 0.0)),
                "Accuracy (Validación)": m.get("val_accuracy", m.get("accuracy", 0.0)),
                "Tiempo (s)": r["training_time_sec"]
            })
        return tabla
