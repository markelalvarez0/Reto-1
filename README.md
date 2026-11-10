# Reto 1 · Acceso a la vivienda para jóvenes en Euskadi

Proyecto interdisciplinar del Curso de Especialización en Inteligencia Artificial y Big Data, IABD 2026–27.

**Versión de trabajo: `dev-jon`.** `main` y `test` no deben confundirse con la versión en desarrollo. La entrega global sigue pendiente de la revisión final de los dos bloques y de su integración verificada.

## Pregunta y alcance

¿Qué referencias de alquiler y qué información verificable pueden utilizar los servicios de orientación para ayudar a jóvenes a estudiar sus opciones de vivienda en Euskadi?

Se separan tres objetos distintos:

1. **Anuncios y promociones:** describen inmuebles o promociones, con fuente, identificador y código municipal. Una promoción no equivale a un contrato individual.
2. **Estadísticas EMAL:** rentas medias y números de contratos por municipio y trimestre. Son observaciones agregadas, no anuncios ni perfiles de solicitantes.
3. **Orientación personal:** utiliza datos declarados en la app y reglas explicables. No concede ni deniega ayudas públicas y no transforma una predicción municipal en una puntuación de riesgo individual.

El antiguo objetivo `es_viable` se generaba artificialmente. Sus CSV y JSON históricos no acreditan resultados observados de emancipación; no son la base del modelo entregable nuevo.

## Estado respaldado por ejecuciones

| Componente | Evidencia y límite |
|---|---|
| Integridad INE | PR #2 integrada en `dev-jon`; un municipio desconocido no se convierte en Bilbao. |
| Suite del bloque ML publicado | 99 pruebas superadas antes de publicar; se mantienen avisos de librerías y de mini-tests con pocas iteraciones. |
| MongoDB | 6 pruebas adicionales con servidor MongoDB real en CI, separadas de `mongomock`. |
| HDFS y Kafka | Integración con servicios temporales reales en CI; los mensajes de prueba son fixtures declarados. |
| n8n | Ocho ramas, persistencia e idempotencia verificadas con servicio real. |
| MLflow y SHAP | Entrenamiento y artefactos reales sobre la captura oficial EMAL. |
| Notebooks y Streamlit | Workflow dedicado que ejecuta los notebooks y comprueba formulario → modelo → reglas → acción n8n. Consultar su resultado, no inferir éxito por la existencia del archivo. |
| Test de ML | Reservado después de seleccionar el modelo; su evaluación final es una acción separada y queda registrada. |
| Entrega global | Pendiente de cerrar dashboard, documentación completa, evaluación final y promoción controlada a `test`/`main`. |

Ejecuciones verificables:

- [Entrenamiento y 99 pruebas del bloque ML](https://github.com/markelalvarez0/Reto-1/actions/runs/42855647062).
- [MongoDB real: suite y pruebas de integración](https://github.com/markelalvarez0/Reto-1/actions/runs/42842995070).
- [HDFS y Kafka reales](https://github.com/markelalvarez0/Reto-1/actions/runs/42842995285).
- [n8n real después de corregir la disponibilidad del webhook](https://github.com/markelalvarez0/Reto-1/actions/runs/42854348068).
- [Notebooks y aplicación con modelo congelado](https://github.com/markelalvarez0/Reto-1/actions/runs/42856972138).

## Datos reales y aprendizaje automático

Los originales se recuperan con `scripts/capture_sources.py`, que conserva URL, fecha UTC, respuesta HTTP y SHA-256. Los fallos se registran, no se sustituyen por datos inventados etiquetados como reales.

La captura EMAL utilizada contiene **768 observaciones de 19 municipios**: 601 en entrenamiento hasta 2023, 75 en validación de 2024 y 92 reservadas desde 2025. Se excluyen los objetivos no publicados, sin imputarlos. La serie está revisada a la fecha de captura: la evaluación es retrospectiva.

El modelo predice **renta media municipal trimestral**, usando año, trimestre, municipio, provincia y retardos observados de renta y contratos. Los retardos se construyen antes de separar los datos, sin utilizar valores contemporáneos del objetivo como entradas. Se evalúan predicciones a un paso con observaciones previas disponibles, no predicciones autónomas de varios trimestres futuros.

Se comparan regresión lineal, KNN, Random Forest, XGBoost y SVM, además de MLP base y tres experimentos. El preprocesado usa `ColumnTransformer`, `Pipeline`, `SimpleImputer`, `StandardScaler` y `OneHotEncoder`; se ajusta dentro del entrenamiento y de cada partición temporal de validación cruzada.

Selección en validación: **MLP de dos capas**, MAE **24,20 EUR**, frente a **24,63 EUR** del baseline de persistencia. La diferencia es pequeña y no demuestra por sí sola una mejora generalizable. No son métricas de test ni del precio de un piso individual.

SMOTE se aplica únicamente a una clasificación auxiliar de subida trimestral observada, nunca a la renta continua. La comparación sin/con balanceo conserva su resultado aunque no mejore F1. SHAP se calcula en validación con fondo de entrenamiento y no se interpreta causalmente.

Documentación: [metodología](docs/METODOLOGIA_ML.md) y [evidencia de validación](docs/EVIDENCIA_ML_VALIDACION.md).

## Organización

```text
src/                         Código canónico: extracción, datos, servicios, ML y reglas
scripts/capture_sources.py    Captura original trazable
scripts/train_official.py     Entrenamiento reproducible sin evaluar test por defecto
scripts/sync_sources.py       Sincronización y verificación de copias académicas
notebooks/                   01 EDA, 02 modelos, 03 SHAP (.ipynb)
app/streamlit_app.py          Aplicación del modelo guardado, reglas y n8n
n8n/                         Workflow y servicios locales de demostración
integration_tests/           Pruebas separadas con servicios reales
tests/                       Suite de regresión y pruebas unitarias
.github/workflows/           Ejecuciones y conservación de evidencias
docs/                        Metodología y resultados comprobados
BDA + SBD/                   Carpeta de entrega del bloque Big Data
SAA + PIA + MIA/              Carpeta de entrega del bloque de IA
ainhoa/                      Copia académica heredada
```

`src/` es la fuente de verdad. Las tres copias se sincronizan; no se mantienen implementaciones alternativas manuales.

## Reproducir el bloque ML

Entorno validado: Python 3.12. Utilizar un entorno virtual y ejecutar desde la raíz del repositorio.

```bash
python -m pip install -r requirements-ci.txt
python -m pytest tests/ -q
python scripts/sync_sources.py --check
```

Para una nueva ejecución, sin un modelo seleccionado previamente en la carpeta de salida:

```bash
python scripts/capture_sources.py --output data/capturas_oficiales
python scripts/train_official.py --raw data/capturas_oficiales --output entrega_ml
python -m streamlit run app/streamlit_app.py
```

No recapturar los datos ni reentrenar para intentar mejorar resultados después de abrir el test. Para reproducir exactamente la evidencia publicada, usar la captura y el artefacto del run enlazado, conservar sus huellas y el entorno registrado. El script rechaza sobrescribir una selección existente.

Abrir los tres `.ipynb` con un kernel del mismo entorno. Los notebooks consultan los experimentos existentes cuando la selección ya está cerrada. La pestaña **Test reservado** de Streamlit evalúa únicamente el modelo elegido y conserva el informe; las reaperturas leen el informe sin repetir la evaluación.

Los archivos `joblib` solo deben cargarse desde artefactos de confianza. MLflow guarda una base SQLite y artefactos con rutas locales; al trasladarlos a otro equipo hay que conservar o adaptar las rutas de los artefactos. El modelo completo de inferencia se encuentra de forma independiente en `entrega_ml/models/best_model.joblib`.

## n8n y protección de datos

```bash
docker compose -f n8n/compose.yml run --rm n8n import:workflow --input=/workflow/flujo.json
docker compose -f n8n/compose.yml run --rm n8n publish:workflow --id=reto1Vivienda2026
docker compose -f n8n/compose.yml up -d
```

La aplicación no envía acciones sin consentimiento. El cliente transmite solo identificador de evento, decisión, regla y referencia estimada; no envía nombre, salario, dirección ni expediente. Una respuesta HTTP por sí sola no se considera éxito: se exige confirmación de persistencia. El UUID conserva la idempotencia al repetir la misma acción.

Las acciones locales generan fichas o listas de comprobación distintas. **No envían SMS reales ni tramitan subvenciones.** La configuración Docker es una demostración local, no un despliegue de producción.

## Evaluación y límites de entrega

Los resultados heredados de `best_model.json`, `mlruns_data.json` y gráficos antiguos no sustituyen los artefactos nuevos ni deben presentarse como evidencia de datos reales. Los README y PDF históricos de cada bloque necesitan conciliación final con el código actualizado.

Pasar pruebas unitarias o probar servicios con fixtures no demuestra por sí solo que todas las fuentes reales atraviesen el pipeline completo. La entrega final debe incluir además los indicadores y mapa basados en datos verificables, la evaluación sellada del test, las capturas efectivas, la documentación coherente y la integración validada en las ramas previstas por `AGENTS.md`.
