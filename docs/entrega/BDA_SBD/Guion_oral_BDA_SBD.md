# Guion oral BDA y SBD

## Cómo usamos este guion

A y B son una propuesta para repartir la exposición, no un reparto de autoría. Los dos tenemos que poder explicar todo. La rúbrica pide demostración y justificación de decisiones, pero no fija minutos para este bloque.

Abrimos la presentación y el visor en http://localhost:8502. Las capturas de las diapositivas muestran nuestra aplicación con resultados reales archivados. Si usamos esos resultados, lo decimos. Los comandos de servicios están en la guía común y en el README del ZIP de entrega.

Este guion es material de preparación. No se incluye en el ZIP destinado a la profesora.

## Diapositiva 1 Qué queríamos averiguar

A: «Queríamos ver qué supone alquilar en distintos municipios de Euskadi. Un precio de 900 euros, por sí solo, dice poco: también necesitamos saber con qué ingreso lo estamos comparando. Por eso nuestro trabajo une vivienda y contexto de ingresos».

Seguimos los tres pasos del esquema. La idea que debe quedar clara es que buscamos una comparación que podamos explicar, no una lista de anuncios sin contexto.

## Diapositiva 2 Por qué elegimos estas fuentes

A: «Las estadísticas oficiales nos permiten comparar municipios y ver la evolución. Los anuncios nos cuentan qué se pide y qué características se publican. El salario medio nos da un punto de partida común. Cada fuente aporta una parte de la respuesta».

Señalamos las tres tarjetas. Aclaramos que el salario es autonómico, no el sueldo medio medido de cada municipio.

## Diapositiva 3 Qué representan los recuentos

A: «Tenemos 17 identidades de anuncios y 621 registros de promociones. Esos 638 registros nos sirven para comprobar el transporte, pero no podemos llamarlos 638 pisos diferentes. Además, EMAL resume contratos por municipio y trimestre».

Las tarjetas separan las unidades. Si preguntan de dónde salen los números, abrimos `docs/evidencias_entrega_2026-11-12/anuncios/resumen.json`. Los 17 anuncios no son las muestras de entrenamiento de la IA.

## Diapositiva 4 Por qué guardamos el original

A: «Una web puede cambiar. Por eso guardamos el archivo recibido, la dirección de origen y la fecha. Así, cuando alguien nos pregunta de dónde sale una cifra, podemos volver al archivo que utilizamos».

Mostramos una entrada del manifiesto de `data/capturas_api_rentas/2026-11-12/` y el JSON correspondiente. Si hace falta, distinguimos API, que devuelve datos estructurados, y scraping, que lee la página de anuncios. No recapturamos durante la exposición.

## Diapositiva 5 Para qué sirve cada herramienta

A: «HDFS conserva los archivos; Kafka mueve los registros; MongoDB los guarda para consultarlos. Hemos conectado estas herramientas porque el reto pide demostrar ese recorrido completo».

Recorremos las flechas una vez. Si preguntan por el tamaño, reconocemos que esta muestra no necesita un clúster por volumen. Lo que demostramos es la integración y la posibilidad de revisar cada paso.

## Diapositiva 6 Qué limpiamos y por qué

B: «Antes de comparar, tenemos que evitar problemas sencillos: el mismo dato repetido, municipios escritos de formas distintas o campos vacíos que se interpretan mal. Por ejemplo, no saber si hay ascensor no significa que no lo haya».

La tabla sirve para explicar cada decisión con un ejemplo. Como apoyo técnico tenemos `src/database/data_loader.py` y `src/database/cleaning.py`. Para CRUD podemos enseñar `test_crud_comprobado_real` en `integration_tests/test_mongodb_live.py`.

## Diapositiva 7 Qué preguntas responden las consultas

B: «No hicimos consultas porque sí. Queríamos responder preguntas como qué anuncios cumplen un presupuesto, qué municipios tienen menor renta y cómo cambia el alquiler con el tiempo. MongoDB prepara las respuestas que luego ve el usuario».

Si piden una consulta concreta, abrimos `docs/evidencias_entrega_2026-11-12/anuncios/consultas.json`: el filtro combinado de Bilbao, hasta 2.000 euros y desde 55 metros cuadrados devuelve cuatro resultados. Las condiciones publicadas y los valores desconocidos también se conservan.

## Diapositiva 8 Cómo comprobamos que funciona

B: «Una carga repetida no debería crear otra copia de todo. Comprobamos que después de repetir seguimos teniendo 638 registros. Las tres estadísticas de la API se guardan aparte. También probamos un índice: obtenemos lo mismo mirando cuatro documentos en vez de 638».

Mostramos `anuncios/explain.json` si preguntan. Ambos tiempos fueron 0 ms, así que no afirmamos una mejora temporal medida. La prueba de atomicidad hizo cien operaciones sobre un documento de una copia aislada y terminó en cien; no fueron cien usuarios reales.

## Diapositiva 9 Qué nos dicen los resultados

B: «Con el mismo ingreso de 1.564 euros, Vitoria necesita un 51,06 %, Bilbao un 59,48 % y Donostia un 73,37 % para pagar la renta media entera. En esta comparación Vitoria requiere menos esfuerzo, aunque las tres superan la mitad del ingreso».

Señalamos cada barra. Las rentas son de EMAL, 2024 T4: 798,57, 930,31 y 1.147,53 euros al mes. No son anuncios actuales ni el presupuesto real de todas las personas jóvenes.

## Diapositiva 10 Cómo lo ve una persona

A: «Preparamos un visor para que los resultados no se queden solo en archivos. Aquí elegimos las capitales y vemos la renta, el ingreso de referencia y el esfuerzo. También podemos cambiar municipios, consultar la evolución y descargar la comparación».

La captura muestra esa selección real, con las columnas relevantes visibles. En directo cambiamos un municipio y seguimos una cifra hasta `docs/evidencias_entrega_2026-11-12/municipal/comparativa_municipal.json`, o hasta `data/analisis_municipal/` si acabamos de generar resultados nuevos. Decimos qué caso mostramos.

## Diapositiva 11 Qué no podemos concluir del mapa

A: «Los puntos sitúan promociones del catálogo de Visesa. Que aparezcan en el mapa no significa que estén disponibles para alquilar ahora. Con los anuncios pasa algo parecido: tenemos una muestra pequeña y archivada, no todo el mercado».

Señalamos las tres capitales en la captura y, si hay tiempo, abrimos el mapa y la tabla de anuncios del visor. Mostramos la fecha y las condiciones publicadas. El visor lee resultados; por sí solo no acredita que HDFS, Kafka y MongoDB estén activos en ese momento.

## Diapositiva 12 Con qué nos quedamos

Ambos: «Hemos pasado de fuentes diferentes a una comparación cuyo origen podemos comprobar. La conclusión concreta es que Vitoria exige menos esfuerzo en este escenario. Para orientar mejor a cada hogar ampliaríamos la muestra y usaríamos sus ingresos y circunstancias reales».

Si falla un servicio, usamos los archivos, consultas y capturas conservados indicando su fecha. Esa evidencia permite explicar el trabajo; la ejecución en directo se prepara con los comandos del README de entrega.

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
