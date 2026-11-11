"""El transporte rechaza derivados corruptos o simulados antes de emitirlos."""
import hashlib
import json
import pytest
from scripts.transport_municipal import FILES, load_verified


def export_fixture(folder, motor='MongoDB'):
    manifest = []
    for name in sorted(FILES):
        data = json.dumps({'motor': motor} if name == 'metadatos.json' else []).encode()
        (folder / name).write_bytes(data)
        manifest.append({'archivo': name, 'sha256': hashlib.sha256(data).hexdigest()})
    (folder / 'manifest.json').write_text(json.dumps(manifest))


def test_corrupted_export_is_rejected(tmp_path):
    export_fixture(tmp_path)
    (tmp_path / 'serie_trimestral.json').write_text('[1]')
    with pytest.raises(ValueError, match='Huella'):
        load_verified(tmp_path)


def test_simulated_export_cannot_be_presented_as_real(tmp_path):
    export_fixture(tmp_path, 'mongomock')
    with pytest.raises(ValueError, match='MongoDB real'):
        load_verified(tmp_path)


def test_manifest_cannot_repeat_or_escape_files(tmp_path):
    export_fixture(tmp_path)
    path = tmp_path / 'manifest.json'
    rows = json.loads(path.read_text())
    rows[0]['archivo'] = '../outside.json'
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match='incompleto'):
        load_verified(tmp_path)
