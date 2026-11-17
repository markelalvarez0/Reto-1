# Instrucciones de ejecución · SAA, PIA y MIA

## Qué entregamos

Hemos creado una aplicación que estima una renta media municipal, explica una orientación mediante reglas y permite registrar una acción local con n8n tras recibir consentimiento.

## Documentos para corregir


- [Memoria en PDF](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.pdf): datos, preparación, modelos, resultados, app, reglas y límites.

- [Presentación en PDF](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.pdf): 12 diapositivas con gráficos, capturas y explicaciones de qué hicimos y por qué.

- Las fuentes editables `.md` están junto a los PDF.

## Qué contiene

| Carpeta | Contenido |
|---|---|
| `src/`, `scripts/`, `app/` | Código Python organizado, pipeline, reglas y aplicación |
| `data/capturas_oficiales/` | Datos originales y procedencia |
| `notebooks/` | EDA, entrenamiento y explicación SHAP en formato editable |
| `entrega_ml/notebooks_ejecutados/` | Los tres notebooks con sus salidas conservadas |
| `entrega_ml/data/` | Train, validación, test y procedencia |
| `entrega_ml/models/` | Pipeline completo guardado y selección del modelo |
| `entrega_ml/resultados/` | Métricas, gráficos, SHAP, SMOTE y test final |
| `entrega_ml/mlruns/` | Registros de experimentos MLflow |
| `docs/evidencias_ml/` | Evidencias y huellas de los artefactos |
| `n8n/` | Workflow importable y configuración de servicios locales |
| `tests/` | Pruebas de modelos, preparación y reglas |

Conservamos las rutas del proyecto para que la aplicación encuentre los archivos. `src/` es código compartido. No se incluyen guiones orales, material de estudio ni informes antiguos.

## Datos, objetivo y resultados

Usamos 768 observaciones EMAL de 19 municipios. Una observación corresponde a un municipio y trimestre, no a un piso individual. Separamos por fecha: 601 para entrenamiento, 75 para validación y 92 para test.

El objetivo es una renta media mensual en euros. Las entradas incluyen municipio, provincia, año, trimestre, rentas anteriores y contratos anteriores. Los datos se imputan, escalan y codifican dentro del pipeline. El sueldo no es una variable de entrenamiento: se usa después en las reglas.

Comparamos regresión lineal, KNN, Random Forest, XGBoost, SVM y cuatro variantes MLP. Se conserva la MLP de dos capas de sklearn: MAE de validación 24,20 €, frente a 24,63 € de usar la renta anterior. La mejora es pequeña. En el test final: MAE 28,67 €, RMSE 37,93 € y R² 0,9189. No es el error garantizado para una vivienda concreta.

SHAP explica contribuciones del modelo sin demostrar causalidad. SMOTE se estudió en una clasificación auxiliar de subidas de renta, separada de la regresión principal. Las decisiones y resultados se desarrollan en la memoria.

## Instalar y comprobar

Descomprimir todo el ZIP y abrir una terminal en la carpeta `Entrega_SAA_PIA_MIA`, donde está este PDF de instrucciones. Se necesita Python 3.12 y [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --locked --extra dev
uv run --no-sync python verificar_entrega.py
uv run --no-sync python -m pytest tests/ -q
```

El verificador comprueba las huellas de los archivos. Los tests utilizan miniensayos y copias temporales; no reentrenan el modelo entregado ni vuelven a puntuar su test final.

## Abrir la aplicación

```bash
uv run --no-sync python main.py --subject saa_pia_mia --server.port 8501
```

Abrir http://localhost:8501. La primera pestaña muestra modelos y datos, la segunda el informe del test ya conservado y la tercera permite introducir un caso. Ctrl+C detiene la aplicación. Para usar el modelo no hacen falta HDFS ni Kafka.

El modelo entregado ya está entrenado. Para revisarlo se abren sus resultados y los notebooks ejecutados. No hace falta ejecutar `scripts/train_official.py`, entrenar desde un notebook ni borrar `test_final.json`.

## Arrancar la acción con n8n

Para guardar acciones se necesita Docker con Compose en marcha. Desde la raíz del paquete, en otra terminal:

```bash
docker compose -f n8n/compose.yml run --rm n8n import:workflow --input=/workflow/flujo.json
docker compose -f n8n/compose.yml run --rm n8n publish:workflow --id=reto1Vivienda2026
docker compose -f n8n/compose.yml up -d
```

La interfaz de n8n está en http://localhost:5678. En un volumen nuevo puede pedir la configuración inicial de la cuenta local. El workflow usa el receptor `acciones` del mismo Compose y guarda las fichas en `data/acciones_n8n/` del equipo. La app apunta por defecto a `http://localhost:5678/webhook/vivienda-decision`; `N8N_WEBHOOK_URL` permite configurar otra dirección.

La aplicación pide consentimiento y solo envía decisión, regla, referencia e identificador del evento. No envía el sueldo ni el perfil. Según la decisión se crea una ficha, un plan o una lista de comprobación. Una confirmación exige que la acción se haya guardado; un error no se presenta como éxito. Repetir el mismo evento conserva una sola ficha.

Para detener los servicios locales:

```bash
docker compose -f n8n/compose.yml down
```

Las fichas y el volumen se conservan. La acción es local: no concede ayudas ni envía correo o SMS a personas.

## Caso ficticio para comprobar el funcionamiento

Municipio Bilbao; edad 25; ingreso neto mensual 1.500 €; ingreso anual computable 18.000 €; pago mensual y renta total 500 €; deudas 0 €; ahorro 2.000 €; coste de entrada 1.000 €. Unidad individual y contrato no compartido. Las siete comprobaciones documentales se marcan verdaderas porque así se define este caso inventado.

Al pulsar «Predecir referencia y orientar», se muestra una referencia para 2026 T2. El esfuerzo del alquiler declarado es 33,33 %. El esfuerzo de referencia se calcula aparte con la renta municipal predicha. Las diez reglas tienen prioridad y explican la recomendación. El umbral interno del 40 % orienta la comparación de municipios; no determina derechos a ayudas.

Para comprobar la acción, activar el consentimiento y pulsar «Registrar accion en n8n». Consultar la confirmación y la ficha local. Si se pulsa otra vez sin enviar un formulario nuevo, debe mantenerse el mismo evento y una sola ficha.

## Límites y procedencia

La fuente principal es EMAL, conservada en `data/capturas_oficiales/` con URL, fecha y huella. La serie revisada permite una evaluación retrospectiva, no una prueba de datos disponibles históricamente en tiempo real. El modelo cubre 19 municipios y predice medias, no precios exactos ni solvencia individual.

El test se evaluó una sola vez y sus resultados están sellados en `docs/TEST_FINAL_EMAL.json`. Los JSON, XML y capturas del 12 de noviembre acreditan ejecuciones conservadas de esa fecha. Las capturas nuevas de la presentación no sustituyen una nueva ejecución de n8n.

Repositorio completo: https://github.com/markelalvarez0/Reto-1
