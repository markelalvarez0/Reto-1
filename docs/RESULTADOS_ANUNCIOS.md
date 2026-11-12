# Muestra de anuncios observada el 12 de noviembre de 2026

Se han conservado 17 identidades de anuncio: 9 de Habitaclia y 8 de Pisos.com.
La captura fue acotada a tres candidatos interpretables por listado y portal;
Pisos.com publicó solo dos interpretables en Vitoria. No es una muestra aleatoria,
un censo, una comprobación de disponibilidad ni 17 viviendas necesariamente distintas.
Los anuncios de portales diferentes pueden corresponder al mismo inmueble.

## Adquisición y comprobación

En este entorno la política de red está aplicada en modo sin lista restrictiva.
Los dos robots y los avisos legales se pudieron consultar con HTTPS verificado.
Las rutas de listados están permitidas para `Reto1AcademicBot/1.0`; se respetaron
robots, pausas y redirecciones del mismo dominio. Los avisos reservan derechos
sobre los contenidos; robots no es una licencia. El uso es académico, sin
explotación comercial, contactos con anunciantes ni seguimiento automatizado.

La primera ejecución conservó un fallo interpretable: URLs antiguas 404 y
selectores desactualizados. Después se corrigieron las rutas de Habitaclia y
ambos parsers usando el HTML recibido. El lote final es
`data/capturas_anuncios/2026-11-12/`; sus 22 ficheros incluyen informe, anuncios,
robots, listados y metadatos. `data/capturas_anuncios/manifest.json` sella sus
bytes. `.gitattributes` impide normalizarlos en Windows.

La comprobación offline vuelve a extraer los campos desde el HTML archivado y
contrasta identidad, URL, precio, municipio INE, superficie, habitaciones y baños
con los documentos de MongoDB. No requiere repetir peticiones a los portales.
El detalle de tarjetas no interpretables y del límite de selección consta en
`evidencias_entrega_2026-11-12/anuncios/resumen.json`: no se confunden los
candidatos no seleccionados por el límite con registros rechazados en transporte.

## Indicadores descriptivos de la muestra

| Municipio | Anuncios | Precio medio pedido €/mes | Mínimo | Máximo | Superficie media m² | Media de €/m² |
|---|---:|---:|---:|---:|---:|---:|
| Vitoria-Gasteiz | 5 | 1.604,40 | 750 | 3.150 | 95,80 | 16,60 |
| Donostia-San Sebastián | 6 | 2.108,33 | 1.350 | 2.500 | 86,00 | 25,70 |
| Bilbao | 6 | 2.316,67 | 1.200 | 4.500 | 105,50 | 21,36 |

El precio medio pedido de esta selección es mayor en Bilbao; la media de €/m²,
mayor en Donostia. Son composiciones diferentes de viviendas y modalidades:
estas diferencias no prueban un orden general de precios entre municipios.
La media de €/m² se calcula sobre las razones de cada anuncio, no dividiendo
las dos medias de la tabla. Los precios están publicados en mensualidades.

Se detectan tres anuncios con señales textuales de temporalidad y dos dirigidos
a empresas; las categorías pueden solaparse. La ausencia de esas palabras no
acredita que un alquiler admita vivienda habitual. No hay nulos de precio,
superficie, habitaciones o baños entre los seleccionados. Las nueve tarjetas de
Habitaclia carecen de descripción; se conserva nula. Ascensor permanece nulo en
los campos normalizados. No se han inventado salarios municipales: esfuerzo y
asequibilidad personal siguen nulos. El salario regional OVJ de 2024 se utiliza
solo en el análisis EMAL de ese mismo año, no para estos anuncios de 2026.

## Transporte, consultas y atomicidad

HDFS conserva y recupera idénticos 31 archivos por carga: originales oficiales,
HTML/robots, sus metadatos y derivados. Kafka confirma 638 mensajes y MongoDB
persiste 638 registros: 621 promociones (215 Visesa y 406 Etxebide) y 17 anuncios.
Los dos rechazos originales de Abanto se producen en la preparación oficial;
los 638 aceptados no producen nuevos rechazos de transporte.
La reentrega de los 17 anuncios mantiene 638 documentos, con cero duplicados
nuevos. También se ha repetido el recorrido completo en la misma base.
Las cinco vistas municipales usan su propio transporte y colección.

Las consultas actuales excluyen promociones y simulaciones. Resultados reales:

| Consulta | Resultados | Interpretación |
|---|---:|---|
| Anuncios de alquiler de Bilbao | 6 | Identidades observadas con precio positivo |
| Precio hasta 750 €/mes | 1 | Umbral analítico, no solvencia ni derecho a ayuda |
| Bilbao, hasta 2.000 €/mes y desde 55 m² | 4 | Filtros combinados sobre la muestra |
| Hasta 10 anuncios con al menos dos habitaciones | 10 | Campo anidado publicado, sin exigir ascensor desconocido |
| Señal temporal en array de condiciones | 3 | Filtrado de una señal textual publicada, no categoría jurídica |
| Dos habitaciones y ascensor acreditado en campo | 0 | Ascensor no se ha extraído a un campo observado |
| Municipios con Gaztelagun publicado en array | 0 | Los catálogos utilizados no aportan ese array; no se rellena |

Se conservaron los tres pipelines: estadísticas por municipio, cruce territorial
con esfuerzo nulo y `$facet` de distribuciones/top. La colección de anuncios
permanece separada por `tipo_registro`; las vistas EMAL no se tratan como anuncios.

`explain` de la consulta Bilbao/alquiler/precio hasta 2.000 examina 638 documentos
con `COLLSCAN` y 4 con `IXSCAN`; ambos devuelven 4. Ambos tiempos medidos son 0 ms:
la reducción de documentos examinados no permite cuantificar aceleración temporal.
No se eliminaron índices ajenos.

La demostración de atomicidad ejecutó 100 incrementos concurrentes sobre una
copia aislada de un anuncio observado y obtuvo contador 100. Es una prueba del
incremento atómico de un documento, no demanda real ni una transacción global.
No se modificó el contador de la colección original.

## Reproducción sin recapturar ni entrenar

Con HDFS, Kafka y MongoDB reales preparados y `MONGO_URI` configurada:

```bash
uv sync --locked --extra dev
uv run --no-sync python scripts/audit_project.py
python -c "import shutil; shutil.copytree('data/capturas_anuncios/2026-11-12', 'data/scraping/reproduccion')"
uv run --no-sync python scripts/run_pipeline.py --snapshot-dir data/capturas_oficiales --raw-dir data/scraping/reproduccion --output-dir data/bda/con_scraping --db-name reto1_muestra
uv run --no-sync python scripts/analyze_rental_sample.py --capture-dir data/capturas_anuncios/2026-11-12 --pipeline-dir data/bda/con_scraping --db-name reto1_muestra
uv run --no-sync python main.py --subject bda_sbd --visual
```

La copia de trabajo recibe los preparados oficiales; el archivo de entrega conserva
sus bytes. El visor abre los resultados archivados verificados;
`RETO1_RENTALS_DIR=data/analisis_anuncios` permite abrir los recién regenerados.
Ninguna de estas órdenes entrena, selecciona modelos ni reevalúa el test conservado.
