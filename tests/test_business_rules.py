from datetime import date
from uuid import uuid4
import json
import pytest
from src.reglas import MotorReglasVivienda, DECISIONES
from src.n8n import N8NWebhookClient
from scripts.action_server import ACTIONS, persist_action


def caso(**changes):
    return {'edad':25,'ingresos_mensuales':2000,'ingresos_anuales_computables':25000,
            'precio_alquiler':700,'renta_total_vivienda':700,'deudas_mensuales':0,
            'ahorros_disponibles':2000,'coste_entrada':1000,'municipio':'Bilbao','modelo_en_cobertura':True,
            **{name:True for name in ('residencia_6_meses','vivienda_habitual_libre','contrato_titular','pagos_bancarios',
                                     'sin_propiedad_disponible','sin_parentesco','sin_incompatibilidades')}, **changes}


def evaluate(**changes):
    return MotorReglasVivienda().evaluar(caso(**changes), renta_estimada=700, fecha=date(2026,11,10))


def test_prioridades_y_seguridad():
    rules=MotorReglasVivienda().reglas
    assert len(rules)>=6 and len({r.id for r in rules})==len(rules)
    assert evaluate(ingresos_mensuales=float('nan')).decision=='REVISION_DATOS'
    assert evaluate(modelo_en_cobertura=False).decision=='REVISION_DATOS'
    assert evaluate(ingresos_mensuales=700).decision=='ORIENTACION_PRIORITARIA'


@pytest.mark.parametrize('amount,expected',[(3000,'REVISION_REQUISITOS'),(3000.01,'CONSULTAR_GAZTELAGUN'),(30000,'CONSULTAR_GAZTELAGUN'),(30000.01,'REVISION_REQUISITOS')])
def test_limite_anual_inclusivo(amount,expected):
    assert evaluate(ingresos_anuales_computables=amount).decision==expected


def test_no_convierte_neto_mensual_en_ingreso_fiscal():
    assert evaluate(ingresos_mensuales=2200,ingresos_anuales_computables=24000).decision=='CONSULTAR_GAZTELAGUN'
    assert evaluate(ingresos_anuales_computables=None).decision=='REVISION_NORMATIVA'


def test_renta_superior_requiere_revisar_excepcion():
    assert evaluate(renta_total_vivienda=950).decision=='REVISION_NORMATIVA'
    assert evaluate(contrato_compartido=True).decision=='REVISION_NORMATIVA'


def test_fechas_fuera_de_convocatoria_no_reutilizan_reglas():
    result=MotorReglasVivienda().evaluar(caso(),fecha=date(2027,1,1))
    assert result.decision=='REVISION_NORMATIVA'


def test_recomendacion_nunca_es_resolucion():
    result=evaluate()
    assert result.decision=='CONSULTAR_GAZTELAGUN' and result.ayuda_teorica_max==300
    assert 'No concede' in result.aviso
    assert evaluate(ahorros_disponibles=100).decision=='PLANIFICAR_ENTRADA'
    assert evaluate(precio_alquiler=500).decision=='INFORMACION_GENERAL'
    assert evaluate(ingresos_mensuales=1500).decision=='BUSCAR_ALTERNATIVAS'


def test_n8n_error_red_no_es_exito(monkeypatch):
    import requests
    def fail(*args,**kwargs): raise requests.ConnectionError('no servidor')
    monkeypatch.setattr(requests,'post',fail)
    result=N8NWebhookClient().disparar_accion({'decision':'REVISION_DATOS'},{'nombre':'Privado','salario':2000})
    assert result['estado']=='ERROR_N8N' and 'nombre' not in str(result['payload_enviado'])


def test_payload_desconocido_se_rechaza():
    with pytest.raises(ValueError): N8NWebhookClient(demo_mode=True).disparar_accion({'decision':'CONCESION'})


def test_acciones_distintas_idempotentes_y_sin_pii(tmp_path):
    for decision,(action,_) in ACTIONS.items():
        payload={'event_id':str(uuid4()),'decision':decision}
        first=persist_action(tmp_path,action,payload)
        assert first==persist_action(tmp_path,action,payload)
        assert first['resolucion_administrativa'] is False
    assert len(list(tmp_path.glob('*.json')))==len(DECISIONES)
    with pytest.raises(ValueError): persist_action(tmp_path,'revision_datos',{'event_id':str(uuid4()),'decision':'REVISION_DATOS','nombre':'No'})
