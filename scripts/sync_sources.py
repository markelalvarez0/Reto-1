"""Sincroniza src/ con las carpetas academicas, o verifica sus hashes."""
import argparse
import hashlib
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
MIRRORS = ('BDA + SBD', 'SAA + PIA + MIA', 'ainhoa')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    mismatches = []
    for source in sorted((ROOT / 'src').rglob('*.py')):
        relative = source.relative_to(ROOT / 'src')
        for mirror in MIRRORS:
            target = ROOT / mirror / 'src' / relative
            equal = target.exists() and hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
            if not equal:
                if args.check:
                    mismatches.append(str(target.relative_to(ROOT)))
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
    if mismatches:
        raise SystemExit('Copias desincronizadas:\n' + '\n'.join(mismatches))
    print('Copias de src verificadas.' if args.check else 'Copias de src sincronizadas.')


if __name__ == '__main__':
    main()
