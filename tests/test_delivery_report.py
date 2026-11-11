"""El informe conserva código MongoDB con dólares y no ejecuta el modelo."""
from pathlib import Path
import joblib
from scripts.build_delivery_report import build
from scripts.audit_project import audit


def test_report_preserves_code_and_sealed_artifacts(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Generar el informe no debe cargar ni ejecutar el modelo')
    monkeypatch.setattr(joblib, 'load', forbidden)
    result = build(tmp_path)
    assert result.read_bytes().startswith(b'%PDF')
    text = (tmp_path / 'informe.md').read_text(encoding='utf-8')
    code = (Path(__file__).resolve().parents[1] / 'src/municipal_analysis.py').read_text(encoding='utf-8')
    assert code in text  # Código completo; $lookup/$unwind son literales, no fórmulas.
    assert audit()['ok']
