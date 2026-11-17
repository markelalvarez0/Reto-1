# Guion oral BDA y SBD

## Cómo usamos este guion

Nos repartimos la exposición como A y B solo para ensayar; no es un reparto de autoría. Ambos tenemos que poder explicar todo. La rúbrica pide demostración y justificación de decisiones, pero no fija minutos. Confirmamos la duración antes del ensayo definitivo.

Abrimos `Presentacion_BDA_SBD.pdf`, el visor de http://localhost:8502 y el repositorio. Llevamos las evidencias del 12 de noviembre descargadas. Si mostramos un archivo histórico lo decimos; no lo presentamos como una ejecución que acaba de ocurrir.

## Diapositivas 1 y 2 La pregunta y las unidades

A: «Queremos comparar referencias de vivienda entre municipios. Para hacerlo necesitamos precios, pero también explicar qué significan frente a unos ingresos. Por eso no basta con enseñar anuncios».

Señalamos el 59,48 % de Bilbao y explicamos que usa un salario común autonómico de 2024. Después distinguimos 17 identidades de anuncio, 621 registros de promociones y estadísticas municipales. Decimos claramente: «638 es un recuento del transporte; no significa 638 pisos distintos».

Pantalla o archivo: `docs/evidencias_entrega_2026-11-12/anuncios/resumen.json` y `data/capturas_oficiales/manifest.json`.

## Diapositiva 3 El origen se puede revisar

A: «Guardamos el archivo tal como llegó, junto con URL, fecha y huella. Así podemos revisar la extracción aunque la web cambie». Explicamos que API devuelve JSON estructurado y scraping lee HTML. Las tres rentas monetarias de la API son estadísticas; los portales aportan anuncios.

Mostramos una entrada del manifiesto de `data/capturas_api_rentas/2026-11-12/` y uno de sus JSON. Después abrimos el HTML archivado de un listado siguiendo la ruta que indica el manifiesto de anuncios. No hacemos otra captura en directo durante la defensa.

## Diapositivas 4 y 5 El recorrido y la recarga

A: «HDFS conserva, Kafka separa el envío de la recepción y MongoDB guarda documentos que después consultamos». Seguimos las flechas en orden. Explicamos que este volumen no necesita un clúster por tamaño, pero el reto pide demostrar esos servicios y su integración.

Enseñamos el informe de transporte conservado en `docs/evidencias_entrega_2026-11-12/`, localizado desde su resumen, y `docs/evidencias_cierre_rubrica_2026-11-12/api-transporte-2.json`. Comprobamos 638 registros en el lote y tres documentos API separados.

Decimos: «Si llega otra vez el mismo registro, actualizamos por fuente e identificador. Guardamos antes de confirmar el offset. La recarga mantiene el recuento». No afirmamos una transacción global ni exactamente una entrega entre todos los servicios.

## Diapositiva 6 Modelado y limpieza

B: «Metemos las características dentro de cada anuncio porque se leen juntas. El municipio se referencia por INE porque lo comparten muchas viviendas». Abrimos `src/database/data_loader.py` y señalamos `caracteristicas`, `codigo_municipio` y el upsert.

Después mostramos las cuatro operaciones en `src/database/cleaning.py`: duplicados, nulos, tipos y derivados. Explicamos los dos rechazos de Abanto y por qué un ascensor sin dato no es falso. Si preguntan por CRUD, abrimos `integration_tests/test_mongodb_live.py`, función `test_crud_comprobado_real`, y explicamos las comprobaciones de insert, find, update y delete.

## Diapositiva 7 Consultas y pipelines

B: «Las consultas parten de una pregunta útil». Leemos un ejemplo de filtros combinados de Bilbao, hasta 2.000 € y desde 55 m². Abrimos `docs/evidencias_entrega_2026-11-12/anuncios/consultas.json` y comprobamos cuatro resultados.

En `src/database/queries.py` señalamos habitaciones como campo anidado y condiciones temporales como array. No ocultamos los ceros de ascensor o Gaztelagun. En `src/database/aggregations.py` recorremos los tres pipelines: filtrar, agrupar, unir y preparar salidas. Explicamos que el salario de los anuncios queda nulo si no hay uno medido y comparable.

## Diapositiva 8 Índice y atomicidad

B: «Un índice evita recorrer toda la colección para esta consulta. Lo que hemos comprobado es que se examinan 4 documentos en vez de 638». Abrimos el explain y señalamos stage, totalDocsExamined y nReturned. Leemos también los dos tiempos 0 ms; no decimos que tarda un porcentaje menos.

En `src/database/consistency.py` mostramos `$inc` y `$set` sobre un documento. «Cien operaciones concurrentes dejan contador cien en una copia aislada. No son cien usuarios reales. Como solo cambia ese documento, no necesitamos una transacción entre colecciones».

## Diapositiva 9 Qué municipios comparamos

B: leemos Vitoria 798,57 €, Bilbao 930,31 € y Donostia 1.147,53 €, todos de 2024 T4. Explicamos que, con el mismo salario 1.564 €, los esfuerzos son 51,06 %, 59,48 % y 73,37 %.

«Vitoria requiere menos esfuerzo en este escenario, pero las tres superan el 30 %. Eso no dice quién puede emanciparse realmente». Mostramos comparación, evolución y tabla del visor. Indicamos que la cobertura del trimestre es 18 municipios y la serie completa 19.

## Diapositiva 10 Demostración

A: en el visor seleccionamos las tres capitales. Cambiamos selección y mostramos que tabla y gráficos responden. Abrimos la serie y el mapa de promociones. Después mostramos la muestra archivada, su tabla de condiciones y la descarga CSV.

Seguimos una cifra de la tabla hasta `docs/evidencias_entrega_2026-11-12/municipal/comparativa_municipal.json` si usamos evidencias archivadas, o `data/analisis_municipal/comparativa_municipal.json` si acabamos de generarla con MongoDB. Decimos cuál de los dos casos mostramos.

Para demostrar servicios reales necesitamos HDFS, Kafka y MongoDB accesibles y los comandos de la guía común preparados. El visor por sí solo lee resultados y no acredita que esos servicios estén funcionando ahora.

## Diapositivas 11 y 12 Cierre

Ambos: «Hemos podido conservar el origen y justificar una comparación concreta. Nos falta ampliar la muestra y contar con información de ingresos más ajustada a cada hogar para sacar conclusiones más amplias». Señalamos las carpetas que acompañan a los PDF y la revisión de rúbricas.

Si falla la red o un servicio, mostramos el resumen, XML, explain y capturas conservadas con su fecha. Eso permite explicar el trabajo, aunque no sustituye una ejecución en directo si el profesorado la exige.

## Preguntas para ensayar

| Pregunta probable | Respuesta que debemos entender | Archivo que mostramos |
|---|---|---|
| Por qué no guardarlo todo solo en MongoDB | HDFS conserva archivos, Kafka transporta eventos y MongoDB consulta documentos; demostramos el recorrido solicitado | scripts/run_pipeline.py |
| Por qué no son 638 viviendas | Sumamos registros de dos unidades; incluso puede haber referencias duplicadas entre fuentes | RESULTADOS_ANUNCIOS.md |
| Por qué no rellenamos salarios municipales | Solo tenemos un contexto autonómico verificado; rellenarlos inventaría una medida local | src/municipal_analysis.py |
| El índice acelera la consulta | Reduce documentos examinados; con ambos tiempos 0 ms no cuantificamos mejora temporal | anuncios/explain.json |
| Qué hace el lookup | Une registros por una clave común, INE, conservando ausencia cuando no hay contexto | src/database/aggregations.py |
| Necesitáis una transacción | El contador y fecha cambian en un documento atómico; otra operación entre colecciones podría necesitarla | src/database/consistency.py |
| Cuál es el mejor municipio | Vitoria tiene menor renta entre las tres capitales de 2024 T4; no basta para afirmar que es mejor para todos | municipal/comparativa_municipal.json |
| Cuándo un cero de consulta es informativo | Cuando la fuente no acredita el campo exigido; ascensor desconocido no significa ausencia real | anuncios/consultas.json |

Las rutas abreviadas de la tabla se resuelven desde `docs/evidencias_entrega_2026-11-12/` cuando empiezan por anuncios o municipal, y desde `docs/` en RESULTADOS_ANUNCIOS.md.
