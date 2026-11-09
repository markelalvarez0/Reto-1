"""
conftest.py - Configuración global de pytest y resolución de paths multiasignatura.
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegurar módulos intermodulares y por asignatura en sys.path
paths_to_add = [
    os.path.join(ROOT_DIR, "BDA + SBD"),
    os.path.join(ROOT_DIR, "SAA + PIA + MIA"),
    os.path.join(ROOT_DIR, "ainhoa"),
    ROOT_DIR
]

for p in paths_to_add:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)
