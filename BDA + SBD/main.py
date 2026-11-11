#!/usr/bin/env python3
"""Entrada del bloque BDA + SBD: delega en el pipeline canonico probado."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_pipeline import main

if __name__ == "__main__":
    # Mantener UTF-8 tambien al capturar la salida en Windows.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    main()
