"""El portal no reentrena al abrir la app y conserva errores de subprocess."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reto_launcher", ROOT / "main.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def test_ml_opens_saved_app_without_training(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher.subprocess, "call", lambda command, **kwargs: calls.append((command, kwargs)) or 7)
    assert launcher.main(["--subject", "saa_pia_mia", "--visual", "--server.headless=true"]) == 7
    assert len(calls) == 1
    command, options = calls[0]
    assert command[1:4] == ["-m", "streamlit", "run"]
    assert command[4] == str(ROOT / "app/streamlit_app.py")
    assert command[5] == "--server.headless=true"
    assert options["cwd"] == ROOT


def test_bda_relative_output_is_relative_to_project(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = []
    monkeypatch.setattr(launcher.subprocess, "call", lambda command, **kwargs: calls.append((command, kwargs)) or 0)
    assert launcher.main(["--subject", "bda", "--prepare-only", "--raw-dir", "data/prepared"]) == 0
    assert calls[0][0][-3:] == ["--prepare-only", "--raw-dir", "data/prepared"]
    assert calls[0][1]["cwd"] == ROOT


def test_full_suite_and_exit_status(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher, "run", lambda command: calls.append(command) or 3)
    assert launcher.main(["--test", "-q"]) == 3
    assert calls == [["-m", "pytest", "tests", "-q"]]


def test_training_and_historical_pdf_are_not_implicit():
    with pytest.raises(SystemExit):
        launcher.main(["--subject", "saa", "--pipeline"])
    with pytest.raises(SystemExit):
        launcher.main(["--pdf"])
