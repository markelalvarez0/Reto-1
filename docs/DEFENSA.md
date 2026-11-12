# Defensa por bloques: dos presentaciones independientes

Material ampliado: [manual](guia_defensa/Manual_completo_Reto1.pdf), [Word editable](guia_defensa/Manual_completo_Reto1.docx), [guía rápida](guia_defensa/Guia_rapida_defensa.pdf).

- [Presentación BDA + SBD: diez diapositivas](guia_defensa/Presentacion_BDA_SBD.pdf).
- [Presentación SAA + PIA + MIA: doce diapositivas, 15 minutos](guia_defensa/Presentacion_SAA_PIA_MIA.pdf).

La anterior presentación que mezclaba las cinco asignaturas queda sustituida por estos dos materiales. El archivo Presentacion_15_minutos.pdf se conserva como copia de la presentación IA para mantener los enlaces anteriores.

El proyecto comparte repositorio y contexto, pero los materiales de exposición se separan en **BDA + SBD** y **SAA + PIA + MIA**. El primer PDF pide una demostración del sistema y justificación de decisiones técnicas; no fija duración. El segundo sí establece 15 minutos por pareja y tres preguntas individuales por alumno, una de cada asignatura de IA. Esta separación de materiales no determina por sí sola fechas o turnos docentes.

### Presentación BDA + SBD: diez diapositivas
| Orden | Persona propuesta | Qué explicar y enseñar |
|---|---|---|
| 1. Problema | A | Pregunta de emancipación y escenario cuantificado. |
| 2. Fuentes y unidades | A | API monetaria, HTML, promociones, INE y OVJ; distinguir sus unidades. |
| 3. Arquitectura | A | Captura → normalización → HDFS → Kafka → MongoDB → vistas. |
| 4. Transporte | A | Recuperación idéntica; 638 registros; API separada; persistencia antes del offset. |
| 5. Modelado y limpieza | B | Colecciones, referencias, embedding, nulos, duplicados y tipos. |
| 6. Consultas y agregaciones | B | Cinco consultas; tres pipelines y sus etapas; salidas para representar. |
| 7. Índice y consistencia | B | Explain 638/4, ambos tiempos 0 ms; atomicidad sobre copia aislada. |
| 8. Comparación territorial | B | Tres capitales, salario autonómico 2024 y resultados de MongoDB. |
| 9. Demostración y entrega | A | Visor, informe de transporte y reentrega; originales, código y datos en servicios. |
| 10. Límites | Ambas | Muestra pequeña, promociones no disponibles y esfuerzo de escenario. |

La duración se ajusta a lo que indique el profesorado de BDA/SBD. Este documento no inventa un límite oficial. Llevar abierto el visor territorial, JSON API, HTML, manifiestos, resumen de transporte, consultas y explain. No consumir esta exposición con modelos ML o n8n.

### Presentación SAA + PIA + MIA: doce diapositivas y 15 minutos
| Tiempo | Persona propuesta | Diapositiva y demostración |
|---|---|---|
| 0:00–1:00 | A | 1. Problema de negocio, usuario, objetivo continuo y límite. |
| 1:00–2:00 | A | 2. Dataset: 768 filas, 19 municipios y 601/75/92. |
| 2:00–3:00 | A | 3. EDA: cinco gráficos, nulos y persistencia. |
| 3:00–4:00 | A | 4. Pipeline, objeto guardado y MLflow. |
| 4:00–5:30 | A | 5. Cinco familias y MLP base más tres experimentos. |
| 5:30–7:00 | B | 6. Comparación, ganador y diferencia pequeña frente a persistencia. |
| 7:00–8:30 | B | 7. SHAP de validación, métricas y test conservado. |
| 8:30–10:00 | B | 8. Caso nuevo en Streamlit; leer periodo y referencia. |
| 10:00–11:15 | B | 9. Reglas, prioridades y contrafactual 600/1600 identificado como prueba. |
| 11:15–13:00 | A | 10. Consentimiento, webhook, ramas y ficha local. |
| 13:00–14:00 | A | 11. Recorrido y repetición del mismo UUID sin duplicados. |
| 14:00–15:00 | Ambas | 12. Diferencias con clase, límites y cierre. |

No dedicar este tiempo a explicar HDFS o Kafka en detalle: pertenecen al otro material. Llevar abierto Streamlit del modelo, MLflow o su captura, comparativa, src/reglas.py, n8n y la ficha. Ambas personas deben entender todo, aunque se repartan minutos. El reparto propuesto no acredita autoría histórica.

### Aperturas adaptadas
**BDA/SBD:** «Recogemos datos reales de vivienda y contexto salarial, conservamos su procedencia y los llevamos hasta MongoDB para comparar municipios con indicadores verificables».

**SAA/PIA/MIA:** «Aprendemos una renta media municipal a partir de EMAL y la usamos como referencia de orientación. Mostraremos cómo se transforma en una decisión explicable y una ficha local, sin resolver derechos administrativos».

### Cierre y ensayo
En BDA/SBD, concluir con lo que los indicadores permiten decir sobre municipios. En IA, concluir con la utilidad y límites de la predicción y las reglas. Ensayar cada presentación por separado y alternar preguntas fuera del bloque asignado. Para IA hacer una vuelta de 15 minutos sin detener el reloj; si n8n falla, mostrar evidencia conservada con su fecha. No entrenar ni repetir el test para defender.

El manual incluye 45 preguntas con respuestas y el archivo de evidencia que mostrar. Ensayar con los artefactos conservados; no entrenar ni reevaluar el test. No presentar una ejecución histórica como si acabara de realizarse.
