# Guion oral SAA PIA y MIA

## Ensayo de quince minutos

La rúbrica fija 15 minutos por pareja. Después cada alumno responde tres preguntas: una de SAA, una de PIA y una de MIA. A y B son una propuesta de reparto; los dos estudiamos todo. Ensayamos con el reloj sin pararlo.

Llevamos abiertos la presentación, la app en http://localhost:8501 y el workflow n8n. Los notebooks ejecutados y las tablas quedan preparados para preguntas. No entrenamos ni repetimos la evaluación del test. Las capturas del formulario usan un caso inventado.

Este guion es para prepararnos y no se incluye en el ZIP de la profesora.

| Tiempo | Persona | Diapositiva | Idea principal |
|---|---|---|---|
| 0:00 a 1:00 | A | 1 | Qué necesidad queremos cubrir |
| 1:00 a 2:00 | A | 2 | Qué representa cada dato |
| 2:00 a 3:00 | A | 3 | Por qué comparar con la renta anterior |
| 3:00 a 4:00 | A | 4 | Cómo evitamos mirar el futuro |
| 4:00 a 5:30 | A | 5 | Qué alternativas probamos |
| 5:30 a 7:00 | B | 6 | Por qué elegimos esta MLP |
| 7:00 a 8:30 | B | 7 | Qué explica el modelo y cuánto se equivoca |
| 8:30 a 10:00 | B | 8 | Caso ficticio en la aplicación |
| 10:00 a 11:15 | B | 9 | Motivo de la orientación |
| 11:15 a 13:00 | A | 10 | Permiso y acción local |
| 13:00 a 14:00 | A | 11 | Comprobar guardado y repetición |
| 14:00 a 15:00 | Ambos | 12 | Resultado, límites y mejoras |

## Diapositivas 1 y 2 Qué hemos construido y con qué datos

A: «Hemos creado una referencia para ayudar a orientar sobre vivienda. Primero estimamos la renta media de un municipio. Después la comparamos con lo que declara la persona y explicamos una recomendación».

«Tenemos 768 observaciones de 19 municipios. Una fila es un municipio en un trimestre, no un piso. De esas filas, 601 se usan para entrenar. El modelo aprende alquileres medios; el sueldo se utiliza después».

Señalamos el esquema y las tarjetas. Si preguntan, es una regresión supervisada: aprendemos con ejemplos que tienen una renta objetivo conocida. Los 17 anuncios son del otro bloque y no forman el entrenamiento.

## Diapositiva 3 Por qué miramos primero los datos

A: «Aquí vemos que la renta de un trimestre se parece mucho a la anterior. Eso nos hizo pensar que no bastaba con probar modelos: también había que comparar con una solución muy sencilla, usar la última renta conocida».

Señalamos la nube de puntos. El gráfico usa entrenamiento. Para ampliar, tenemos los cinco gráficos y sus conclusiones en `entrega_ml/notebooks_ejecutados/01_eda.ipynb`. Los valores no publicados no se convierten en alquileres de cero euros.

## Diapositiva 4 Cómo hacemos una comparación justa

A: «Separamos por fechas: 601 filas para aprender, 75 para comparar modelos y 92 para la prueba final. Así intentamos reproducir la idea de aprender del pasado y predecir después».

«Guardamos la preparación de los datos junto al modelo para hacer los mismos pasos cuando llegue un caso nuevo». Si preguntan por fugas, explicamos que imputación, escalado y codificación se ajustan dentro del pipeline usando entrenamiento; el test no se usa para elegir.

## Diapositiva 5 Por qué probamos varias opciones

A: «No sabíamos de antemano cuál funcionaría mejor. Probamos cinco familias y cuatro versiones de una red MLP. Cambiamos su estructura o su forma de aprender para ver si esos cambios ayudaban».

«Guardamos los experimentos en MLflow y comparamos el error de validación en euros, porque es una medida que podemos interpretar». Tenemos preparada `entrega_ml/resultados/comparativa_mlflow.csv` y la captura MLflow. Si preguntan por las variantes: base de 32, dos capas 64/32, tanh y regularización alpha 0,01. Usamos sklearn, no Keras.

## Diapositiva 6 Por qué conservamos ese modelo

B: «La MLP de dos capas fue la mejor en validación, con un error medio de 24,20 euros. Pero usar la renta anterior ya daba 24,63. La mejora es de unos 43 céntimos, así que no la presentamos como un salto enorme».

Señalamos las dos barras, que empiezan en cero. Lo relevante es justificar la elección y reconocer lo ajustado del resultado. En preguntas podemos explicar el sobreajuste de KNN: casi no falla en entrenamiento y empeora mucho en validación.

## Diapositiva 7 Cómo entendemos el resultado

B: «SHAP nos ayuda a ver qué información pesa más en las predicciones. La renta anterior es la más importante. Eso encaja con lo que vimos antes, aunque no demuestra una relación de causa y efecto».

«En la prueba final el error absoluto medio fue de 28,67 euros. Es un promedio sobre rentas municipales: no significa que cualquier piso vaya a estar dentro de ese margen». Si piden más métricas, abrimos el informe conservado: RMSE 37,93 y R² 0,9189. R² no es un porcentaje de aciertos. No reevaluamos test.

## Diapositiva 8 Qué introducimos en la app

B: «Usamos un ejemplo inventado de Bilbao: 25 años, 1.500 euros netos al mes y 500 de alquiler, sin deudas. Su alquiler supone un tercio del ingreso: 33,33 %. La renta de referencia del modelo se muestra aparte».

Para repetirlo: ingreso anual computable 18.000, renta total 500, ahorro 2.000, entrada 1.000, unidad individual y contrato no compartido. Las siete comprobaciones documentales se marcan verdaderas solo porque así definimos este caso ficticio. La captura enseña el formulario real, no un diseño de ejemplo.

## Diapositiva 9 Por qué sale esa orientación

B: «La aplicación no suelta una recomendación sin explicar nada. Tiene diez reglas ordenadas. En este caso, la renta municipal de referencia supera el 40 % del ingreso y por eso propone comparar municipios y presupuesto».

«El sueldo no ha servido para entrenar ni para predecir la renta. Entra después, en las reglas». Leemos la referencia real que aparece en pantalla y su periodo, 2026 T2. En la captura actual de Bilbao es aproximadamente 1.013,84 euros y el esfuerzo de referencia es 67,59 %. El contrato declarado sigue siendo 500 euros y 33,33 %.

Si preguntan por prioridades, seguridad es 100 y R_REFERENCIA es 65. Una regla anterior puede cambiar la decisión. El 40 % es un umbral interno de orientación, no un requisito legal para conceder ayudas.

## Diapositivas 10 y 11 Qué ocurre después del permiso

A: «Pedimos consentimiento antes de enviar la decisión. n8n recibe lo mínimo necesario y prepara una ficha según la orientación. No enviamos el sueldo ni el perfil completo».

Pulsamos Registrar accion con los servicios preparados. Abrimos la ficha de `data/acciones_n8n/`. «Ahora comprobamos que existe. Si repetimos el mismo envío, seguimos teniendo una sola ficha. Si el guardado falla, la aplicación debe avisar y no decir que ha salido bien».

Repetimos el botón sin volver a enviar el formulario, para conservar el mismo identificador de evento. La acción es local: no manda SMS ni resuelve solicitudes de ayudas. Para preguntas quedan las ocho ramas de `n8n/flujo.json` y la confirmación de persistencia. Si el servicio falla, mostramos la evidencia del 12 de noviembre indicando que es histórica.

## Diapositiva 12 Cierre dentro de tiempo

Ambos: «Hemos unido una referencia municipal, una explicación y una acción comprobable. Nos quedamos con que el sistema orienta, pero su mejora frente a usar la renta anterior es pequeña y solo cubre 19 municipios. Mejoraríamos la actualización de datos y la información sobre incertidumbre».

Cerramos antes de los 15 minutos. Los detalles de SMOTE y de implementación quedan preparados para las preguntas; no añadimos una explicación nueva en el último minuto.

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
