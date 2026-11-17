# Guía de entrega y defensa

## 1 Qué presentamos a la profesora

Entregamos dos bloques del mismo proyecto: BDA y SBD, y SAA, PIA y MIA. Las memorias explican el trabajo por sí solas; las presentaciones sirven para contarlo en voz alta. Los guiones y esta guía ayudan a prepararnos. El código, los datos y el modelo se conservan en sus formatos funcionales: un PDF no sustituye una base de datos ni un notebook.

Preparamos dos ZIP en la raíz: `Entrega_BDA_SBD.zip` y `Entrega_SAA_PIA_MIA.zip`. Cada uno incluye la memoria y la presentación de su bloque, las fuentes editables, los archivos funcionales y un PDF con las instrucciones de ejecución. Los guiones orales, esta guía y la revisión de rúbricas quedan fuera de los ZIP porque son material de preparación.

## 2 Lista exacta de archivos PDF

| Bloque | Archivo desde docs/entrega/ | Para qué sirve | Carácter |
|---|---|---|---|
| BDA y SBD | [BDA_SBD/Documentacion_BDA_SBD.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/BDA_SBD/Documentacion_BDA_SBD.pdf) | Arquitectura, decisiones, resultados y límites | Informe y arquitectura confirmados en rúbrica; formato PDF solicitado por el equipo |
| BDA y SBD | [BDA_SBD/Presentacion_BDA_SBD.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/BDA_SBD/Presentacion_BDA_SBD.pdf) | Apoyo a la demostración | Presentación preparada para la defensa; demostración confirmada |
| BDA y SBD | [BDA_SBD/Guion_oral_BDA_SBD.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/BDA_SBD/Guion_oral_BDA_SBD.pdf) | Qué decir y qué abrir en cada diapositiva | Estudio, solicitado por el equipo |
| SAA PIA MIA | [SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.pdf) | Explicación de datos, modelos, app y acción | Memoria PDF solicitada por el equipo; acompañada del contenido del README en PDF y de los notebooks exigidos |
| SAA PIA MIA | [SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.pdf) | Exposición de 15 minutos por pareja | Duración y defensa confirmadas; soporte PDF preparado |
| SAA PIA MIA | [SAA_PIA_MIA/Guion_oral_SAA_PIA_MIA.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/SAA_PIA_MIA/Guion_oral_SAA_PIA_MIA.pdf) | Ensayo con tiempos y preguntas | Estudio, solicitado por el equipo |
| BDA y SBD | [Instrucciones_BDA_SBD.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/paquetes/Instrucciones_BDA_SBD.pdf) | Instalación, visor y servicios | Incluido en la raíz de su ZIP |
| BDA y SBD | [Instrucciones_restauracion.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/data/exportaciones_entrega_2026-11-17/Instrucciones_restauracion.pdf) | Recuperar HDFS y MongoDB | Incluido junto a las exportaciones |
| SAA PIA MIA | [Instrucciones_SAA_PIA_MIA.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/paquetes/Instrucciones_SAA_PIA_MIA.pdf) | Instalación, app y n8n | Incluido en la raíz de su ZIP |
| Común | [Guia_entrega_y_defensa.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/Guia_entrega_y_defensa.pdf) | Lista de entrega, estudio y demo | Apoyo solicitado por el equipo |
| Común | [Revision_rubricas.pdf](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/Revision_rubricas.pdf) | Relación de criterios con evidencia | Comprobación adicional; no es un certificado de nota |

Las fuentes Markdown editables tienen el mismo nombre y carpeta. `scripts/build_academic_docs.py` genera los PDF desde esas fuentes. Sus dependencias documentales van aparte en `docs/entrega/requirements-documentacion.txt`; no cambiamos las dependencias del modelo.

## 3 Qué más tiene que acompañar a los PDF

| Bloque o asignatura | Archivo o carpeta desde la raíz | Para qué sirve | Confirmado o recomendado |
|---|---|---|---|
| Común | PDF de instrucciones de cada paquete | Entrada, instrucciones y resultados | Contenido del README confirmado para IA; entregado en PDF por indicación del equipo |
| Común | [main.py](https://github.com/markelalvarez0/Reto-1/blob/main/main.py), src/, scripts/, app/ | Código Python organizado y funcional | Confirmado en ambos enunciados |
| Común | [requirements.txt](https://github.com/markelalvarez0/Reto-1/blob/main/requirements.txt) | Dependencias | Confirmado en PIA |
| Común | [pyproject.toml](https://github.com/markelalvarez0/Reto-1/blob/main/pyproject.toml), uv.lock, requirements-ci.txt | Instalación reproducible y comprobaciones | Soporte técnico recomendado; uv es el camino preparado |
| BDA | [data/capturas_oficiales/](https://github.com/markelalvarez0/Reto-1/tree/main/data/capturas_oficiales/) | Seis originales y manifiesto | Datos y originales en HDFS confirmados |
| BDA | [data/capturas_anuncios/](https://github.com/markelalvarez0/Reto-1/tree/main/data/capturas_anuncios/) y data/capturas_api_rentas/ | HTML, robots, JSON API y procedencia | Evidencia de API y scraping confirmados |
| BDA | [Copia de HDFS](https://github.com/markelalvarez0/Reto-1/tree/main/data/exportaciones_entrega_2026-11-17/hdfs/) | 37 archivos recuperados y verificados | Datos exigidos; exportación incluida |
| SBD | [Copias MongoDB](https://github.com/markelalvarez0/Reto-1/tree/main/data/exportaciones_entrega_2026-11-17/mongodb/) | Tres bases exportadas con sus índices | Base de datos exigida; restauración comprobada |
| BDA y SBD | [docs/evidencias_entrega_2026-11-12/](https://github.com/markelalvarez0/Reto-1/tree/main/docs/evidencias_entrega_2026-11-12/) | Transporte, consultas, explain y vistas | Respaldo recomendado de la demostración exigida |
| BDA y SBD | [docs/evidencias_cierre_rubrica_2026-11-12/](https://github.com/markelalvarez0/Reto-1/tree/main/docs/evidencias_cierre_rubrica_2026-11-12/) | API monetaria y cierre real | Evidencia adicional del recorrido |
| SAA | [notebooks/](https://github.com/markelalvarez0/Reto-1/tree/main/notebooks/) y entrega_ml/notebooks_ejecutados/ | EDA, modelos y SHAP con salidas conservadas | Notebooks y análisis confirmados; salidas ayudan a revisar sin ejecutar |
| SAA y PIA | [entrega_ml/data/](https://github.com/markelalvarez0/Reto-1/tree/main/entrega_ml/data/) | train.csv, val.csv, test.csv y procedencia | Datos y particiones confirmados; estas rutas sustituyen la estructura de ejemplo |
| SAA y PIA | [entrega_ml/models/](https://github.com/markelalvarez0/Reto-1/tree/main/entrega_ml/models/) | Pipeline joblib y selección cerrada | Mejor modelo guardado confirmado |
| SAA y PIA | [entrega_ml/resultados/](https://github.com/markelalvarez0/Reto-1/tree/main/entrega_ml/resultados/) | Tabla MLflow, EDA, SHAP, SMOTE y test | Resultados y métricas confirmados |
| PIA | [entrega_ml/mlruns/](https://github.com/markelalvarez0/Reto-1/tree/main/entrega_ml/mlruns/) y docs/evidencias_ml/capturas/ | Registros y capturas MLflow y app | Registro y captura confirmados |
| SAA y PIA | [docs/TEST_FINAL_EMAL.json](https://github.com/markelalvarez0/Reto-1/blob/main/docs/TEST_FINAL_EMAL.json) y docs/evidencias_ml/ | Evaluación única y manifiesto de artefactos | Test una vez confirmado; huellas son protección técnica |
| MIA | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)reglas.py, [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)n8n.py | Prioridad, motivo, seguridad y webhook | Confirmado |
| MIA | [n8n/flujo.json](https://github.com/markelalvarez0/Reto-1/blob/main/n8n/flujo.json) y n8n/compose.yml | Workflow importable y servicios locales | Flujo por decisión confirmado; Compose es soporte local |
| MIA | data/acciones_n8n/ si se genera una demo | Ficha local de un caso ficticio | Evidencia recomendada, generada fuera de Git |
| Común | [tests/](https://github.com/markelalvarez0/Reto-1/tree/main/tests/), integration_[tests/](https://github.com/markelalvarez0/Reto-1/tree/main/tests/) y .github/workflows/ | Verificación y ejecuciones | Evidencia técnica de apoyo |

La estructura del enunciado IA es básica y no coincide literalmente con todas nuestras rutas. Conservamos un único repositorio y explicamos la correspondencia: `data/raw` pasa a capturas originales, particiones a `entrega_ml/data`, modelo a `entrega_ml/models` y resultados a `entrega_ml/resultados`. Las carpetas académicas comparten recursos de raíz; copiarlas solas puede dejar fuera archivos necesarios.

## 4 Los dos ZIP que entregamos

[Entrega_BDA_SBD.zip](https://github.com/markelalvarez0/Reto-1/raw/refs/heads/main/Entrega_BDA_SBD.zip) corresponde a BDA y SBD. Lleva memoria, presentación e instrucciones en PDF, código, originales de API y scraping, consultas, resultados, evidencias del transporte y las instrucciones del visor y de los servicios.

[Entrega_SAA_PIA_MIA.zip](https://github.com/markelalvarez0/Reto-1/raw/refs/heads/main/Entrega_SAA_PIA_MIA.zip) corresponde a SAA, PIA y MIA. Lleva memoria, presentación e instrucciones en PDF, código, datos y particiones, modelo guardado, notebooks fuente y ejecutados, registros MLflow, resultados, capturas y workflow n8n.

Descomprimimos cada ZIP completo. Dentro encontramos `Instrucciones_BDA_SBD.pdf` o `Instrucciones_SAA_PIA_MIA.pdf`, los documentos en `docs/entrega/` y un comprobador `verificar_entrega.py`. No copiamos únicamente una carpeta académica antigua, porque utiliza recursos compartidos de raíz. Los ZIP mantienen las rutas necesarias para sus aplicaciones.

Si hay buzones separados, usamos el paquete del bloque correspondiente: BDA/SBD para esas dos asignaturas y SAA/PIA/MIA para las otras tres. Si piden enlaces, adjuntamos también el repositorio. El canal y el límite de tamaño los marca el aula virtual.

El paquete BDA/SBD incluye los datos exportados de HDFS y MongoDB. El apartado 10 explica cómo restaurarlos. Para repetir el sistema hacen falta los servicios accesibles; el ZIP conserva sus datos, no un servidor en marcha.

## 5 Qué se guarda en Git y qué se genera en el equipo

Git incluye código, dependencias, originales archivados, modelo, particiones, resultados ML, notebooks ejecutados, workflow, evidencias históricas y estos PDF. Podemos comprobarlo con `git ls-files`.

`.gitignore` excluye `data/analisis_municipal/`, `data/analisis_anuncios/`, `data/bda/`, `data/acciones_n8n/`, `data/scraping/`, almacenamiento HDFS emulado, informes regenerados y entorno virtual. También hay un volumen Docker local para n8n. No prometemos que todo eso aparezca al clonar.

El visor territorial espera resultados municipales verificables. En un clon nuevo hay que generarlos con MongoDB o seleccionar explícitamente las evidencias conservadas. Las fichas de n8n se crean al ejecutar la acción. `localhost` apunta a la máquina desde la que se abre el navegador y no es una URL pública para la profesora.

## 6 Descargar instalar y comprobar

Para el repositorio completo, con Git, Python 3.12 y uv disponibles:

```bash
git clone https://github.com/markelalvarez0/Reto-1.git
cd Reto-1
uv sync --locked --extra dev
uv run --no-sync python main.py --audit --json
uv run --no-sync python scripts/sync_sources.py --check
uv run --no-sync python -m pytest tests/ -q
```

Si usamos uno de los ZIP, seguimos su PDF de instrucciones y ejecutamos `python verificar_entrega.py` dentro de su carpeta. La auditoría global del repositorio completo comprueba originales, artefactos, test sellado, anuncios y copias académicas sin entrenar. Los tests incluyen miniensayos con fixtures; no reentrenan el modelo entregado ni repiten su holdout. Para abrir los resultados no ejecutamos `scripts/train_official.py` ni las celdas históricas de entrenamiento.

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
uv run --no-sync python scripts/transport_rent_api.py --input-dir data/capturas_api_rentas/2026-11-12 --db-name reto1_api_rentas --report data/bda/api-rentas-ensayo.json
```

Enseñamos archivos recuperados idénticos, recuentos y reentrega. Para comparar índices abrimos explain y sus medidas; para CRUD y atomicidad mostramos las pruebas y la evidencia real. Preparamos servicios antes de entrar, sin consumir la exposición en descargas.

## 8 Si no hay servicios disponibles

Podemos abrir el visor con los resultados históricos guardados, sin simular que acabamos de generarlos. En Bash:

```bash
RETO1_ANALYSIS_DIR=docs/evidencias_entrega_2026-11-12/municipal uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

En PowerShell:

```powershell
$env:RETO1_ANALYSIS_DIR='docs/evidencias_entrega_2026-11-12/municipal'
uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

 Esta alternativa lee datos reales archivados, no certifica servicios vivos. Llevamos además capturas, XML de integración, consultas y explain del 12 de noviembre. Confirmamos si la profesora acepta ese respaldo cuando falle una ejecución presencial.

## 9 Demostración SAA PIA y MIA

Para predicción y reglas basta el entorno Python y los artefactos conservados:

```bash
uv run --no-sync python main.py --subject saa_pia_mia --server.port 8501
```

Abrimos http://localhost:8501. Cada aplicación queda en su propia terminal; la detenemos con Ctrl+C. Primero mostramos Modelos y datos, luego el informe ya conservado en Test reservado y después el caso nuevo. La app no exige HDFS ni Kafka para inferencia. No borramos `test_final.json` ni sustituimos el modelo. El diccionario completo añadido al notebook fuente es una celda explicativa; los notebooks ejecutados originales se mantienen intactos.

Para la acción local hace falta Docker en marcha. Importamos, publicamos y arrancamos n8n:

```bash
docker compose -f n8n/compose.yml run --rm n8n import:workflow --input=/workflow/flujo.json
docker compose -f n8n/compose.yml run --rm n8n publish:workflow --id=reto1Vivienda2026
docker compose -f n8n/compose.yml up -d
```

La interfaz está en http://localhost:5678. Si es un volumen nuevo puede pedir configuración inicial local. Comprobamos que el workflow esté publicado y que el receptor de acciones funcione. No compartimos credenciales del equipo ni tratamos localhost como un acceso remoto.

Caso ficticio: Bilbao, 25 años, ingreso neto 1.500 €, anual computable 18.000 €, alquiler y renta total 500 €, deudas 0 €, ahorro 2.000 € y entrada 1.000 €. Unidad individual, no compartido, siete comprobaciones verdaderas para el ensayo. Leemos predicción y periodo reales. Explicamos el 33,33 % declarado y el esfuerzo de referencia separado. Consentimos, registramos, abrimos la ficha y repetimos el mismo evento.

Si falla n8n mostramos `docs/evidencias_cierre_rubrica_2026-11-12/app-n8n.json`, `n8n.txt` y `caso.png`. Si falla la app usamos capturas, gráficos y notebooks ejecutados. Decimos la fecha y el alcance del respaldo. Nunca presentamos un fallo de red como acción confirmada.

## 10 Datos de HDFS y MongoDB incluidos

El ZIP BDA/SBD contiene `data/exportaciones_entrega_2026-11-17/`. Incluye 37 archivos recuperados de HDFS y tres copias MongoDB creadas después de repetir el recorrido con los originales archivados y servicios reales. Comprobamos la restauración de los archivos, documentos e índices en destinos nuevos.

Las bases exportadas son `reto1_entrega_paquete` (638 registros y 80 municipios), `reto1_municipal_paquete` (768 observaciones EMAL y un contexto OVJ) y `reto1_api_paquete` (tres estadísticas). Son unidades distintas y no se suman como viviendas.

Con MongoDB y MongoDB Database Tools instalados, desde la raíz del paquete:

```bash
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_entrega_paquete.archive.gz --gzip
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_municipal_paquete.archive.gz --gzip
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_api_paquete.archive.gz --gzip
```

Las órdenes crean las bases con esos nombres. Si ya existen, usamos otros nombres con `--nsFrom` y `--nsTo`; no necesitamos borrar datos del servidor. Con HDFS y su cliente disponibles:

```bash
hdfs dfs -mkdir -p /data
hdfs dfs -put data/exportaciones_entrega_2026-11-17/hdfs/data/reto1 /data/
hdfs dfs -ls -R /data/reto1
```

La carga supone que `/data/reto1` no existe. Si ya existe, elegimos otra ruta de destino. El [PDF de restauración](https://github.com/markelalvarez0/Reto-1/blob/main/data/exportaciones_entrega_2026-11-17/Instrucciones_restauracion.pdf), los inventarios y `restauracion_verificada.json` explican la copia. Para demostrar el recorrido desde el principio usamos los comandos del apartado 7.

## 11 Orden de estudio BDA y SBD

| Orden | Qué abrimos | Apartado concreto | Qué tenemos que explicar |
|---|---|---|---|
| 1 | Documentacion_BDA_SBD.pdf | 1 a 3 | Pregunta, fuentes y por qué 638 no son pisos únicos |
| 2 | Misma memoria y manifiestos | 4 a 6 | Originales, huella, recorrido y reentrega |
| 3 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)database/data_loader.py y cleaning.py | Normalización, upsert y cuatro operaciones | INE, identidad, nulos y derivados |
| 4 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)database/queries.py y consultas.json | Cinco consultas útiles | Condiciones, anidados, arrays y ceros |
| 5 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)database/aggregations.py | Tres pipelines | Qué responde group, lookup, unwind y facet |
| 6 | explain.json y [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)database/consistency.py | Memoria 11 y 12 | 638/4, 0 ms y atomicidad de un documento |
| 7 | Memoria 13 a 15 y visor | Tablas de capitales y muestra | 51,06/59,48/73,37 %, fechas y límites |
| 8 | Guion_oral_BDA_SBD.pdf | Demo y preguntas | Mostrar cada evidencia y justificar decisiones |

## 12 Orden de estudio de IA

| Orden | Qué abrimos | Apartado concreto | Qué tenemos que explicar |
|---|---|---|---|
| 1 | Documentacion_SAA_PIA_MIA.pdf | 1 a 4 | Alquiler medio, aprendizaje supervisado y 601/75/92; no pisos |
| 2 | Notebook ejecutado 01_eda | Campos, cinco gráficos y conclusiones | Nulos con patrón, retardos y baseline |
| 3 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)ml_data.py y [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)pipeline.py | temporal_folds y build_preprocessor | Fugas, tiempo, imputación, escalado y codificación |
| 4 | Notebook ejecutado 02 y comparativa_mlflow.csv | Nueve modelos y MLP | Motivo de cada variante y MAE de validación |
| 5 | Memoria 11 a 15 y notebook 03 | Persistencia, SHAP, SMOTE y test | 24,20 frente a 24,63; SHAP no causal; test único 28,67 |
| 6 | [app/](https://github.com/markelalvarez0/Reto-1/tree/main/app/)streamlit_app.py | features, submit y caso nuevo | Pipeline guardado; referencia 2026 T2 y cobertura |
| 7 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)reglas.py | evaluar y orden de reglas | Dos esfuerzos, prioridades y seguridad |
| 8 | [src/](https://github.com/markelalvarez0/Reto-1/tree/main/src/)n8n.py, flujo.json y action_server.py | Envío, rama y persistencia | Consentimiento, ocho decisiones, UUID y confirmación |
| 9 | Guion_oral_SAA_PIA_MIA.pdf | Cronograma y preguntas | Exponer en 15 minutos y responder cada asignatura |

Las preguntas probables con respuestas y archivos concretos están en ambos guiones. Nos alternamos: quien no explicó un apartado en el ensayo responde su pregunta. No basta memorizar cifras si no sabemos qué unidad tienen y qué no permiten concluir.

## 13 Qué está comprobado y qué sigue pendiente

La revisión documental actual contrasta código, CSV, JSON, imágenes, manifiestos y los dos PDF docentes adjuntos. Se instalaron las dependencias con `uv sync --locked --extra dev`, se ejecutaron auditoría y sincronización, y pasaron 168 pruebas con cinco avisos conocidos. Las comprobaciones de PDF y apps que se ejecuten después constan en `validacion_documentacion.json` y en el cierre de publicación.

Las evidencias del 12 de noviembre se conservan con su fecha. Para preparar el ZIP BDA/SBD hemos repetido además el recorrido HDFS/Kafka/MongoDB con los originales archivados, creado las exportaciones y comprobado su restauración. Las ocho ramas n8n siguen respaldadas por la ejecución histórica; no se declara una nueva ejecución de n8n en esta revisión.

Queda a nuestro cargo ensayar con reloj y comprobar el equipo del aula. Los datos exportados ya están incluidos en el paquete BDA/SBD. El profesorado debe confirmar canal de entrega, tamaño máximo de ZIP, buzones, duración BDA/SBD y valoración de novedad. No afirmamos una nota ni que el aula virtual ya haya recibido nada.

## 14 Fuentes docentes de los requisitos

`Reto1_SAA_PIA_MIA_2026-27_v5.pdf`: páginas 1 a 4 para requisitos, estructura y README; 5 a 9 para rúbricas SAA, PIA y MIA. Confirma regresión como opción, 15 minutos y tres preguntas individuales por alumno.

`RETO 1Evaluacion SBD-BDA.pdf`: páginas 1 y 2 para objetivos y entregables; 3 para BDA; 4 a 6 para SBD RA1, RA3 y RA4. Confirma datos en servicios, demostración y análisis. No fija duración de exposición BDA/SBD.

La revisión criterio por criterio se entrega aparte. Los PDF docentes son fuentes de evaluación: no convierten sus ejemplos de estructura en resultados que hayamos obtenido ni sustituyen nuestras limitaciones reales.
