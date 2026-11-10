"""Resultados municipales observados, calculados previamente con MongoDB."""
import hashlib
import json
import os
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
folder = Path(os.getenv('RETO1_ANALYSIS_DIR', str(ROOT / 'data/analisis_municipal')))
st.set_page_config(page_title='Alquileres y territorio · Euskadi', layout='wide')
st.title('Alquileres y territorio en Euskadi')
st.caption('Comparación de rentas medias municipales y un escenario común de ingresos.')
try:
    files = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    for item in files:
        path = folder / item['archivo']
        if Path(item['archivo']).name != item['archivo'] or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('La integridad de los resultados no coincide: ' + item['archivo'])
    def read(name):
        return json.loads((folder / (name + '.json')).read_text(encoding='utf-8'))
    meta = read('metadatos')
    comparison = pd.DataFrame(read('comparativa_municipal'))
except (OSError, ValueError, KeyError) as exc:
    st.error('Resultados no disponibles o no verificables: ' + str(exc))
    st.code('python scripts/analyze_municipal.py')
    st.stop()
st.subheader(f"Rentas observadas · {meta['anio']} T{meta['trimestre']}")
st.info(f"Escenario: una persona cobra el salario neto medio autonómico OVJ de {meta['salario']['valor']:,.0f} €/mes en 2024. No es el salario de cada municipio ni una evaluación individual.")
if meta['motor'] != 'MongoDB':
    st.warning('Resultados calculados con una base simulada. Los originales son observados; no acredita ejecución en MongoDB real.')
names = comparison.municipio.tolist()
chosen = st.multiselect('Municipios que quieres comparar', names, default=names)
table = comparison.loc[comparison.municipio.isin(chosen)]
st.dataframe(table, hide_index=True)
st.bar_chart(table.set_index('municipio')[['renta_media_eur']])
st.download_button('Descargar la comparación (CSV)', table.to_csv(index=False).encode('utf-8-sig'), 'comparativa_municipal.csv', 'text/csv')
if not table.empty:
    first, last = table.iloc[0], table.iloc[-1]
    st.write(f"En esta selección, {first.municipio} tiene la menor renta media ({first.renta_media_eur:.2f} €/mes) y {last.municipio} la mayor ({last.renta_media_eur:.2f} €/mes). Son contratos observados en el trimestre, no precios de anuncios actuales.")
    st.write(f"Con el salario de referencia común, los esfuerzos correspondientes son {first.esfuerzo_escenario_pct:.1f}% y {last.esfuerzo_escenario_pct:.1f}%. El coste de acceso no queda explicado solo por la renta: faltan los ingresos y circunstancias reales de cada hogar.")
st.subheader('Evolución de la renta mensual')
series = pd.DataFrame(read('serie_trimestral'))
series = series.loc[series.municipio.isin(chosen)]
series['trimestre_observado'] = series.anio.astype(str) + ' T' + series.trimestre.astype(str)
st.line_chart(series.pivot(index='trimestre_observado', columns='municipio', values='renta_media_eur'))
st.subheader('Promociones del catálogo Visesa')
st.caption('Coordenadas publicadas por Visesa. La presencia en el catálogo no acredita disponibilidad. El mapa usa cartografía externa.')
points = pd.DataFrame(read('mapa_promociones'))
if not points.empty:
    points = points.loc[points.codigo_municipio.isin(table.codigo_municipio)]
    if not points.empty:
        st.map(points[['lat', 'lon']])
    st.dataframe(points, hide_index=True)
st.subheader('Resumen territorial')
st.dataframe(pd.DataFrame(read('resumen_territorial')), hide_index=True)
with st.expander('Fuentes, unidades y límites'):
    for note in meta['limites']:
        st.write(note)
    st.json(meta['fuentes'])
