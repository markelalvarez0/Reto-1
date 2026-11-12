# Defensa de 15 minutos

Material de preparación ampliado: [manual completo](guia_defensa/Manual_completo_Reto1.pdf),
[Word editable](guia_defensa/Manual_completo_Reto1.docx),
[presentación de doce diapositivas](guia_defensa/Presentacion_15_minutos.pdf) y
[guía rápida](guia_defensa/Guia_rapida_defensa.pdf).
El manual incluye explicaciones, ejemplos comentados y 45 preguntas con el código que mostrar.
La presentación propone el reparto A/B; no atribuye autoría histórica ni acredita un ensayo humano.

Ensayar con los artefactos conservados; no entrenar ni volver a evaluar test.
No presentar una ejecución histórica como si acabara de realizarse.

| Minutos | Contenido y demostración |
|---|---|
| 0–2 | Problema, usuario y límite. Bilbao 2024T4: renta 930,31 EUR frente a salario regional OVJ de 1.564 EUR; escenario 59,48 %, no salario individual ni municipal. |
| 2–4 | Fuentes originales y manifiesto, INE y rechazos. Promociones no son ofertas disponibles. Mostrar HDFS raw/processed y recuperación idéntica. |
| 4–6 | Kafka → MongoDB: lote, procedencia, persistencia antes del offset, recarga sin duplicados. Distinguir las vistas EMAL de los mensajes HousingAd. |
| 6–8 | Comparar las tres capitales y mostrar tabla, serie y mapa. Seis indicadores; media territorial simple y cobertura limitada. |
| 8–10 | Datos y pipeline ML, división temporal 601/75/92, comparativa MLflow y MLP_2_capas frente a persistencia. Explicar la pequeña diferencia. |
| 10–12 | SHAP de validación y test sellado (MAE 28,67 EUR); abrir la app sin recalcular. Predecir un caso declarado como demostración. |
| 12–14 | Reglas por prioridad, consentimiento, n8n y ficha local. Repetir UUID para mostrar idempotencia sin enviar comunicaciones reales. |
| 14–15 | Limitaciones, requisitos pendientes y conclusión vinculada a los indicadores. Mostrar la muestra archivada verificada y explicar su sesgo y mezcla de modalidades. |

## Reproducción

Desde la raíz con Python 3.12: `uv sync --locked --extra dev`.
`python main.py --audit --json` comprueba integridad;
`python main.py --test -q` ejecuta la suite.
`python scripts/analyze_municipal.py` requiere MongoDB real en MONGO_URI;
`--simulate-db` solo es desarrollo identificado.
`python main.py --subject bda_sbd --visual` abre el visor;
`python main.py --subject saa_pia_mia` abre el modelo conservado.
`python main.py --pdf` genera un informe desde artefactos sin reentrenar.

Los servicios HDFS, Kafka, MongoDB y n8n deben arrancarse expresamente.
Ver `.github/workflows/bda-candidate.yml`, `infra/start_hdfs_ci.sh` y
`n8n/compose.yml`. Los XML con skips no acreditan integración real.

## Preguntas individuales para preparar

- ¿Por qué regresión? El objetivo observado es una renta continua agregada; no hay etiquetas personales de solvencia.
- ¿Dónde se ajustan imputadores y escaladores? En train y dentro de cada fold temporal, mediante Pipeline.
- ¿Por qué persistencia? Lag1 y objetivo tienen fuerte correlación; un modelo complejo debe compararse con esa referencia.
- ¿Por qué no usar SMOTE sobre euros? Genera muestras para clases; no corresponde al objetivo continuo. Se conserva un experimento auxiliar separado.
- ¿Por qué no cambiar a Keras tras ver test? La selección está cerrada. Los ejercicios muestran otra biblioteca, pero el enunciado no la fija.
- ¿Qué explica SHAP? Contribuciones del modelo en validación, no causalidad ni derechos administrativos.
- ¿Cuándo se confirma Kafka? Después de persistencia y verificación. Una caída previa permite reentrega e inserción idempotente.
- ¿Qué protege un índice único? La identidad de cada dato; no convierte catálogos de dos fuentes en viviendas únicas.
- ¿Qué significa el esfuerzo? Escenario renta/ingreso regional, no proporción de jóvenes capaces de emanciparse.
- ¿Qué hace n8n? Guarda acciones locales distintas con consentimiento e idempotencia; no concede ayudas.
- ¿Qué queda sin acreditar? Ensayo humano, actualización de disponibilidad de los anuncios y cualquier plataforma o integración sin evidencia actual. La captura del 12 de noviembre está conservada.

## Ensayo técnico del incremento de anuncios

En los minutos 2–4 mostrar `data/capturas_anuncios/manifest.json`, un HTML y su
metadato robots; `scripts/audit_project.py` verifica sus bytes. En los minutos 4–6
mostrar 638 mensajes recibidos (621 promociones + 17 anuncios) y recarga sin duplicados.
En los minutos 6–8 abrir la sección de anuncios del visor: 6 Bilbao, 6 Donostia y
5 Vitoria. Comparar precio pedido y superficie, sin confundirlo con EMAL.
Explicar 3 señales de temporalidad y 2 de empresas, que pueden solaparse.

Preguntas añadidas: ¿17 anuncios son 17 viviendas distintas? No: son identidades
de portal; puede haber publicación cruzada. ¿El índice aceleró el tiempo? Se
examinaron 638 frente a 4 documentos; ambos tiempos fueron 0 ms y no permiten
cuantificar aceleración. ¿Por qué dos consultas devuelven cero? No se ha observado
ascensor en los campos normalizados ni programas municipales publicados en esas
fuentes; no se rellenan con constantes. ¿El contador prueba demanda real? No: las
100 operaciones se hicieron sobre una copia aislada para demostrar atomicidad.

El guion está preparado y se ha comprobado el recorrido técnico; el ensayo oral
cronometrado y las respuestas personales corresponden al alumnado y siguen pendientes.

## Recorrido de cierre para ensayar en pareja

- Minutos 0–2 (persona A): explicar el servicio de orientación y el escenario
  Bilbao 2024 T4, con salario regional. No hablar de concesiones o solvencia.
- 2–4 (A): mostrar respuesta JSON de API EMAL y sus filtros; contraponerla a un
  anuncio HTML. Señalar municipio/trimestre frente a identidad de portal.
- 4–6 (A): mostrar los informes HDFS/Kafka/MongoDB, recuperación y recarga.
  Enseñar explain (638 frente a 4 documentos) y atomicidad sobre copia aislada.
- 6–8 (B): comparar tres capitales, separar anuncios 2026 de estadísticas 2024,
  explicar los indicadores y que una muestra de conveniencia no es un censo.
- 8–10 (B): enseñar el EDA y tabla MLflow; explicar 601/75/92, lag1, preprocesado
  en train y la pequeña diferencia frente a persistencia. No entrenar.
- 10–12 (B): SHAP de validación, test sellado leído y nuevo caso. Explicar que
  R_REFERENCIA usa la predicción para orientar, sin sustituir el contrato.
- 12–14 (A): contrastar el caso de prueba 600/1.600, mostrar consentimiento,
  ficha n8n con regla/referencia y repetir UUID. No enviar mensajes externos.
- 14–15 (ambas personas): límites, diferencias respecto a clase y conclusión.

Este reparto es un guion de ensayo, no un ensayo oral ya realizado. Practicar
con cronómetro; al llegar a 15 minutos se corta como indica el enunciado.

Preguntas individuales nuevas, con respuesta y punto del código que mostrar:

1. SAA: ¿por qué no clasificación? La etiqueta observada es renta continua
   municipal; enseñar TARGET y temporal_split en src/ml_data.py.
2. SAA: ¿qué pasa si KNN memoriza? Su MAE train casi cero contrasta con MAE val
   51,52 €; mostrar comparativa conservada y justificar el ganador sin mirar test.
3. SAA: ¿por qué sklearn y no Keras? Misma familia MLP, otra API; mostrar las
   cuatro configuraciones en regression_models. No se cambia tras abrir test.
4. PIA: ¿qué contiene joblib? Pipeline con preprocesador y regresor; mostrar
   construcción en src/ml_workflow.py y carga/inferencia de la app sin fit.
5. PIA: ¿cómo se evita repetir test? Mostrar la rama que lee test_final.json y
   verifica las huellas en evaluate_test_once, sin pulsar una nueva evaluación.
6. PIA: ¿de dónde sale la tabla? Consulta MLflow y CSV conservado; mostrar sus
   métricas train/validación y tiempo, no generar valores manualmente.
7. MIA: ¿dónde influye la predicción? R_REFERENCIA y esfuerzo_referencia_pct;
   enseñar el contrafactual de tests/test_business_rules.py.
8. MIA: ¿puede ganar sobre seguridad? No: prioridad 65 frente a 100; mostrar la
   prueba que devuelve R_SEGURIDAD incluso con una referencia alta.
9. MIA: ¿qué acción se ejecutó? Una ficha local con regla y referencia, no una
   cita concertada ni una ayuda concedida; mostrar persist_action y el JSON.
