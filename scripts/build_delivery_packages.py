"""Empaqueta dos entregas autocontenidas; excluye material de preparación oral.

Solo lee código y evidencias conservados. No carga modelos ni ejecuta servicios.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/entrega'
BLOCKS = ('BDA_SBD', 'SAA_PIA_MIA')
COMMON = ('AGENTS.md', '.gitignore', 'main.py', 'conftest.py', 'pyproject.toml',
          'uv.lock', 'requirements.txt', 'requirements-ci.txt',
          'scripts/build_academic_docs.py', 'docs/entrega/requirements-documentacion.txt')
VERIFIER = '''"""Comprueba los archivos entregados sin ejecutar el modelo ni los servicios."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFIESTO_ENTREGA.json').read_text(encoding='utf-8'))
errors = []
for entry in manifest['archivos']:
    path = root / entry['ruta']
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        errors.append(entry['ruta'] + ': ruta no valida')
    elif not path.is_file():
        errors.append(entry['ruta'] + ': archivo ausente')
    elif hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        errors.append(entry['ruta'] + ': contenido modificado')
if errors:
    print('\\n'.join(errors))
    raise SystemExit(1)
print(f"OK: {len(manifest['archivos'])} archivos verificados. No se ha ejecutado el modelo.")
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(block):
    files: dict[str, bytes] = {}

    def add(relative):
        path = ROOT / relative
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f'Ruta no admisible: {relative}')
        if path.name.lower() == 'readme.md' or path.name == 'Instrucciones_restauracion.md':
            return
        if path.is_dir():
            for item in sorted(path.rglob('*')):
                if item.is_file() and '__pycache__' not in item.parts and item.suffix != '.pyc':
                    add(str(item.relative_to(ROOT)))
        else:
            files[relative] = path.read_bytes()

    for name in COMMON:
        add(name)
    add('src')
    add('data/capturas_oficiales')
    for kind in ('Documentacion', 'Presentacion'):
        for extension in ('pdf', 'md'):
            source = f'docs/entrega/{block}/{kind}_{block}.{extension}'
            add(source)
            if extension == 'md':
                # Incluir cada imagen referenciada por los documentos editables.
                for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', files[source].decode()):
                    add(str((ROOT / source).parent.joinpath(image).resolve().relative_to(ROOT)))

    if block == 'BDA_SBD':
        add('app/territorio.py')
        add('BDA + SBD/main.py')
        for name in ('run_pipeline', 'analyze_municipal', 'analyze_rental_sample',
                     'transport_municipal', 'transport_rent_api', 'capture_emal_api',
                     'capture_rentals', 'capture_sources'):
            add(f'scripts/{name}.py')
        add('data/capturas_anuncios')
        add('data/capturas_api_rentas')
        add('data/exportaciones_entrega_2026-11-17')
        add('infra')
        add('.github/workflows/bda-candidate.yml')
        excluded = {'test_business_rules.py', 'test_ml_pipeline.py', 'test_ml_standard.py',
                    'test_project_audit.py', 'test_project_launcher.py', 'test_delivery_report.py'}
        for test in sorted((ROOT/'tests').glob('test_*.py')):
            if test.name not in excluded:
                add(str(test.relative_to(ROOT)))
        for test in sorted((ROOT/'integration_tests').glob('test_*.py')):
            add(str(test.relative_to(ROOT)))
        for name in ('anuncios', 'municipal', 'transporte', 'integracion-final.xml',
                     'transporte-municipal.json', 'territorio.png', 'muestra_anuncios.png',
                     'resumen.json', 'acceso.json'):
            add(f'docs/evidencias_entrega_2026-11-12/{name}')
        for name in ('api-transporte-1.json', 'api-transporte-2.json', 'api-visor.png', 'integracion.xml'):
            add(f'docs/evidencias_cierre_rubrica_2026-11-12/{name}')
        for name in ('RESULTADOS_ANUNCIOS.md', 'ANALISIS_MUNICIPAL.md'):
            if (ROOT/'docs'/name).exists():
                add(f'docs/{name}')
    else:
        add('app/streamlit_app.py')
        for name in ('action_server', 'train_official', 'capture_sources'):
            add(f'scripts/{name}.py')
        add('notebooks')
        add('entrega_ml')
        add('n8n')
        add('docs/evidencias_ml')
        add('docs/TEST_FINAL_EMAL.json')
        for name in ('test_ml_pipeline', 'test_ml_standard', 'test_business_rules'):
            add(f'tests/{name}.py')
        add('integration_tests/check_n8n_live.py')
        for name in ('app-n8n.json', 'caso.png', 'n8n.txt'):
            add(f'docs/evidencias_cierre_rubrica_2026-11-12/{name}')
        add('docs/evidencias_entrega_2026-11-12/n8n-live.json')

    # Procedencia solo de los apoyos visuales pertenecientes al bloque.
    visual_source = json.loads((DOCS/'assets/procedencia_visuales.json').read_text(encoding='utf-8'))
    visual_names = {Path(name).name for name in files if name.startswith('docs/entrega/assets/')}
    visual = {key: value for key, value in visual_source.items()
              if key in {'fecha', 'captura', 'entrenamientos_nuevos', 'test_reevaluado', 'servicios_bda_repetidos'}
              or key in visual_names}
    visual['graficos'] = {key: value for key, value in visual_source['graficos'].items() if key in visual_names}
    files['docs/entrega/assets/procedencia_visuales.json'] = (json.dumps(visual, ensure_ascii=False, indent=2)+'\n').encode()
    instructions = f'Instrucciones_{block}.pdf'
    files[instructions] = (ROOT/'docs/paquetes'/instructions).read_bytes()
    # El paquete entrega las instrucciones en PDF y no depende de un README.md
    # para construir su distribución Python. Las dependencias no cambian.
    project = files['pyproject.toml'].decode('utf-8')
    project, removed = re.subn(r'^readme = "README\.md"\n', '', project, flags=re.M)
    if removed != 1:
        raise ValueError('Revisar la referencia al README en pyproject.toml')
    files['pyproject.toml'] = project.encode('utf-8')
    files['verificar_entrega.py'] = VERIFIER.encode()
    for name in files:
        if any(term in name.lower() for term in ('guion_oral', 'guia_defensa', 'guia_entrega_y_defensa', 'revision_rubricas')):
            raise ValueError(f'Material de preparación dentro de la entrega: {name}')
        if '.venv' in Path(name).parts or Path(name).name.startswith('.env'):
            raise ValueError(f'Archivo local no admisible: {name}')
        if Path(name).name.lower() == 'readme.md':
            raise ValueError(f'Las instrucciones se entregan en PDF: {name}')
    expected_pdfs = {f'docs/entrega/{block}/{kind}_{block}.pdf' for kind in ('Documentacion', 'Presentacion')}
    expected_pdfs.add(instructions)
    if block == 'BDA_SBD':
        expected_pdfs.add('data/exportaciones_entrega_2026-11-17/Instrucciones_restauracion.pdf')
    if {name for name in files if name.endswith('.pdf')} != expected_pdfs:
        raise ValueError('Los PDF del paquete no coinciden con memoria, presentación e instrucciones')
    manifest = {
        'bloque': block, 'fecha': '2026-11-17',
        'repositorio': 'https://github.com/markelalvarez0/Reto-1',
        'codigo_base_conservado': '0f990531c86a7b4f247cb80631b02609fed687a0',
        'contenido': 'Memoria, presentación, instrucciones en PDF y archivos funcionales; sin README.md ni material oral de preparación',
        'test_reevaluado_al_empaquetar': False,
        'archivos': [{'ruta': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in sorted(files.items())],
    }
    files['MANIFIESTO_ENTREGA.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode()
    name = f'Entrega_{block}'
    target = ROOT/f'{name}.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, data in sorted(files.items()):
            entry = zipfile.ZipInfo(f'{name}/{path}', date_time=(2026, 11, 17, 12, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP con error de integridad: '+target.name)
    result = {'archivo': target.name, 'bytes': target.stat().st_size,
              'sha256': sha(target.read_bytes()), 'archivos': len(files), 'pdf': sorted(expected_pdfs)}
    print(f'{target.name}: {len(files)} archivos, {target.stat().st_size/1_000_000:.2f} MB')
    return result


def main():
    result = [build(block) for block in BLOCKS]
    (ROOT/'docs/paquetes/manifest_paquetes.json').write_text(
        json.dumps({'fecha': '2026-11-17', 'paquetes': result}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
