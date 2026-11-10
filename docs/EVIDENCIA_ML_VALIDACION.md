# Evidencia de validacion del bloque ML

## Ejecucion comprobada antes de publicar el codigo

- GitHub Actions: https://github.com/markelalvarez0/Reto-1/actions/runs/42855647062
- Job: 129967813996, completed / success, 10-11-2026.
- Base: 3d5c2a42507c986db1045015568381accb9302fc.
- Propuesta exacta aplicada al runner: arbol 476ba0404071ab4a5a113d7c851427963ae6c14d. Sus 21 archivos se verificaron por identidad Git y se sincronizaron las copias de src antes de probar.
- Version anterior: 84 passed. Propuesta: 99 passed, 5 warnings in 6.05s. No pruebas omitidas.
- Avisos: deprecaciones de Pydantic en MLflow y convergencia en los mini-tests heredados limitados a 5/10 iteraciones. Los nueve entrenamientos sobre EMAL no registraron avisos de entrenamiento.
- Se corrigio una incompatibilidad de MLflow 2.x con SQLAlchemy 2.1 fijando SQLAlchemy <2.1. No se eliminaron pruebas.

## Procedencia y particion

Captura oficial: https://github.com/markelalvarez0/Reto-1/actions/runs/42835919323

Archivo: emal_municipios.xlsx. SHA-256: f4d27d4e8e9bd3688d4e7a454026a4a0884073dc73e3fc1c0da4891a1ad1af5c.

Fuente: https://opendata.euskadi.eus/contenidos/estadistica/122417_emal_tablas_estad/opendata/EMAL.-Barrios-Municipios.-2016-2026_es.xlsx

768 observaciones municipio/trimestre de 19 municipios: 601 de entrenamiento hasta 2023, 75 de validacion de 2024 y 92 reservadas desde 2025. Se excluyeron 11 objetivos no publicados. La fuente es una serie estadistica revisada, NO anuncios individuales ni expedientes de personas jovenes. La evaluacion es retrospectiva con retardos observados; no una prediccion multitrimestre sin datos intermedios.

## Comparacion en validacion (EUR de renta media municipal)

| Modelo | MAE | RMSE | R2 |
|---|---:|---:|---:|
| MLP dos capas | 24.1970 | 31.8597 | 0.9370 |
| Random Forest | 25.1507 | 34.7620 | 0.9250 |
| MLP regularizada | 25.4173 | 34.0273 | 0.9282 |
| MLP base | 25.7799 | 34.3755 | 0.9267 |
| XGBoost | 26.5234 | 37.0516 | 0.9148 |
| Regresion lineal | 31.1665 | 40.5837 | 0.8978 |
| MLP tanh | 35.1592 | 50.7876 | 0.8400 |
| SVM | 37.8630 | 55.5557 | 0.8085 |
| KNN | 51.5196 | 60.8912 | 0.7700 |

Seleccion: MLP dos capas, run MLflow bcc44862768c4488ac8a04b41ece5efa. Baseline de persistencia: MAE 24.6267 EUR. La mejora es pequena (aproximadamente 0.43 EUR); no justifica afirmar una superioridad general o una utilidad individual demostrada. KNN muestra un error casi nulo en train y el mayor en validacion, compatible con sobreajuste.

El experimento auxiliar de subida trimestral observada comparo SMOTE solo en train: F1 sin SMOTE 0.8254 y con SMOTE 0.8167; accuracy 0.7067 en ambos. No se afirma una mejora universal. No se aplica SMOTE a la renta continua.

SHAP real: 30 filas de validacion, fondo de 30 filas de train, algoritmo permutation. Sus contribuciones estan en EUR y no prueban causalidad.

## Artefactos y limites

Artefacto validacion-propuesta-ml: https://github.com/markelalvarez0/Reto-1/actions/runs/42855647062/artifacts/13782292743

SHA-256 ZIP: bfda0f4aaa7cac793cf1d8e217a0bc854341af16f49207cbd115547f8b9d7b6d.

Contiene registros, XML de pruebas, particiones, modelo, MLflow SQLite y sus artefactos, EDA, SHAP y comparativas. El test final sigue reservado; no hay metricas finales de test en esta evidencia. La ejecucion interactiva de Streamlit y los notebooks completos se verifican por separado. Esta evidencia NO certifica la entrega del proyecto entero.
