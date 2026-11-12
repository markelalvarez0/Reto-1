"""API JSON pública del visor EMAL: originales separados del modelo sellado."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import requests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
API = 'https://eremutentsionatua.euskadi.eus/ad23aConsultaWar/consulta/emal'
VIEWER = 'https://eremutentsionatua.euskadi.eus/webzte00-municipios/es/ad23aConsultaWar/emal?locale=es'
MUNICIPALITIES = {'01059':'Vitoria-Gasteiz', '20069':'Donostia-San Sebastián', '48020':'Bilbao'}


def parse(payload, code):
    """Selecciona 2024 T4: vivienda habitual colectiva y nuevos contratos trimestrales."""
    if code not in MUNICIPALITIES or not isinstance(payload.get('datos'), list):
        raise ValueError('Contrato o municipio no reconocido')
    rows = [r for r in payload['datos'] if r.get('anyo') == 2024 and r.get('trimestre') == 4]
    if len(rows) != 1:
        raise ValueError('Se requiere exactamente una observacion 2024 T4')
    row = rows[0]; price = row.get('impAlqMes')
    if isinstance(price, bool) or not isinstance(price, (int,float)) or not math.isfinite(price) or price <= 0:
        raise ValueError('Renta mensual no publicada o invalida')
    return {'codigo_municipio':code, 'municipio':MUNICIPALITIES[code], 'anio':2024, 'trimestre':4,
            'renta_media_eur':price, 'numero_contratos':row.get('numVivAlq'),
            'contratos_con_importe':row.get('numImpAlqMes'),
            'unidad':'municipio/trimestre; EUR/mes; nuevos contratos de vivienda habitual colectiva',
            'fuente':'API_JSON_visor_EMAL', 'tipo_registro':'estadistica_agregada'}


def capture(folder):
    """Captura acotada, sin reintentos ni sustitución del Excel/modelo conservados."""
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    sources=[];rows=[]
    def get(url, name, params=None):
        r=requests.get(url,params=params,headers={'Accept':'application/json' if params else 'text/html',
                       'User-Agent':'Reto1AcademicBot/1.0'},timeout=20)
        (folder/name).write_bytes(r.content)
        meta={'archivo':name,'url':r.url,'http_status':r.status_code,'bytes':len(r.content),
              'sha256':hashlib.sha256(r.content).hexdigest(),'fecha_utc':datetime.now(timezone.utc).isoformat(),
              'parametros':params,'tls_verificado':True}
        sources.append(meta);(folder/'manifest.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
        r.raise_for_status();return r,meta
    get(VIEWER,'visor.html')
    for code in MUNICIPALITIES:
        time.sleep(1.5)
        response,meta=get(API,code+'.json',{'ambito':4,'tipoDatoContratos':4,'tipoContrato':1,'tipoHueco':0,
                                        'idProvincia':code[:2],'idMunicipio':code[2:]})
        rows.append({**parse(response.json(),code),'procedencia':meta})
    (folder/'rentas_api.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    return rows


def verified(folder):
    """Reinterpreta los bytes de API antes de transportar: falla ante alteraciones."""
    folder=Path(folder);entries=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if {e['archivo'] for e in entries} != {'visor.html',*(c+'.json' for c in MUNICIPALITIES)} or len(entries)!=4:
        raise ValueError('Manifiesto incompleto')
    rows=[]
    for e in entries:
        raw=(folder/e['archivo']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=e['sha256'] or len(raw)!=e['bytes'] or e['http_status']!=200:
            raise ValueError('Original API alterado')
        if e['archivo'].endswith('.json'):
            code=e['archivo'][:5]
            expected={'ambito':4,'tipoDatoContratos':4,'tipoContrato':1,'tipoHueco':0,'idProvincia':code[:2],'idMunicipio':code[2:]}
            if e['parametros']!=expected or not e['url'].startswith(API+'?'):
                raise ValueError('Filtros API distintos de los declarados')
            rows.append({**parse(json.loads(raw),code),'procedencia':e})
    if rows!=json.loads((folder/'rentas_api.json').read_text(encoding='utf-8')):
        raise ValueError('Normalizados distintos de los originales')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();print(json.dumps(capture(a.output_dir),ensure_ascii=False,indent=2))
