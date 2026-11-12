# Contraste con los materiales originales aportados

Revisión del 11 de noviembre de 2026. Los adjuntos son fuentes de requisitos y
ejemplos; las instrucciones directas del usuario fijan objetivo, rama y test sellado.
El ZIP del proyecto no reemplaza la rama remota comprobada `dev-jon`.

| Fuente | Requisito y correspondencia comprobada |
|---|---|
| Reto1_SAA_PIA_MIA_2026-27_v5.pdf, pp. 1–3 y rúbricas | Admite regresión. Pide cinco familias, MLP base + tres experimentos, pipeline sklearn, MLflow, SHAP con validación y test una vez. Los artefactos conservados contienen nueve experimentos, pipeline completo, figuras y evaluación única. No fija Keras como biblioteca obligatoria. |
| ejercicios2.zip | 195 archivos, incluidos 59 notebooks, 84 CSV y 28 Python. Los notebooks de redes densas usan Sequential, Dense y Adam. La entrega usa MLPRegressor de sklearn: documentar esta diferencia, sin presentarlo como Keras ni reseleccionar con el test observado. |
| EJERCICIOS.zip | 49 archivos; los notebooks Kafka_Python_HDFS y Practica_Pedidos usan confluent_kafka y hdfs.InsecureClient. La entrega usa kafka-python-ng y REST WebHDFS. Implementan productor/consumidor Python y almacenamiento HDFS; no son las mismas API. |
| RETO 1Evaluacion SBD-BDA.pdf, pp. 1–2 | Exige precios reales mediante API y scraping. Los catálogos de promociones y el HTML salarial no acreditan anuncios individuales. La muestra del 12 de noviembre acredita 17 anuncios; ver RESULTADOS_ANUNCIOS.md. |
| Misma rúbrica SBD, RA3 | Exige tres pipelines y cinco etapas **diferentes en conjunto**, incluyendo group y lookup/unwind/facet; no exige cinco etapas en cada pipeline. Ver src/database/aggregations.py y src/municipal_analysis.py. Las pruebas reales distinguen esta ejecución de mongomock. |
| Misma rúbrica SBD, RA4 | Cinco indicadores, tres municipios y tres conjuntos para visualizar. La exportación EMAL/OVJ contiene comparación, serie, resumen y mapa; el salario es autonómico y la media territorial simple. |
| README_ejemplo_CV.md | Ejemplo ficticio orientativo, no plantilla obligatoria. No reutilizar sus cifras de negocio. El README del proyecto incorpora objetivos, métricas observadas, límites y capturas. |
| DOCUMENTO_MAESTRO_CONTEXTO_TECNICO_RETO1.pdf | Documento histórico con XGBoost ganador, métricas sintéticas y salarios constantes. No sirve como evidencia de la versión actual. Se sustituye como informe vigente mediante scripts/build_delivery_report.py. |

## Evidencia y límites

Las seis capturas originales y los 88 artefactos ML se verifican por SHA-256 con
`scripts/audit_project.py`. La generación del PDF lee el informe sellado y sus
figuras; no deserializa ni ejecuta el modelo. Las capturas de MLflow conservadas
son históricas y están etiquetadas como tales.

La ejecución 42999928204 del commit f107a0a aparece cancelada por exceder 30 minutos
en GitHub. No cuenta como éxito. Se ha acotado la descarga de Hadoop y se utiliza
la distribución lean oficial con SHA512, suficiente para HDFS local.

En el entorno anterior, el 11 de noviembre, la red rechazaba el CONNECT a www.habitaclia.com y www.pisos.com
con HTTP 403; api.github.com también devuelve Forbidden. Es un bloqueo de acceso,
no evidencia de que los portales permitan scraping. Hay que habilitar los dominios
en la configuración y consultar después robots.txt y condiciones, conservando
procedencia. No se eluden restricciones ni se inventan anuncios.

En ese entorno, la herramienta de configuración tampoco podía verificar el borrador del entorno
(INVALID_ARGUMENT). No se afirma que esos permisos se hayan guardado. La
publicación de código por Git usa la autenticación HTTPS existente, separada de
la API de Actions. No se piden ni almacenan tokens en el repositorio.


Actualización 12 de noviembre: entorno operativo, robots HTTP 200 en ambos portales y API GitHub HTTP 200. Se han revisado avisos legales y rutas permitidas antes de la muestra acotada. Robots no concede derechos de redistribución o explotación comercial.
