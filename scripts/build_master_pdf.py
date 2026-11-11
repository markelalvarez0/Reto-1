#!/usr/bin/env python3
"""Entrada compatible: informe vigente desde artefactos verificados.

El generador histórico se sustituyó para evitar métricas sintéticas obsoletas.
No ejecuta el modelo ni vuelve a evaluar test.
"""
from build_delivery_report import main

if __name__ == '__main__':
    main()
