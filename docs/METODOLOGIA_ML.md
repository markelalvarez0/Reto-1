# Aprendizaje con observaciones reales

## Objetivo y limite de validez

Predecir la renta media municipal de nuevos contratos de alquiler del siguiente trimestre usando EMAL, no evaluar la viabilidad de personas ni decidir ayudas. La fuente contiene agregados de municipios de mas de 20.000 habitantes, no anuncios individuales. No se sustituye un anuncio ausente por una estadistica municipal. El clasificador antiguo de perfiles sinteticos y sus metricas no acreditan resultados reales y quedan obsoletos para la entrega.

## Reproduccion

**Modelo publicado y test cerrados:** para abrir la entrega use
`python main.py --subject saa_pia_mia`; para el informe use `python main.py --pdf`.
No ejecutar la captura ni el entrenamiento siguientes para abrir la app,
generar figuras o modificar documentación. Son reproducción del procedimiento
en una salida nueva, no autorización para reseleccionar mirando el test observado.

Desde la raiz, instalar `requirements-ci.txt`, ejecutar `python scripts/capture_sources.py` y `python scripts/train_official.py`. Abrir `streamlit run app/streamlit_app.py`. Los tres notebooks `.ipynb` explican las mismas etapas con pandas, sklearn, XGBoost, matplotlib, MLflow y SHAP. Los scripts homonimos se mantienen como entradas equivalentes. Python comprobable: 3.12/3.13.

## Datos y division

Se verifican los originales mediante manifest.json. T1.1 aporta volumen de contratos y T1.2 renta media. No se usan stocks vigentes actualizados por IRAV. Se excluye Galdakao por cambio territorial. Los guiones no son ceros. No se imputan objetivos no publicados. Retardos de uno/cuatro trimestres calculados antes de excluir objetivos ausentes. Train hasta 2023, validacion 2024, test desde 2025. Es un backtest de una serie revisada, no una prueba de disponibilidad historica en tiempo real.

## Modelos

Cinco familias: regresion lineal, KNN, Random Forest, XGBoost y SVM. MLP separado: base, mayor capacidad, tanh y regularizacion. Todos comparten ColumnTransformer + SimpleImputer + StandardScaler + OneHotEncoder; TransformedTargetRegressor vuelve a convertir predicciones a euros. GridSearchCV temporal en train. MAE principal; RMSE, R2 y tiempo adicionales. Seleccion con validacion y preferencia por modelo simple en empate del 1%. Se informa tambien la persistencia donde existe lag1; no se afirma mejora sin comparacion sobre la misma cobertura.

## SMOTE y SHAP

SMOTE no tiene sentido sobre el objetivo continuo. El experimento auxiliar de subida trimestral observada compara regresion logistica con/sin SMOTE real dentro del pipeline de entrenamiento y solo con numericas. No genera etiquetas de personas. Validacion conserva la distribucion original; se registran precision, recall, F1 y matriz de confusion. SHAP se calcula solo sobre validacion con fondo de train, en euros, sin interpretacion causal.

## Test y app

Se guarda el pipeline completo en best_model.joblib. La seleccion contiene huellas del modelo y test. Streamlit evalua test una vez, escribe test_final.json y lo reutiliza; modificar modelo o test invalida el informe. La app muestra prediccion y decision de reglas. n8n solo recibe datos minimos tras consentimiento y confirma la persistencia; un fallo de red no se presenta como exito.

## Evidencias

La tabla de modelos se extrae de MLflow, no de JSON de metricas inventadas. Los resultados verificables son los del artefacto de la ejecucion correspondiente: comparativa_mlflow.csv, fuentes y huellas, graficos EDA, SHAP, test_final.json y JUnit. Las cifras de documentos y modelos JSON anteriores no deben reutilizarse. El trabajo en equipo conserva src/ como fuente unica, sincronizada a los tres bloques academicos.
