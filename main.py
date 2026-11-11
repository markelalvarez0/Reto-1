#!/usr/bin/env python3
"""Portal de BDA/SBD y SAA/PIA/MIA; abre el modelo conservado sin reentrenar."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BDA_SUBJECTS = {'bda_sbd', 'bda', 'sbd', 'ainhoa'}


def run(command):
    """Conserva el código de salida y ejecuta desde la raíz del proyecto."""
    return subprocess.call([sys.executable, *map(str, command)], cwd=ROOT)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject', choices=sorted(BDA_SUBJECTS | {'saa_pia_mia', 'saa', 'pia', 'mia'}))
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--test', action='store_true', help='Ejecutar toda la suite tests/')
    action.add_argument('--audit', action='store_true', help='Verificar integridad sin ejecutar modelos')
    action.add_argument('--pdf', action='store_true', help='Generar informe desde artefactos verificados sin ejecutar el modelo')
    args, extra = parser.parse_known_args(argv)
    if args.test:
        return run(['-m', 'pytest', 'tests', *extra])
    if args.audit:
        return run([ROOT / 'scripts/audit_project.py', *extra])
    if args.pdf:
        return run([ROOT / 'scripts/build_delivery_report.py', *extra])
    if args.subject in BDA_SUBJECTS:
        if '--visual' in extra:
            if '--pipeline' in extra:
                parser.error('Ejecute el pipeline y el visor en comandos separados.')
            return run(['-m', 'streamlit', 'run', ROOT / 'app/territorio.py',
                        *[value for value in extra if value != '--visual']])
        return run([ROOT / 'scripts/run_pipeline.py', *extra])
    if args.subject:
        if '--pipeline' in extra:
            parser.error('Entrenamiento explícito: scripts/train_official.py --output DIRECTORIO_NUEVO')
        extra = [value for value in extra if value != '--visual']
        return run(['-m', 'streamlit', 'run', ROOT / 'app/streamlit_app.py', *extra])
    if extra:
        parser.error('Indique --subject para las opciones: ' + ' '.join(extra))
    print('Reto 1 · Vivienda joven en Euskadi\n'
          '  python main.py --subject bda_sbd --prepare-only\n'
          '  python main.py --subject bda_sbd --pipeline\n'
          '  python main.py --subject saa_pia_mia\n'
          '  python main.py --test -q\n'
          '  python main.py --audit --json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
