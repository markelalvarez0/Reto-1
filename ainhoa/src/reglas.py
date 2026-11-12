"""Orientacion de vivienda: reglas trazables, nunca resoluciones administrativas.

Norma parametrizada: Orden de 5/6/2026, BOPV 15/6/2026, bases 2, 5 y 7.
El modelo predice renta municipal, NO elegibilidad ni riesgo individual.
"""
from dataclasses import asdict, dataclass
from datetime import date
import math
from typing import Any, Callable
from src.extraction.models import resolver_codigo_ine

NORMA_URL = 'https://www.euskadi.eus/bopv2/datos/2026/06/2602608a.shtml'
LIMITES_ANUALES = {'individual': 30000.0, 'familiar': 36764.0, 'numerosa': 39184.0}
CAPITALES = {'48020', '20069', '01059'}
DECISIONES = ('REVISION_DATOS', 'REVISION_NORMATIVA', 'ORIENTACION_PRIORITARIA',
              'REVISION_REQUISITOS', 'BUSCAR_ALTERNATIVAS', 'PLANIFICAR_ENTRADA',
              'CONSULTAR_GAZTELAGUN', 'INFORMACION_GENERAL')


@dataclass(frozen=True)
class DecisionNegocio:
    regla_id: str
    nombre_regla: str
    prioridad: int
    decision: str
    accion_recomendada: str
    justificacion_negocio: str
    renta_estimada: float | None
    esfuerzo_pct: float | None
    ayuda_teorica_max: float | None = None
    canal_notificacion: str = 'registro_local_n8n'
    aviso: str = 'Orientativo. No concede ni deniega ayudas. Se requiere comprobacion administrativa.'
    norma: str = NORMA_URL
    esfuerzo_referencia_pct: float | None = None

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Regla:
    id: str
    prioridad: int
    decision: str
    motivo: str
    accion: str
    condicion: Callable[[dict], bool]


def numero(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


class MotorReglasVivienda:
    """Primera regla aplicable en prioridad descendente, como en la plantilla MIA."""
    def __init__(self):
        self.reglas = [
            Regla('R_SEGURIDAD', 100, 'REVISION_DATOS', 'Faltan datos, hay valores imposibles o el modelo esta fuera de cobertura.', 'Abrir tarea de verificacion sin resolver derechos.', lambda c: c['invalido']),
            Regla('R_NORMA', 95, 'REVISION_NORMATIVA', 'La convocatoria parametrizada solo cubre 2026.', 'Comprobar convocatoria vigente antes de orientar sobre ayudas.', lambda c: c['fecha'].year != 2026),
            Regla('R_ESFUERZO_CRITICO', 90, 'ORIENTACION_PRIORITARIA', 'El coste declarado supera el 70% del ingreso neto disponible; es un umbral interno, no una norma legal.', 'Crear solicitud de asesoramiento prioritario, sin denegacion automatica.', lambda c: c['esfuerzo'] > 70),
            Regla('R_REQUISITOS', 80, 'REVISION_REQUISITOS', 'Un requisito basico declarado requiere revision; ingreso anual computable no equivale a salario neto por doce.', 'Generar lista de requisitos que revisar con personal tecnico.', lambda c: c['requisito_no_cumplido']),
            Regla('R_DOCUMENTACION', 75, 'REVISION_NORMATIVA', 'Faltan comprobaciones o hay excepciones territoriales/contractuales no resueltas.', 'Preparar checklist documental; revisar limite de renta y excepciones.', lambda c: not c['documentacion_completa'] or c['limite_pendiente']),
            Regla('R_ALTERNATIVAS', 70, 'BUSCAR_ALTERNATIVAS', 'El coste supera el 40% del ingreso neto; comparar alternativas sin dar por concedida una ayuda.', 'Crear ficha de alternativas y presupuesto maximo orientativo.', lambda c: c['esfuerzo'] > 40),
            Regla('R_REFERENCIA', 65, 'BUSCAR_ALTERNATIVAS', 'La renta municipal predicha supera el 40% del ingreso declarado en el escenario de pagarla integra; no es el alquiler real ni un requisito de ayudas.', 'Comparar referencias de otros municipios y presupuesto, manteniendo separado el contrato declarado.', lambda c: c['esfuerzo_referencia'] is not None and c['esfuerzo_referencia'] > 40),
            Regla('R_ENTRADA', 60, 'PLANIFICAR_ENTRADA', 'El ahorro declarado no cubre la entrada estimada por el usuario.', 'Crear plan de ahorro para entrada; no ofrecer creditos ficticios.', lambda c: c['ahorros'] < c['entrada']),
            Regla('R_GAZTELAGUN', 50, 'CONSULTAR_GAZTELAGUN', 'Comprobaciones basicas declaradas completas; la cuantia maxima es orientativa y esta sujeta a la resolucion oficial.', 'Generar checklist de solicitud Gaztelagun, nunca una concesion.', lambda c: c['esfuerzo'] > 30),
            Regla('R_GENERAL', 0, 'INFORMACION_GENERAL', 'Caso sin alertas anteriores; la renta predicha es una media municipal, no una oferta individual.', 'Guardar una ficha informativa de presupuesto y limites del modelo.', lambda c: True),
        ]

    def evaluar(self, caso: dict[str, Any], prob_viable=None, *, renta_estimada=None, fecha=None):
        """prob_viable se ignora: la clasificacion sintetica no decide sobre personas."""
        fecha = fecha or date.today()
        income = numero(caso.get('ingresos_mensuales'))
        rent = numero(caso.get('precio_alquiler', renta_estimada))
        debt = numero(caso.get('deudas_mensuales'))
        age = numero(caso.get('edad'))
        annual = numero(caso.get('ingresos_anuales_computables'))
        savings = numero(caso.get('ahorros_disponibles'))
        entry = numero(caso.get('coste_entrada'))
        estimate = numero(renta_estimada)
        group = caso.get('unidad', 'individual')
        invalid = any(v is None for v in (income, rent, debt, age, savings, entry))
        invalid = invalid or (income is not None and income <= 0) or any(v is not None and v < 0 for v in (rent, debt, savings, entry))
        invalid = invalid or (age is not None and (not age.is_integer() or age < 0 or age > 120))
        invalid = invalid or group not in LIMITES_ANUALES or caso.get('modelo_en_cobertura') is not True
        invalid = invalid or (renta_estimada is not None and (estimate is None or estimate <= 0))
        effort = (rent + debt) / income * 100 if not invalid else None
        reference_effort = estimate / income * 100 if not invalid and estimate is not None else None
        code = resolver_codigo_ine(caso.get('municipio'))
        # Unknown municipal classification is reviewed rather than assumed.
        limit = 900 if code in CAPITALES else 800 if caso.get('municipio_grupo_800_verificado') is True else None
        total_rent = numero(caso.get('renta_total_vivienda'))
        pending_limit = limit is None or total_rent is None or total_rent > limit or caso.get('contrato_compartido') is True
        document_fields = ('residencia_6_meses', 'vivienda_habitual_libre', 'contrato_titular', 'pagos_bancarios', 'sin_propiedad_disponible', 'sin_parentesco', 'sin_incompatibilidades')
        missing = any(caso.get(k) is not True for k in document_fields) or annual is None
        failed = (age is not None and not 18 <= age <= 35) or (annual is not None and not 3000 < annual <= LIMITES_ANUALES.get(group, 0))
        failed = failed or any(caso.get(k) is False for k in document_fields)
        context = {'invalido': invalid, 'fecha': fecha, 'esfuerzo': effort, 'requisito_no_cumplido': failed,
                   'documentacion_completa': not missing, 'limite_pendiente': pending_limit,
                   'ahorros': savings, 'entrada': entry, 'esfuerzo_referencia': reference_effort}
        rule = next(rule for rule in sorted(self.reglas, key=lambda r: -r.prioridad) if rule.condicion(context))
        aid = min(300.0, 0.6 * rent) if rule.decision == 'CONSULTAR_GAZTELAGUN' else None
        return DecisionNegocio(rule.id, rule.id, rule.prioridad, rule.decision, rule.accion, rule.motivo,
                               estimate, effort, aid, esfuerzo_referencia_pct=reference_effort)
