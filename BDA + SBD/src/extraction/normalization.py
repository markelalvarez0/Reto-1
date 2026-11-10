"""Conversion de valores observados. Nunca imputa datos de mercado."""
import math
import re
from numbers import Real
from typing import Any, Optional


def numero_observado(value: Any, *, minimo: float = 0.0, entero: bool = False) -> Optional[float]:
    """Convierte numeros y formatos espanoles; devuelve None si son invalidos."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        value = value.strip().replace('\u00a0', '').replace(' ', '')
        value = re.sub(r'(?:EUR|\u20ac|/mes|m\u00b2|m2)$', '', value, flags=re.I)
        if not value:
            return None
        if ',' in value:
            value = value.replace('.', '').replace(',', '.')
        elif re.fullmatch(r'[+-]?\d{1,3}(?:\.\d{3})+', value):
            value = value.replace('.', '')
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(result) or result < minimo or (entero and not result.is_integer()):
        return None
    return int(result) if entero else result


def booleano_observado(value: Any) -> Optional[bool]:
    """Distingue False de ausencia; nunca usa bool('false')."""
    if isinstance(value, bool):
        return value
    if isinstance(value, Real) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        value = value.strip().casefold()
        if value in {'true', '1', 'si', 's\u00ed', 'yes'}:
            return True
        if value in {'false', '0', 'no'}:
            return False
    return None


def primer_valor(*values: Any) -> Any:
    """Primer valor informado, conservando ceros y falsos observados."""
    return next((v for v in values if v is not None and v != ''), None)
