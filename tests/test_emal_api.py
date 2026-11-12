"""Fixtures de contrato API; las capturas observadas se verifican por separado."""
import pytest
from scripts.capture_emal_api import parse, verified, ROOT

def test_archivo_observado_api():
    rows=verified(ROOT/'data/capturas_api_rentas/2026-11-12')
    assert len(rows)==3 and {r['codigo_municipio'] for r in rows}=={'01059','20069','48020'}
    assert all(r['tipo_registro']=='estadistica_agregada' for r in rows)

@pytest.mark.parametrize('value',[None,True,-2,0,float('nan')])
def test_no_imputa_importe_api(value):
    with pytest.raises(ValueError):parse({'datos':[{'anyo':2024,'trimestre':4,'impAlqMes':value}]},'48020')

def test_no_sustituye_periodo_por_ultimo_disponible():
    with pytest.raises(ValueError):parse({'datos':[{'anyo':2026,'trimestre':1,'impAlqMes':1000}]},'48020')

def test_rechaza_normalizado_alterado(tmp_path):
    import shutil, json
    source=ROOT/'data/capturas_api_rentas/2026-11-12'
    shutil.copytree(source,tmp_path/'captura')
    target=tmp_path/'captura/rentas_api.json';rows=json.loads(target.read_text())
    rows[0]['renta_media_eur']=1
    target.write_text(json.dumps(rows))
    with pytest.raises(ValueError,match='Normalizados'):verified(tmp_path/'captura')
