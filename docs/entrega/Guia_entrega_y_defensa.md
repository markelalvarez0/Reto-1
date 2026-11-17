# Guía de entrega y defensa

## 1 Qué presentamos a la profesora

Entregamos dos bloques del mismo proyecto: BDA y SBD, y SAA, PIA y MIA. Las memorias explican el trabajo por sí solas; las presentaciones sirven para contarlo en voz alta. Los guiones y esta guía ayudan a prepararnos. El código, los datos y el modelo se conservan en sus formatos funcionales: un PDF no sustituye una base de datos ni un notebook.

Los siete PDF principales vigentes están en `docs/entrega/`. La revisión adicional de las rúbricas está en `Revision_rubricas.pdf`. Los documentos anteriores se conservan como históricos. Los cuatro informes antiguos de raíz y carpetas académicas tienen contenido idéntico y SHA-256 `629956f7a3fa836d0fb12d42d4e7e05d1f3e264ffeaac86da242529371f99e5b`. Ya no son la entrada principal para esta entrega.

## 2 Lista exacta de archivos PDF

| Bloque | Archivo desde docs/entrega/ | Para qué sirve | Carácter |
|---|---|---|---|
| BDA y SBD | BDA_SBD/Documentacion_BDA_SBD.pdf | Arquitectura, decisiones, resultados y límites | Informe y arquitectura confirmados en rúbrica; formato PDF solicitado por el equipo |
| BDA y SBD | BDA_SBD/Presentacion_BDA_SBD.pdf | Apoyo a la demostración | Presentación preparada para la defensa; demostración confirmada |
| BDA y SBD | BDA_SBD/Guion_oral_BDA_SBD.pdf | Qué decir y qué abrir en cada diapositiva | Estudio, solicitado por el equipo |
| SAA PIA MIA | SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.pdf | Explicación de datos, modelos, app y acción | Memoria PDF solicitada por el equipo; no reemplaza README y notebooks exigidos |
| SAA PIA MIA | SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.pdf | Exposición de 15 minutos por pareja | Duración y defensa confirmadas; soporte PDF preparado |
| SAA PIA MIA | SAA_PIA_MIA/Guion_oral_SAA_PIA_MIA.pdf | Ensayo con tiempos y preguntas | Estudio, solicitado por el equipo |
| Común | Guia_entrega_y_defensa.pdf | Lista de entrega, estudio y demo | Apoyo solicitado por el equipo |
| Común | Revision_rubricas.pdf | Relación de criterios con evidencia | Comprobación adicional; no es un certificado de nota |

Las fuentes Markdown editables tienen el mismo nombre y carpeta. `scripts/build_academic_docs.py` genera los PDF desde esas fuentes. Sus dependencias documentales van aparte en `docs/entrega/requirements-documentacion.txt`; no cambiamos las dependencias del modelo.

## 3 Qué más tiene que acompañar a los PDF

| Bloque o asignatura | Archivo o carpeta desde la raíz | Para qué sirve | Confirmado o recomendado |
|---|---|---|---|
| Común | README.md y README de ambos bloques | Entrada, instrucciones y resultados | README confirmado para IA; organización recomendada para entrega común |
| Común | main.py, src/, scripts/, app/ | Código Python organizado y funcional | Confirmado en ambos enunciados |
| Común | requirements.txt | Dependencias | Confirmado en PIA |
| Común | pyproject.toml, uv.lock, requirements-ci.txt | Instalación reproducible y comprobaciones | Soporte técnico recomendado; uv es el camino preparado |
| BDA | data/capturas_oficiales/ | Seis originales y manifiesto | Datos y originales en HDFS confirmados |
| BDA | data/capturas_anuncios/ y data/capturas_api_rentas/ | HTML, robots, JSON API y procedencia | Evidencia de API y scraping confirmados |
| BDA | HDFS real, rutas /data/reto1/ y listado de sus archivos | Mostrar almacenamiento y recuperación | Datos almacenados en HDFS confirmados; modo de acceso por acordar |
| SBD | MongoDB real con colecciones y resultados | Datos, CRUD, agregaciones, índices y consistencia | Base de datos confirmada; acceso o exportación por acordar |
| BDA y SBD | docs/evidencias_entrega_2026-11-12/ | Transporte, consultas, explain y vistas | Respaldo recomendado de la demostración exigida |
| BDA y SBD | docs/evidencias_cierre_rubrica_2026-11-12/ | API monetaria y cierre real | Evidencia adicional del recorrido |
| SAA | notebooks/ y entrega_ml/notebooks_ejecutados/ | EDA, modelos y SHAP con salidas conservadas | Notebooks y análisis confirmados; salidas ayudan a revisar sin ejecutar |
| SAA y PIA | entrega_ml/data/ | train.csv, val.csv, test.csv y procedencia | Datos y particiones confirmados; estas rutas sustituyen la estructura de ejemplo |
| SAA y PIA | entrega_ml/models/ | Pipeline joblib y selección cerrada | Mejor modelo guardado confirmado |
| SAA y PIA | entrega_ml/resultados/ | Tabla MLflow, EDA, SHAP, SMOTE y test | Resultados y métricas confirmados |
| PIA | entrega_ml/mlruns/ y docs/evidencias_ml/capturas/ | Registros y capturas MLflow y app | Registro y captura confirmados |
| SAA y PIA | docs/TEST_FINAL_EMAL.json y docs/evidencias_ml/ | Evaluación única y manifiesto de artefactos | Test una vez confirmado; huellas son protección técnica |
| MIA | src/reglas.py, src/n8n.py | Prioridad, motivo, seguridad y webhook | Confirmado |
| MIA | n8n/flujo.json y n8n/compose.yml | Workflow importable y servicios locales | Flujo por decisión confirmado; Compose es soporte local |
| MIA | data/acciones_n8n/ si se genera una demo | Ficha local de un caso ficticio | Evidencia recomendada, generada fuera de Git |
| Común | tests/, integration_tests/ y .github/workflows/ | Verificación y ejecuciones | Evidencia técnica de apoyo |

La estructura del enunciado IA es básica y no coincide literalmente con todas nuestras rutas. Conservamos un único repositorio y explicamos la correspondencia: `data/raw` pasa a capturas originales, particiones a `entrega_ml/data`, modelo a `entrega_ml/models` y resultados a `entrega_ml/resultados`. Las carpetas académicas comparten recursos de raíz; copiarlas solas puede dejar fuera archivos necesarios.

## 4 Si piden enlace ZIP o buzones separados

Si piden enlace, enviamos el repositorio y enlaces directos a los dos PDF del bloque correspondiente. Indicamos rama y commit entregados. No basta enlazar la presentación si también necesitan revisar código y datos.

Si piden ZIP, descargamos el repositorio del commit publicado y comprobamos que incluye `entrega_ml/`, originales y documentación. Adjuntamos por separado las exportaciones de servicios que acuerden, porque Git no contiene un clúster HDFS ni una instancia MongoDB en marcha. No incluimos `.venv`, credenciales o datos personales de ensayos.

Si hay buzones separados para SAA, PIA y MIA, podemos referenciar el mismo repositorio y memoria IA señalando sus apartados: SAA, datos y modelos; PIA, pipeline, código, MLflow y app; MIA, necesidad, reglas y acción. Para BDA, captura, HDFS y Kafka; para SBD, MongoDB y análisis. No inventamos que el aula virtual acepte enlaces o el mismo ZIP en todos los buzones: eso se confirma con el profesorado.

## 5 Qué se guarda en Git y qué se genera en el equipo

Git incluye código, dependencias, originales archivados, modelo, particiones, resultados ML, notebooks ejecutados, workflow, evidencias históricas y estos PDF. Podemos comprobarlo con `git ls-files`.

`.gitignore` excluye `data/analisis_municipal/`, `data/analisis_anuncios/`, `data/bda/`, `data/acciones_n8n/`, `data/scraping/`, almacenamiento HDFS emulado, informes regenerados y entorno virtual. También hay un volumen Docker local para n8n. No prometemos que todo eso aparezca al clonar.

El visor territorial espera resultados municipales verificables. En un clon nuevo hay que generarlos con MongoDB o seleccionar explícitamente las evidencias conservadas. Las fichas de n8n se crean al ejecutar la acción. `localhost` apunta a la máquina desde la que se abre el navegador y no es una URL pública para la profesora.

## 6 Descargar instalar y comprobar

Con Git, Python 3.12 y uv disponibles:

```bash
git clone https://github.com/markelalvarez0/Reto-1.git
cd Reto-1
uv sync --locked --extra dev
uv run --no-sync python main.py --audit --json
uv run --no-sync python scripts/sync_sources.py --check
uv run --no-sync python -m pytest tests/ -q
```

La auditoría comprueba originales, artefactos, test sellado, anuncios y copias académicas sin entrenar. Los tests incluyen miniensayos con fixtures; no reentrenan el modelo entregado ni repiten su holdout. Para abrir los resultados no ejecutamos `scripts/train_official.py` ni las celdas históricas de entrenamiento.

Si necesitamos regenerar solo la documentación, instalamos sus dependencias en otro entorno y ejecutamos el generador desde la raíz:

```bash
uv venv .venv-docs
uv pip install --python .venv-docs/bin/python -r docs/entrega/requirements-documentacion.txt
.venv-docs/bin/python scripts/build_academic_docs.py
```

En Windows el intérprete documental está en `.venv-docs/Scripts/python.exe`. Esta dependencia adicional sirve para maquetar; no cambia `uv.lock` ni el modelo.

## 7 Demostración BDA y SBD

Para generar resultados municipales nuevos necesitamos MongoDB accesible. Si el servidor no es el predeterminado configuramos `MONGO_URI` en el entorno. Desde la raíz:

```bash
uv run --no-sync python scripts/analyze_municipal.py
uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

Abrimos http://localhost:8502. Mostramos comparación de tres capitales, evolución, tabla, mapa y anuncios archivados. Leemos fecha, unidad, salario y límites. El visor muestra los resultados exportados; abrirlo no vuelve a conectar por sí solo todo el transporte.

Para demostrar el recorrido completo hacen falta HDFS con WebHDFS, Kafka y MongoDB reales. Las variables preparadas son `HDFS_NAMENODE_HOST`, `HDFS_NAMENODE_PORT`, `HDFS_USER`, `KAFKA_BOOTSTRAP_SERVERS`, `MONGO_URI` y las opciones de base del script. Las plantillas de servicios y versiones de referencia están en `.github/workflows/bda-candidate.yml` y `docs/BDA_ESTADO.md`. Un modo simulado sirve para desarrollo, pero no sustituye la prueba real que pide la rúbrica.

Para repetir el lote archivado sin recapturar, primero creamos una carpeta de trabajo nueva y copiamos los archivos de la captura; no sobrescribimos los originales. El nombre siguiente debe estar libre:

```bash
uv run --no-sync python -c "import shutil; shutil.copytree('data/capturas_anuncios/2026-11-12', 'data/scraping/ensayo_defensa')"
uv run --no-sync python scripts/run_pipeline.py --snapshot-dir data/capturas_oficiales --raw-dir data/scraping/ensayo_defensa --output-dir data/bda/ensayo_defensa --db-name reto1_ensayo
uv run --no-sync python scripts/analyze_rental_sample.py --capture-dir data/capturas_anuncios/2026-11-12 --pipeline-dir data/bda/ensayo_defensa --db-name reto1_ensayo
uv run --no-sync python scripts/transport_rent_api.py --input-dir data/capturas_api_rentas/2026-11-12 --report data/bda/api-rentas-ensayo.json
```

Enseñamos archivos recuperados idénticos, recuentos y reentrega. Para comparar índices abrimos explain y sus medidas; para CRUD y atomicidad mostramos las pruebas y la evidencia real. Preparamos servicios antes de entrar, sin consumir la exposición en descargas.

## 8 Si no hay servicios disponibles

Podemos abrir el visor con los resultados históricos guardados, sin simular que acabamos de generarlos. En Bash:

```bash
RETO1_ANALYSIS_DIR=docs/evidencias_entrega_2026-11-12/municipal uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

En PowerShell fijamos primero `$env:RETO1_ANALYSIS_DIR='docs/evidencias_entrega_2026-11-12/municipal'` y después ejecutamos el mismo lanzador. Esta alternativa lee datos reales archivados, no certifica servicios vivos. Llevamos además capturas, XML de integración, consultas y explain del 12 de noviembre. Confirmamos si la profesora acepta ese respaldo cuando falle una ejecución presencial.

## 9 Demostración SAA PIA y MIA

Para predicción y reglas basta el entorno Python y los artefactos conservados:

```bash
uv run --no-sync python main.py --subject saa_pia_mia --server.port 8501
```

Abrimos http://localhost:8501. Primero mostramos Modelos y datos, luego el informe ya conservado en Test reservado y después el caso nuevo. La app no exige HDFS ni Kafka para inferencia. No borramos `test_final.json` ni sustituimos el modelo. El diccionario completo añadido al notebook fuente es una celda explicativa; los notebooks ejecutados originales se mantienen intactos.

Para la acción local hace falta Docker en marcha. Importamos, publicamos y arrancamos n8n:

```bash
docker compose -f n8n/compose.yml run --rm n8n import:workflow --input=/workflow/flujo.json
docker compose -f n8n/compose.yml run --rm n8n publish:workflow --id=reto1Vivienda2026
docker compose -f n8n/compose.yml up -d
```

La interfaz está en http://localhost:5678. Si es un volumen nuevo puede pedir configuración inicial local. Comprobamos que el workflow esté publicado y que el receptor de acciones funcione. No compartimos credenciales del equipo ni tratamos localhost como un acceso remoto.

Caso ficticio: Bilbao, 25 años, ingreso neto 1.500 €, anual computable 18.000 €, alquiler y renta total 500 €, deudas 0 €, ahorro 2.000 € y entrada 1.000 €. Unidad individual, no compartido, siete comprobaciones verdaderas para el ensayo. Leemos predicción y periodo reales. Explicamos el 33,33 % declarado y el esfuerzo de referencia separado. Consentimos, registramos, abrimos la ficha y repetimos el mismo evento.

Si falla n8n mostramos `docs/evidencias_cierre_rubrica_2026-11-12/app-n8n.json`, `n8n.txt` y `caso.png`. Si falla la app usamos capturas, gráficos y notebooks ejecutados. Decimos la fecha y el alcance del respaldo. Nunca presentamos un fallo de red como acción confirmada.

## 10 Exportaciones y accesos que debemos preparar

El enunciado BDA/SBD pide originales almacenados en HDFS y base de datos MongoDB. Antes de entregar acordamos si revisarán acceso, exportación o ambos. Una captura y un PDF explican el trabajo, pero no equivalen automáticamente a entregar los datos de los servicios.

Como preparación recomendamos un inventario de rutas HDFS, sus huellas y una copia recuperada de la carpeta del reto, y un dump MongoDB de las bases utilizadas. Hacen falta herramientas y servicios accesibles; estas órdenes son ejemplos para adaptar a las bases y rutas realmente usadas:

```bash
hdfs dfs -ls -R /data/reto1
hdfs dfs -get /data/reto1 exportacion_hdfs_defensa
mongodump --uri mongodb://localhost:27017 --db reto1_ensayo --out exportacion_mongodb_defensa
mongodump --uri mongodb://localhost:27017 --db reto1_analisis_municipal --out exportacion_mongodb_defensa
```

La API utiliza la base indicada en su script y configuración; comprobamos su nombre y exportamos también `rentas_api`. No suponemos que esté en `reto1_ensayo`. Guardamos fecha, versión, colecciones, recuentos y README de restauración. Revisamos la copia antes de enviarla y excluimos datos personales. Estas exportaciones no se incluyen como si ya se hubieran generado en esta actualización documental.

## 11 Orden de estudio BDA y SBD

| Orden | Qué abrimos | Apartado concreto | Qué tenemos que explicar |
|---|---|---|---|
| 1 | Documentacion_BDA_SBD.pdf | 1 a 3 | Pregunta, fuentes y por qué 638 no son pisos únicos |
| 2 | Misma memoria y manifiestos | 4 a 6 | Originales, huella, recorrido y reentrega |
| 3 | src/database/data_loader.py y cleaning.py | Normalización, upsert y cuatro operaciones | INE, identidad, nulos y derivados |
| 4 | src/database/queries.py y consultas.json | Cinco consultas útiles | Condiciones, anidados, arrays y ceros |
| 5 | src/database/aggregations.py | Tres pipelines | Qué responde group, lookup, unwind y facet |
| 6 | explain.json y src/database/consistency.py | Memoria 11 y 12 | 638/4, 0 ms y atomicidad de un documento |
| 7 | Memoria 13 a 15 y visor | Tablas de capitales y muestra | 51,06/59,48/73,37 %, fechas y límites |
| 8 | Guion_oral_BDA_SBD.pdf | Demo y preguntas | Mostrar cada evidencia y justificar decisiones |

## 12 Orden de estudio de IA

| Orden | Qué abrimos | Apartado concreto | Qué tenemos que explicar |
|---|---|---|---|
| 1 | Documentacion_SAA_PIA_MIA.pdf | 1 a 4 | Alquiler medio, aprendizaje supervisado y 601/75/92; no pisos |
| 2 | Notebook ejecutado 01_eda | Campos, cinco gráficos y conclusiones | Nulos con patrón, retardos y baseline |
| 3 | src/ml_data.py y src/pipeline.py | temporal_folds y build_preprocessor | Fugas, tiempo, imputación, escalado y codificación |
| 4 | Notebook ejecutado 02 y comparativa_mlflow.csv | Nueve modelos y MLP | Motivo de cada variante y MAE de validación |
| 5 | Memoria 11 a 15 y notebook 03 | Persistencia, SHAP, SMOTE y test | 24,20 frente a 24,63; SHAP no causal; test único 28,67 |
| 6 | app/streamlit_app.py | features, submit y caso nuevo | Pipeline guardado; referencia 2026 T2 y cobertura |
| 7 | src/reglas.py | evaluar y orden de reglas | Dos esfuerzos, prioridades y seguridad |
| 8 | src/n8n.py, flujo.json y action_server.py | Envío, rama y persistencia | Consentimiento, ocho decisiones, UUID y confirmación |
| 9 | Guion_oral_SAA_PIA_MIA.pdf | Cronograma y preguntas | Exponer en 15 minutos y responder cada asignatura |

Las preguntas probables con respuestas y archivos concretos están en ambos guiones. Nos alternamos: quien no explicó un apartado en el ensayo responde su pregunta. No basta memorizar cifras si no sabemos qué unidad tienen y qué no permiten concluir.

## 13 Qué está comprobado y qué sigue pendiente

La revisión documental actual contrasta código, CSV, JSON, imágenes, manifiestos y los dos PDF docentes adjuntos. Se instalaron las dependencias con `uv sync --locked --extra dev`, se ejecutaron auditoría y sincronización, y pasaron 168 pruebas con cinco avisos conocidos. Las comprobaciones de PDF y apps que se ejecuten después constan en `validacion_documentacion.json` y en el cierre de publicación.

Las ejecuciones HDFS/Kafka/MongoDB y las ocho ramas n8n del 12 de noviembre son evidencia conservada. No las presentamos como una nueva ejecución de servicios en esta actualización de documentación. Los comandos de arranque y exportación se contrastan con código y configuración; no se declaran ejecutados solo por aparecer aquí.

Queda a nuestro cargo ensayar con reloj, comprobar el equipo del aula y preparar los accesos o exportaciones que se pidan. El profesorado debe confirmar canal de entrega, tamaño máximo de ZIP, buzones, duración BDA/SBD y valoración de novedad. No afirmamos una nota ni que el aula virtual ya haya recibido nada.

## 14 Fuentes docentes de los requisitos

`Reto1_SAA_PIA_MIA_2026-27_v5.pdf`: páginas 1 a 4 para requisitos, estructura y README; 5 a 9 para rúbricas SAA, PIA y MIA. Confirma regresión como opción, 15 minutos y tres preguntas individuales por alumno.

`RETO 1Evaluacion SBD-BDA.pdf`: páginas 1 y 2 para objetivos y entregables; 3 para BDA; 4 a 6 para SBD RA1, RA3 y RA4. Confirma datos en servicios, demostración y análisis. No fija duración de exposición BDA/SBD.

La revisión criterio por criterio se entrega aparte. Los PDF docentes son fuentes de evaluación: no convierten sus ejemplos de estructura en resultados que hayamos obtenido ni sustituyen nuestras limitaciones reales.
