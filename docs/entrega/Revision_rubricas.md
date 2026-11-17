# Revisión de las rúbricas del reto

## Cómo leemos esta comprobación

Revisamos el código y los artefactos del commit base `0f99053` contra los dos PDF docentes adjuntos en este chat. El 17 de noviembre de 2026 comprobamos los requisitos escritos, no una nota. Tener un archivo no demuestra que sepamos defenderlo ni que el profesorado valore una ampliación como novedosa.

Usamos tres estados: comprobado en código o artefactos; evidencia de ejecución conservada, con su fecha; pendiente humano o docente. Las pruebas de servicios del 12 de noviembre no se etiquetan como ejecuciones nuevas de esta revisión.

## BDA RA1

| Criterio del PDF docente página 3 | Qué tenemos y dónde se comprueba | Estado y límite |
|---|---|---|
| Extracción Python mediante API y scraping | scripts/capture_emal_api.py, capture_rentals.py; originales en data/capturas_api_rentas y capturas_anuncios | Implementado; tres estadísticas monetarias y 17 anuncios archivados. No son la misma unidad |
| HDFS organizado y recuperación | src/hdfs/, scripts/run_pipeline.py; informes de docs/evidencias_entrega_2026-11-12/ | Ejecución real conservada: 31 archivos del lote recuperados idénticos. Acceso o exportación de aula pendiente |
| Productor y consumidor Kafka Python | src/kafka/producer.py y consumer.py | Implementados; 638 mensajes del lote conservado. Simulación explícita no se presenta como broker real |
| Integración completa hasta MongoDB | scripts/run_pipeline.py y scripts/transport_rent_api.py | Evidencia real conservada de lote y API separados; reentrega sin duplicar |

Las promociones oficiales por sí solas no acreditaban precios de alquiler de anuncios. La API monetaria EMAL y el scraping archivado cubren las dos vías de extracción, explicando que la API devuelve estadísticas y no pisos individuales. Si la profesora exige anuncios individuales también por API, deberá confirmar esa interpretación: el enunciado no especifica esa unidad en cada vía.

## SBD RA1 con peso del 46,7 por ciento

| Criterio del PDF docente página 4 | Qué tenemos y dónde se comprueba | Estado y límite |
|---|---|---|
| Dos fuentes o más con campo común | INE relaciona municipios con vivienda y estadísticas; src/database/data_loader.py y src/municipal_analysis.py | Comprobado; no se unen municipios por coincidencias parciales de texto |
| Dos colecciones y relación o embedding | viviendas y municipios; características embebidas y referencia INE | Comprobado; documentamos por qué se elige cada estructura |
| Cuatro operaciones de limpieza con PyMongo | src/database/cleaning.py: duplicados, ausencias, tipos, derivados | Comprobado; no se inventan medidas ausentes |
| Carga, limpieza y transformación automática | scripts/run_pipeline.py y scripts/analyze_municipal.py | Código y ejecución histórica conservados; no requiere editar MongoDB manualmente |

## SBD RA3 con peso del 13,3 por ciento

| Criterio del PDF docente página 5 | Qué tenemos y dónde se comprueba | Estado y límite |
|---|---|---|
| Modelado con colecciones y embedding o referencia | Memoria BDA apartados 7 y 8, data_loader.py | Comprobado; tipos y claves explicados |
| CRUD completo y resultado comprobado | integration_tests/test_mongodb_live.py, test_crud_comprobado_real | Insert, find, update y delete con aserciones; ejecución real histórica en XML |
| Cinco consultas útiles con anidados o arrays y combinación | src/database/queries.py; anuncios/consultas.json en evidencias del 12 de noviembre | 6 Bilbao, 1 hasta 750, 4 filtros combinados, hasta 10 habitaciones y 3 temporales; dos ceros adicionales conservados |
| Tres pipelines y cinco etapas diferentes en total | src/database/aggregations.py: estadísticas, cruce y facet | match, group, project, sort, lookup, unwind, set, facet y limit; no exige cinco etapas por pipeline |
| Explain comparado con o sin índice | anuncios/explain.json y src/database/indexes.py | COLLSCAN 638 frente a IXSCAN 4; cuatro resultados; ambos 0 ms. No acredita velocidad temporal |
| Consistencia y justificación de transacción | src/database/consistency.py y prueba concurrente | Cien incrementos, contador 100, sobre copia aislada. Un documento atómico no requiere transacción global |

Las rutas anuncios de esta sección pertenecen a `docs/evidencias_entrega_2026-11-12/anuncios/`. El CRUD de prueba no se presenta como una vivienda observada. La prueba de atomicidad tampoco se presenta como demanda real.

## SBD RA4 con peso del 40 por ciento

| Criterio del PDF docente página 6 | Qué tenemos y dónde se comprueba | Estado y límite |
|---|---|---|
| Datos heterogéneos adaptados | JSON Visesa y API, CSV Etxebide, XLSX EMAL/INE, HTML OVJ y portales | Comprobado en src/extraction y municipal_analysis.py; cada contrato tiene tratamiento propio |
| Análisis automático | scripts/analyze_municipal.py y analyze_rental_sample.py | Generan salidas y manifiestos; no copiamos las cifras del panel a mano |
| Cinco indicadores combinando fuentes | Renta mensual y anual, contratos, variación interanual, esfuerzo y distancia al 30 % | EMAL + OVJ en 2024; no inventa salario municipal ni usa OVJ 2024 para anuncios 2026 |
| Comparar tres municipios con conclusiones vinculadas | Vitoria, Bilbao y Donostia en comparativa_municipal.json | 798,57/930,31/1.147,53 € y esfuerzos 51,06/59,48/73,37 %. Conclusión válida para el escenario |
| Tres conjuntos preparados para representar | comparativa_municipal, serie_trimestral y resumen_territorial; también mapa | Ejecución real histórica conservada; resultados nuevos requieren MongoDB y generación local |

No demostramos qué municipio es mejor para cualquier joven. La renta, un salario agregado y una selección pequeña no describen empleo, hogar, transporte o disponibilidad. La conclusión defendible es comparativa y condicionada a los indicadores calculados.

## SAA indicadores 1 a 5

| Indicador del PDF IA páginas 5 y 6 | Evidencia | Estado y límite |
|---|---|---|
| 1 IA débil y comparación con fuerte | README Qué hemos construido y memoria IA 2 | Explicación preparada; comprensión oral pendiente |
| 2 Tipo de aprendizaje y diferencia con no supervisado | README y memoria IA 2 | Regresión supervisada con objetivo observado; no agrupamiento sin etiquetas |
| 3 Dataset, campos, tipos, nulos y exclusiones | Notebook 01, resultados/diccionario.csv, README y memoria IA 3 a 5 | Once campos y siete entradas; tabla de README completada con significado de cada campo |
| 4 Cinco gráficos comentados | Notebook 01 ejecutado y resultados/01_barras a 05_correlacion | Cinco figuras reales de train y conclusión debajo; no generamos EDA nuevo mirando test |
| 5 Nulos con patrón y variables nuevas | src/ml_data.py, src/pipeline.py y notebook 01 | Retardos, supresión EMAL, objetivo sin imputar y medianas dentro de train/folds |

El notebook fuente 01 incorpora una celda Markdown con los once campos, su significado, tipo, nulos y uso. Se añade sin ejecutar celdas ni cambiar las salidas conservadas. La versión ejecutada original mantiene su tabla de tipos y nulos y las explicaciones anteriores. El README y la memoria también reúnen el diccionario completo para facilitar la corrección.

## SAA indicadores 6 a 10

| Indicador del PDF IA páginas 6 y 7 | Evidencia | Estado y límite |
|---|---|---|
| 6 Cinco familias y ampliación comparada | src/ml_models.py, ml_workflow.py y comparativa_mlflow.csv | Cinco familias implementadas; si la ampliación cuenta como no vista en clase lo confirma el profesorado |
| 7 Base MLP y tres experimentos explicados | Base 32; dos capas 64/32; tanh; alpha 0,01 | Cuatro ejecuciones registradas; memoria explica el motivo técnico de cada cambio |
| 8 Métricas adecuadas y significado para el servicio | Tabla train/validación, MAE RMSE R² y real frente a predicho | Comprobado en artefactos; error de referencia municipal, no de piso o solvencia |
| 9 Elección, tiempo, sencillez y SHAP en validación | selection.json, tabla MLflow y shap_metadatos.json | MLP 24,20 frente a persistencia 24,63; SHAP 30 filas de validación, fondo 30 de train |
| 10 Pregunta individual | Guion oral IA con respuestas y archivos | Pendiente humano; no lo certifican tests |

El requisito SMOTE es condicional al desbalance en clasificación. La tarea principal es regresión. Conservamos una clasificación auxiliar real de subida trimestral con y sin SMOTE, incluyendo matriz de confusión, precisión, recall y F1. El F1 no mejora; no se esconde ni se cambia para buscar nota.

## PIA indicadores 1 a 6

| Indicador del PDF IA página 8 | Evidencia | Estado y límite |
|---|---|---|
| 1 README completo y funciones documentadas | README, docstrings en src/ y scripts/ | Apartados obligatorios presentes; documentación nueva enlazada como vigente |
| 2 Estructura y requirements | Código canónico src/, scripts, app y requirements.txt | Estructura adaptada y explicada; carpetas académicas no son proyectos independientes |
| 3 Pipeline sklearn y modelo completo guardado | src/pipeline.py y best_model.joblib | StandardScaler y OneHotEncoder comunes; pipeline conservado para inferencia |
| 4 Modelos y experimentos en MLflow | entrega_ml/mlruns/ y captura real | Nueve experimentos de regresión y dos auxiliares; rutas de artefactos al trasladar requieren revisión |
| 5 Streamlit con test y caso nuevo más decisión | app/streamlit_app.py, test_final.json y caso.png | Test evaluado una vez; reapertura lee informe. Caso nuevo muestra referencia y regla |
| 6 Pregunta individual con código | Guion oral IA | Pendiente humano |

El ejemplo de carpetas de la página 3 se corresponde con nuestras rutas `entrega_ml/data`, `models`, `resultados` y notebooks por fase. No hemos separado artificialmente notebooks por persona ni inventado un reparto de autoría para imitar los nombres del ejemplo.

## MIA indicadores 1 a 4

| Indicador del PDF IA página 9 | Evidencia | Estado y límite |
|---|---|---|
| 1 Necesidad con dato, objetivo, usuario y mejora esperada | README Necesidad del servicio de orientación y memoria IA 1 | Contexto de servicio, Bilbao 930,31 € y escenario 59,48 %; beneficio esperado sin impacto medido |
| 2 Seis reglas o más con prioridad, decisión y seguridad | src/reglas.py | Diez reglas, seguridad 100, R_REFERENCIA 65; prueba 600/1.600 cambia orientación |
| 3 Webhook con rama por decisión y acción | n8n/flujo.json, src/n8n.py y action_server.py | Ocho ramas y fichas distintas; ejecución real histórica conservada. Novedad frente a clase pendiente docente |
| 4 Pregunta individual mostrando proyecto | Guion oral IA y caso ficticio | Pendiente humano |

La acción elegida es crear fichas locales persistidas, no enviar comunicaciones reales. El enunciado da ejemplos de acciones, no una obligación de enviar correo. Si se espera una integración concreta distinta, se debe confirmar con la profesora sin atribuirle al proyecto funciones que no tiene.

## README y requisitos transversales

El PDF IA página 4 pide título y frase, captura arriba, necesidad desarrollada, esquema y explicación de IA, datos con tabla y gráficos, y resultados con tabla MLflow, elección, test y captura. El README de esta revisión conserva esos apartados y añade enlaces a la entrega actual. La captura de app es real e histórica; las conclusiones no se basan en métricas sintéticas antiguas.

Los 15 minutos por pareja y las tres preguntas individuales por alumno están confirmados en la página 1. BDA/SBD pide demostración sin duración escrita. La memoria y presentaciones PDF responden además a la petición del equipo para la corrección; no sustituyen los archivos funcionales ni las condiciones de entrega del aula virtual.

## Qué falta realmente para entregar con tranquilidad

Tenemos implementación y evidencia conservada para los requisitos técnicos principales. La actualización documental no declara una nueva ejecución completa de todos los servicios. En `validacion_documentacion.json` se registran las comprobaciones que sí se hayan ejecutado ahora.

Antes de entregar debemos ensayar ambos, preparar el equipo y comprobar qué acceso o exportación de HDFS y MongoDB se pide. Solo el profesorado puede confirmar canal de entrega, duración BDA/SBD y novedad de las ampliaciones. No hay una garantía automática de obtener la puntuación máxima por tener todos los archivos.

Hay un límite de alcance que conviene hablar con la profesora: el servicio ofrece una referencia territorial con 19 municipios, no una respuesta individual completa a la emancipación. La API monetaria es agregada y la muestra de anuncios tiene 17 identidades. Los documentos explican esa limitación en lugar de inventar cobertura o conclusiones más amplias.

## Referencias docentes revisadas

`Reto1_SAA_PIA_MIA_2026-27_v5.pdf`, nueve páginas, adjunto recibido en esta conversación. `RETO 1Evaluacion SBD-BDA.pdf`, seis páginas, adjunto recibido en esta conversación. Los SHA-256 de ambos originales quedan en el manifiesto de validación documental. Las referencias de página permiten localizar cada requisito aunque los PDF docentes no se redistribuyan en el repositorio.
