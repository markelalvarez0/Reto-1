"""Integridad sin deserializar artefactos ejecutables ni recalcular test."""
import json
from scripts.audit_project import audit, digest, ROOT


def test_published_artifacts_are_intact():
    result = audit(ROOT)
    assert result["ok"], result


def test_audit_reports_all_errors_without_changing_files(tmp_path):
    folder = tmp_path / "docs/evidencias_ml"
    folder.mkdir(parents=True)
    manifest = folder / "manifest.json"
    manifest.write_text(json.dumps([{"archivo": "../escape", "sha256": "bad"}]))
    before = digest(manifest)
    result = audit(tmp_path)
    assert not result["ok"]
    assert len(result["controles"]) == 4
    assert all(not item["ok"] for item in result["controles"])
    assert "Ruta inválida" in result["controles"][1]["detalle"]
    assert digest(manifest) == before
