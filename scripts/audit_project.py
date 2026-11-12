"""Auditoría de bytes y contratos publicados. No importa ni ejecuta modelos."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root=ROOT):
    """Devuelve todos los controles, incluidos los fallidos; no modifica archivos."""
    root = Path(root).resolve()
    checks = []

    def check(name, operation):
        try:
            checks.append({"control": name, "ok": True, "detalle": operation()})
        except (ValueError, OSError, KeyError, TypeError) as exc:
            checks.append({"control": name, "ok": False, "detalle": str(exc)})

    def read(relative):
        return json.loads((root / relative).read_text(encoding="utf-8"))

    def verify_files(entries):
        entries = list(entries)
        if not entries:
            raise ValueError("Manifiesto vacío")
        errors, seen = [], set()
        for entry in entries:
            name = entry["archivo"]
            path = root / name
            if path.is_symlink() or not path.resolve().is_relative_to(root) or name in seen:
                errors.append(f"Ruta inválida o duplicada: {name}")
            elif not path.is_file() or digest(path) != entry["sha256"]:
                errors.append(f"Huella incorrecta o archivo ausente: {name}")
            seen.add(name)
        if errors:
            raise ValueError("; ".join(errors))
        return {"archivos_verificados": len(entries)}

    check("originales", lambda: verify_files(
        {"archivo": "data/capturas_oficiales/" + e["archivo"], "sha256": e["sha256"]}
        for e in read("data/capturas_oficiales/manifest.json")["fuentes"] if e.get("estado") == "descargado"))
    check("artefactos_ml", lambda: verify_files(read("docs/evidencias_ml/manifest.json")))

    def sealed_test():
        selection = read("entrega_ml/models/selection.json")
        report = read("entrega_ml/resultados/test_final.json")
        if report != read("docs/TEST_FINAL_EMAL.json"):
            raise ValueError("El informe de test publicado difiere del conservado")
        if report.get("evaluaciones") != 1:
            raise ValueError("No se acredita una única evaluación")
        for file, key in [("models/best_model.joblib", "sha256_modelo"), ("data/test.csv", "sha256_test")]:
            if digest(root / "entrega_ml" / file) != report[key]:
                raise ValueError("El test sellado no corresponde a " + file)
        if selection["sha256_modelo"] != report["sha256_modelo"]:
            raise ValueError("Selección y evaluación corresponden a modelos distintos")
        return {"modelo": report["modelo"], "evaluaciones": 1, "modelo_ejecutado": False}

    check("test_sellado", sealed_test)

    def mirrors():
        sources = sorted((root / "src").rglob("*.py"))
        mismatches = []
        for source in sources:
            for folder in ("BDA + SBD", "SAA + PIA + MIA", "ainhoa"):
                target = root / folder / "src" / source.relative_to(root / "src")
                if not target.is_file() or digest(target) != digest(source):
                    mismatches.append(str(target.relative_to(root)))
        if not sources or mismatches:
            raise ValueError("Fuentes ausentes o copias diferentes: " + ", ".join(mismatches))
        return "Tres copias académicas coinciden con src/"

    check("copias_academicas", mirrors)
    check("captura_anuncios", lambda: verify_files(
        {"archivo": "data/capturas_anuncios/" + e["archivo"], "sha256": e["sha256"]}
        for e in read("data/capturas_anuncios/manifest.json")))
    return {"ok": all(item["ok"] for item in checks), "controles": checks,
            "alcance": "Integridad local. No acredita servicios activos, scraping vigente ni cumplimiento completo de rúbricas."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = audit()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in result["controles"]:
            print(("OK" if item["ok"] else "ERROR"), item["control"], item["detalle"])
        print(result["alcance"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
