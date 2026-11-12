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

st.divider()
st.header('Muestra archivada de anuncios de alquiler')
sample_folder = Path(os.getenv('RETO1_RENTALS_DIR', str(ROOT / 'docs/evidencias_entrega_2026-11-12/anuncios')))
try:
    sample_manifest = json.loads((sample_folder / 'manifest.json').read_text(encoding='utf-8'))
    entries = sample_manifest['resultados']
    if {item['archivo'] for item in entries} != {'resumen.json', 'consultas.json', 'explain.json', 'anuncios.json'}:
        raise ValueError('El manifiesto no contiene los resultados esperados')
    for item in entries:
        name = item['archivo']
        path = sample_folder / name
        if Path(name).name != name or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Resultado de anuncios alterado: ' + name)
    sample = json.loads((sample_folder / 'resumen.json').read_text(encoding='utf-8'))
    ads = pd.DataFrame(json.loads((sample_folder / 'anuncios.json').read_text(encoding='utf-8')))
    if sample['motor'] != 'MongoDB':
        raise ValueError('La muestra no acredita MongoDB real')
except FileNotFoundError:
    st.info('La muestra de anuncios aún no está disponible en esta copia.')
except (OSError, ValueError, KeyError) as exc:
    st.error('No se puede verificar la muestra de anuncios: ' + str(exc))
else:
    st.caption(f"Captura archivada del 12 de noviembre de 2026 · {sample['anuncios']} identidades de anuncio en dos portales. No es una búsqueda en tiempo real.")
    st.warning('La muestra mezcla modalidades de alquiler y no acredita disponibilidad. Sus precios pedidos no son rentas de contratos EMAL ni una estimación representativa del mercado.')
    comparison_ads = pd.DataFrame(sample['comparativa'])
    st.dataframe(comparison_ads, hide_index=True)
    st.bar_chart(comparison_ads.set_index('municipio')[['precio_medio', 'precio_minimo', 'precio_maximo']], stack=False)
    st.scatter_chart(ads, x='superficie_m2', y='precio', color='fuente')
    ads['condiciones_publicadas'] = ads.procedencia.map(lambda p: ', '.join(p.get('condiciones_publicadas', [])) or 'No determinadas en el listado')
    st.dataframe(ads[['fuente', 'municipio', 'titulo', 'precio', 'superficie_m2', 'condiciones_publicadas', 'url']], hide_index=True)
    st.caption('Las señales de temporalidad o destinatarios proceden del texto publicado. Su ausencia no demuestra que el alquiler admita uso habitual.')
    st.download_button('Descargar la muestra (CSV)', ads.drop(columns=['procedencia']).to_csv(index=False).encode('utf-8-sig'), 'muestra_anuncios.csv', 'text/csv')
    with st.expander('Cobertura y validación de la muestra'):
        st.json({k: sample[k] for k in ('por_fuente', 'nulos', 'reentrega', 'atomicidad', 'consultas')})
        for note in sample['limites']:
            st.write(note)
