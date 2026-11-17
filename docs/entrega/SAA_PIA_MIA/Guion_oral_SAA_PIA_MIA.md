# Guion oral SAA PIA y MIA

## Ensayo de quince minutos

La rúbrica fija 15 minutos por pareja y corta la exposición al llegar al límite. Después cada alumno responde tres preguntas, una de SAA, otra de PIA y otra de MIA. A y B indican una propuesta de reparto, no autoría histórica. Ambos estudiamos el proyecto completo y ensayamos con el reloj sin pararlo.

Llevamos abiertos la presentación, Streamlit en http://localhost:8501, la comparación CSV, la captura MLflow, las figuras y el workflow n8n. Abrimos los notebooks ejecutados para consultar salidas, sin ejecutar todo. No entrenamos ni volvemos a evaluar test.

| Tiempo | Persona propuesta | Diapositiva | Objetivo |
|---|---|---|---|
| 0:00 a 1:00 | A | 1 | Situar necesidad y referencia municipal |
| 1:00 a 2:00 | A | 2 | Explicar filas, objetivo y cobertura |
| 2:00 a 3:00 | A | 3 | Relacionar EDA y persistencia |
| 3:00 a 4:00 | A | 4 | Explicar pipeline y fugas |
| 4:00 a 5:30 | A | 5 | Comparar familias y MLP |
| 5:30 a 7:00 | B | 6 | Justificar elección y baseline |
| 7:00 a 8:30 | B | 7 | SHAP y test conservado |
| 8:30 a 10:00 | B | 8 | Introducir caso y dos esfuerzos |
| 10:00 a 11:15 | B | 9 | Explicar prioridad y referencia |
| 11:15 a 13:00 | A | 10 | Consentimiento y ramas n8n |
| 13:00 a 14:00 | A | 11 | Persistencia, repetición y SMOTE |
| 14:00 a 15:00 | Ambos | 12 | Límites, diferencias y conclusión |

## Diapositivas 1 y 2 No entrenamos con pisos individuales

«Hemos creado una referencia para un servicio de orientación. La IA aprende rentas medias de municipios y trimestres. El sueldo se utiliza después en las reglas; no es lo que aprende el modelo».

Explicamos regresión supervisada: cada ejemplo tiene entradas históricas y una renta objetivo conocida. Son 601 observaciones de train, 75 de validación y 92 de test, de 19 municipios. Una fila resume contratos: no permite contar pisos distintos. Los 17 anuncios pertenecen a BDA/SBD.

Mostrar: `entrega_ml/data/procedencia.json` y una fila de train.csv con INE leído como texto. No confundir la unidad mensual del importe con la frecuencia trimestral de la observación.

## Diapositivas 3 y 4 Qué hacemos para aprender sin mirar el futuro

«En el EDA vemos que la renta anterior se parece mucho a la siguiente. Por eso sería injusto celebrar un buen resultado sin compararlo con copiar la renta anterior». Señalamos la dispersión y la correlación 0,985 de train.

«Los nulos tienen motivos: faltan retardos al principio y EMAL suprime valores no publicados. No ponemos cero en el objetivo. Ajustamos la imputación dentro de train». Recorremos las ramas de `src/pipeline.py` y los folds por trimestres de `src/ml_data.py`. El pipeline guardado contiene las transformaciones y el regresor.

Mostrar: `entrega_ml/notebooks_ejecutados/01_eda.ipynb` con sus cinco gráficos y conclusiones, y código sin ejecutarlo.

## Diapositivas 5 y 6 Por qué conservamos este modelo

Nombramos las cinco familias y explicamos un contraste: lineal como referencia sencilla, árboles para no linealidad, KNN por proximidad y SVM por margen. Después explicamos base MLP de 32, dos capas 64/32, tanh y alpha 0,01. No afirmamos que sea Keras.

Abrimos `comparativa_mlflow.csv` y la captura MLflow. «Elegimos con MAE de validación porque se entiende en euros. Dos capas obtiene 24,20 €, pero persistencia ya obtiene 24,63 €. Mejoramos unos 43 céntimos; no es una ventaja enorme». Señalamos el casi cero en train de KNN y sus 51,52 € en validación para explicar sobreajuste.

Si preguntan por tiempo, aclaramos que es el del entrenamiento histórico y del entorno registrado. Mostrar `entrega_ml/notebooks_ejecutados/02_entrenamiento_modelos.ipynb`.

## Diapositiva 7 Qué significan SHAP y el test

«Las mayores contribuciones medias son renta anterior, renta de hace cuatro trimestres y año. SHAP describe cómo usa el modelo esas entradas; no demuestra que sean causas». Son 30 filas de validación y fondo de 30 de train.

Abrimos el gráfico real frente a predicho en la pestaña Test reservado. Leemos MAE 28,67 €, RMSE 37,93 € y R² 0,9189. «R² no es porcentaje de aciertos. Este error es de renta media municipal, no de un piso». Mostramos `docs/TEST_FINAL_EMAL.json`, con una evaluación, sin tocar ningún botón de evaluación ni borrar el informe.

## Diapositivas 8 y 9 Caso ficticio y reglas

Preparamos Bilbao, 25 años, ingreso 1.500 €, anual computable 18.000 €, alquiler y renta total 500 €, deudas 0 €, ahorro 2.000 € y entrada 1.000 €. Unidad individual y sin compartir. Para este caso inventado marcamos las siete comprobaciones documentales verdaderas.

«El modelo no usa este sueldo para predecir. Produce una referencia municipal para 2026 T2 y después las reglas comparan». Leemos la predicción real de pantalla y el 33,33 % de esfuerzo declarado. Explicamos que esfuerzo de referencia divide la predicción entre el ingreso y supone pagarla íntegra.

Abrimos `src/reglas.py`. Seguridad tiene prioridad 100; R_REFERENCIA 65 interviene cuando la referencia supera el 40 % del ingreso y no salta antes otra regla. El ejemplo 600/1.600 es contrafactual con valores puestos por nosotros, no dos predicciones del modelo. No cambiamos los artefactos para forzar una pantalla.

## Diapositivas 10 y 11 Del permiso a una ficha

«Sin consentimiento no enviamos nada. Después enviamos decisión, regla y referencia, con un identificador de evento; no el sueldo ni el perfil». Mostramos las ocho ramas de `n8n/flujo.json` y abrimos la acción local.

Pulsamos Registrar accion, comprobamos la confirmación y abrimos el JSON de `data/acciones_n8n/`. Repetimos el mismo botón sin crear otro formulario y comprobamos mismo UUID y una sola ficha. La app no puede decir éxito solo porque recibió un HTTP 200; tiene que confirmarse persistencia.

En la última parte de este minuto explicamos SMOTE: «Lo probamos aparte para clasificar si sube la renta. El F1 baja de 0,8254 a 0,8167; no mejora por el hecho de balancear». La matriz está en `comparacion_smote.json`. No mezclamos ese F1 con la regresión principal.

## Diapositiva 12 Cierre dentro de tiempo

«Tenemos una referencia municipal, una orientación que se puede explicar y una acción local comprobada. No tenemos una tasación, una evaluación de solvencia ni un trámite de ayudas. La mejora frente a persistencia es pequeña y los datos deben actualizarse con versiones nuevas».

Indicamos MLP sklearn frente a Keras y que la novedad la valora el profesorado. Cerramos antes de 15:00. Si un servicio falla, mostramos la evidencia fechada y continuamos; no fingimos una ejecución correcta ni consumimos el tiempo instalando dependencias.

## Preguntas individuales que ensayamos ambos

| Asignatura y pregunta | Respuesta basada en el proyecto | Dónde enseñarlo |
|---|---|---|
| SAA: qué predice y por qué es regresión | Una renta media mensual por municipio y trimestre, continua y observada en EMAL | src/ml_data.py, TARGET |
| SAA: por qué no basta R² alto | La persistencia ya da MAE 24,63 €; el elegido 24,20 €. R² no mide aciertos | models/selection.json |
| SAA: cómo evitamos fugas | Tiempo ordenado, retardos previos, folds por periodo y ajuste de transformaciones dentro del pipeline | temporal_folds y src/pipeline.py |
| SAA: qué pasó con SMOTE | Es auxiliar, solo train; mejora precisión y baja recall y F1. No se aplica al objetivo continuo | resultados/comparacion_smote.json |
| PIA: qué incluye joblib | Preprocesado ajustado y modelo con transformación del objetivo | src/ml_workflow.py, construcción Pipeline |
| PIA: por qué OneHotEncoder | Codifica territorio sin tratar los INE como magnitudes; tolerar desconocidos no garantiza cobertura | src/pipeline.py |
| PIA: cómo sabemos qué modelo se guardó | Selección, run MLflow y huellas de modelo y test conservadas | entrega_ml/models/selection.json |
| PIA: abrir test lo calcula otra vez | Si existe informe y coinciden huellas, la función devuelve el existente | evaluate_test_once en src/ml_workflow.py |
| MIA: cambia algo la predicción | R_REFERENCIA usa el esfuerzo de referencia y puede cambiar la orientación manteniendo el contrato | src/reglas.py y CIERRE_RUBRICA.md |
| MIA: qué hace seguridad | Prioridad 100 pide revisar datos inválidos o fuera de cobertura | R_SEGURIDAD |
| MIA: cómo evitamos duplicados | Mismo UUID y contenido devuelve ficha existente; cambiar contenido con ese UUID se rechaza | scripts/action_server.py |
| MIA: realmente concede una ayuda | No, crea una ficha local para revisar; la administración decide derechos | n8n/flujo.json y aviso de la decisión |

Las rutas models y resultados abreviadas pertenecen a `entrega_ml/`; CIERRE_RUBRICA.md pertenece a `docs/`.
