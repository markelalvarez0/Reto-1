"""
src/reglas.py - Motor de reglas de negocio para el Reto MIA (Modelos de IA).
Cumple con la rúbrica MIA RA5:
- 6 o más reglas con prioridad estricta
- Decisión de negocio clara
- Justificación ("Por qué") económica y social
- Regla de seguridad / Fallback por defecto
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class DecisionNegocio:
    regla_id: str
    nombre_regla: str
    prioridad: int
    decision: str
    accion_recomendada: str
    canal_notificacion: str
    justificacion_negocio: str
    probabilidad_modelo: float


class MotorReglasVivienda:
    """Motor experto de decisión basado en la predicción probabilística del modelo y datos del joven."""

    def __init__(self):
        self.reglas = [
            self._regla_1_riesgo_extremo,
            self._regla_2_aprobacion_expres,
            self._regla_3_fianza_vulnerable,
            self._regla_4_alquiler_compartido,
            self._regla_5_mercado_tensionado_vpo,
            self._regla_6_seguridad_fallback
        ]

    def evaluar(self, caso: Dict[str, Any], prob_viable: float) -> DecisionNegocio:
        """Evalúa un caso por orden de prioridad estricta hasta encontrar coincidencia."""
        for regla_fn in self.reglas:
            resultado = regla_fn(caso, prob_viable)
            if resultado is not None:
                return resultado
        return self._regla_6_seguridad_fallback(caso, prob_viable)

    # -------------------------------------------------------------
    # REGLA 1 (Prioridad 1): Riesgo Extremo de Insolvencia
    # -------------------------------------------------------------
    def _regla_1_riesgo_extremo(self, caso: Dict[str, Any], p: float) -> Optional[DecisionNegocio]:
        alquiler = float(caso.get("precio_alquiler", 800.0))
        ingresos = max(float(caso.get("ingresos_mensuales", 1200.0)), 1.0)
        deudas = float(caso.get("deudas_mensuales", 0.0))
        comparte = caso.get("comparte_piso", "No")
        alquiler_efectivo = alquiler / 2.0 if comparte == "Si" else alquiler
        esfuerzo = (alquiler_efectivo + deudas) / ingresos

        if p < 0.30 or esfuerzo > 0.70:
            return DecisionNegocio(
                regla_id="R1_RIESGO_EXTREMO",
                nombre_regla="Prevención de Sobreendeudamiento Inasumible",
                prioridad=1,
                decision="DENEGADO_PROTECCION",
                accion_recomendada="Derivar urgentemente al Servicio de Mediación de Alokabide y solicitar plaza en VPO de alquiler social.",
                canal_notificacion="email_asesoramiento_social",
                justificacion_negocio=(
                    f"El esfuerzo financiero individual supera el umbral crítico del 70 % ({esfuerzo*100:.1f} %) o la probabilidad es muy baja ({p:.2f}). "
                    "Conceder la ayuda en el mercado libre provocaría desahucio o insolvencia en menos de 6 meses."
                ),
                probabilidad_modelo=p
            )
        return None

    # -------------------------------------------------------------
    # REGLA 2 (Prioridad 2): Aprobación Directa Exprés
    # -------------------------------------------------------------
    def _regla_2_aprobacion_expres(self, caso: Dict[str, Any], p: float) -> Optional[DecisionNegocio]:
        contrato = caso.get("tipo_contrato", "")
        ahorros = float(caso.get("ahorros_disponibles", 0.0) or 0.0)

        if p >= 0.72 and contrato == "Indefinido" and ahorros >= 1500.0:
            return DecisionNegocio(
                regla_id="R2_APROBACION_EXPRES",
                nombre_regla="Concesión Exprés de Ayuda Gaztelagun",
                prioridad=2,
                decision="CONCESION_EXPRES_300EUR",
                accion_recomendada="Emisión inmediata de la resolución favorable de ayuda Gaztelagun (hasta 300 €/mes) sin requerir documentación adicional.",
                canal_notificacion="sms_y_sede_electronica",
                justificacion_negocio=(
                    f"Solicitud con solvencia contrastada (p={p:.2f}), estabilidad laboral indefinida y colchón de ahorros. "
                    "Se tramita en 24 horas ahorrando un 85 % de coste burocrático de revisión."
                ),
                probabilidad_modelo=p
            )
        return None

    # -------------------------------------------------------------
    # REGLA 3 (Prioridad 3): Viable con Vulnerabilidad de Fianza
    # -------------------------------------------------------------
    def _regla_3_fianza_vulnerable(self, caso: Dict[str, Any], p: float) -> Optional[DecisionNegocio]:
        ahorros = float(caso.get("ahorros_disponibles", 0.0) or 0.0)
        alquiler = float(caso.get("precio_alquiler", 700.0))

        if p >= 0.55 and ahorros < alquiler:
            return DecisionNegocio(
                regla_id="R3_FIANZA_VULNERABLE",
                nombre_regla="Concesión con Microcrédito de Fianza Cero Interés",
                prioridad=3,
                decision="CONCESION_CON_ANTICIPO_FIANZA",
                accion_recomendada="Aprobar ayuda mensual y activar microcrédito sin interés de hasta 1.000 € para depósito de fianza ante Bizilagun.",
                canal_notificacion="email_concesion_condicionada",
                justificacion_negocio=(
                    f"El solicitante es solvente para el pago mensual (p={p:.2f}), pero carece de liquidez inmediata para los 2 meses de fianza legal. "
                    "El microcrédito puente desbloquea la firma del contrato de arrendamiento."
                ),
                probabilidad_modelo=p
            )
        return None

    # -------------------------------------------------------------
    # REGLA 4 (Prioridad 4): Emancipación Colectiva / Piso Compartido
    # -------------------------------------------------------------
    def _regla_4_alquiler_compartido(self, caso: Dict[str, Any], p: float) -> Optional[DecisionNegocio]:
        comparte = caso.get("comparte_piso", "No")

        if p >= 0.50 and comparte == "Si":
            return DecisionNegocio(
                regla_id="R4_PISO_COMPARTIDO",
                nombre_regla="Ayuda a la Co-Emancipación Juvenil",
                prioridad=4,
                decision="CONCESION_ALQUILER_COMPARTIDO",
                accion_recomendada="Aprobar subvención proporcional para vivienda compartida y solicitar identificación de los cotitulares.",
                canal_notificacion="email_tramitacion_compartida",
                justificacion_negocio=(
                    f"Al compartir los gastos de la vivienda, el esfuerzo real individual se reduce a la mitad. "
                    "El modelo confirma viabilidad sostenible (p={p:.2f})."
                ),
                probabilidad_modelo=p
            )
        return None

    # -------------------------------------------------------------
    # REGLA 5 (Prioridad 5): Zona Tensionada con Mercado Inasumible
    # -------------------------------------------------------------
    def _regla_5_mercado_tensionado_vpo(self, caso: Dict[str, Any], p: float) -> Optional[DecisionNegocio]:
        municipio = caso.get("municipio", "")
        if municipio in ["Donostia-San Sebastián", "Bilbao"] and p < 0.60:
            return DecisionNegocio(
                regla_id="R5_ZONA_TENSIONADA_VPO",
                nombre_regla="Derivación a Cupo Joven de VPO en Zonas Tensionadas",
                prioridad=5,
                decision="DERIVACION_CUPO_VPO",
                accion_recomendada="Inscribir de oficio con preferencia en la próxima adjudicación de promociones públicas VPO de Alokabide en el municipio.",
                canal_notificacion="carta_etxebide",
                justificacion_negocio=(
                    f"En {municipio} los alquileres superan la media autonómica. Aun con subsidio, el mercado libre es precario (p={p:.2f}). "
                    "La solución eficiente y duradera es la adjudicación de vivienda de protección pública."
                ),
                probabilidad_modelo=p
            )
        return None

    # -------------------------------------------------------------
    # REGLA 6 (Prioridad 6): Regla de Seguridad / Fallback
    # -------------------------------------------------------------
    def _regla_6_seguridad_fallback(self, caso: Dict[str, Any], p: float) -> DecisionNegocio:
        return DecisionNegocio(
            regla_id="R6_SEGURIDAD_FALLBACK",
            nombre_regla="Regla de Seguridad: Revisión Humana Individualizada",
            prioridad=6,
            decision="REVISION_MANUAL_TECNICO_SOCIAL",
            accion_recomendada="Asignar expediente a un trabajador social comarcal para entrevista presencial y análisis pormenorizado.",
            canal_notificacion="alerta_sistema_gestion_interna",
            justificacion_negocio=(
                f"Caso en franja de incertidumbre estadística (p={p:.2f}) que no cumple condiciones automáticas inequívocas. "
                "La regla de seguridad previene denegaciones indebidas y asegura atención humana a casos singulares."
            ),
            probabilidad_modelo=p
        )
