# Punto de reanudación · 10 de noviembre de 2026

El usuario ha pedido pausar hasta mañana. Continuar desde este checkpoint,
sin reiniciar la auditoría ni volver a entrenar el modelo conservado.

## Objetivo y decisiones confirmadas

Terminar el proyecto interdisciplinar «Acceso a la vivienda para jóvenes en
Euskadi», conforme a los enunciados BDA/SBD y SAA/PIA/MIA 2026–27, y a los
ejercicios del curso. El usuario aprobó la Fase 1 y autorizó desarrollo modular.
Eligió **predecir alquileres con datos reales y aplicar reglas al perfil del
joven**, frente a la clasificación sintética de viabilidad.

El modelo ya conservado en `dev-jon` predice renta media municipal trimestral
EMAL. No predice el precio exacto de un inmueble ni la solvencia de una persona.
Mantener esa unidad en gráficos, app, conclusiones y documentación.

## Estado de Git y trabajo previo encontrado

La auditoría inicial se hizo sobre `main` en `6e279a4`. Al empezar desarrollo,
se encontró mucho trabajo posterior en `origin/dev-jon`, base `4ba6937`.
Se hizo checkout de esa rama y se conservaron sus cambios: modelos estándar,
datos oficiales, reglas, n8n, pruebas y evidencias. No atribuir ese trabajo previo
al nuevo incremento. `AGENTS.md` contiene alcance antiguo de Fase 1; prevalece
la petición explícita del usuario de completar ambos bloques.

Se trabaja en `dev-jon` (configuración local `git config dev.branch dev-jon`).
No se integra el conjunto pendiente en `test`/`main` durante esta pausa. Antes
de continuar, consultar `git status`, `git fetch` y cambios remotos para conservar
el trabajo del compañero. No forzar pushes ni resetear ramas.

## Incremento guardado en esta sesión

1. Portal `main.py`: rutas desde la raíz, propagación de códigos de error,
   suite completa, apertura directa de Streamlit sin entrenar. BDA `--visual`
   abre el nuevo visor territorial. El PDF histórico se rechaza con explicación.
2. Auditoría `scripts/audit_project.py`: seis originales, 88 artefactos ML,
   correspondencia del test sellado y sincronización de las copias de `src/`.
   Recoge todos los errores; no deserializa ni ejecuta modelos.
3. `src/municipal_analysis.py`: carga idempotente de 768 observaciones EMAL en
   `rentas_emal` y referencia OVJ en `contextos_ovj`; tres agregaciones reales
   MongoDB y salidas para comparación, serie y resumen territorial.
4. `scripts/analyze_municipal.py`: exporta JSON con manifiesto SHA-256. Datos
   de 2024 se comparan con el salario OVJ de 2024; se rechazan años incompatibles.
   La opción `--simulate-db` identifica explícitamente la base simulada.
5. `app/territorio.py`: 18 municipios publicados en 2024 T4, seis indicadores,
   gráficos, descarga CSV y mapa con coordenadas observadas de promociones Visesa.
   El esfuerzo es un escenario con salario autonómico de 1.564 €/mes, no salario
   municipal ni regla legal. Las promociones no equivalen a viviendas disponibles.
6. Actualización de `uv.lock` y extra `dev` para instalación reproducible.
7. Pruebas nuevas de lanzador, integridad, análisis y MongoDB real.

## Verificación realizada

- `python main.py --test -q`: **124 passed**, cinco avisos de librerías/mini-tests.
- Integración MongoDB existente: **6 passed** con mongod real.
- Nueva integración EMAL/OVJ: **1 passed** con mongod real, incluida recarga.
- `python main.py --audit --json`: cuatro controles correctos.
- `uv sync --locked --extra dev` y `uv pip check`: correctos.
- `scripts/sync_sources.py --check`: copias sincronizadas.
- AppTest: app ML abre leyendo el test conservado; visor territorial funciona
  incluso sin municipios seleccionados.
- Chromium/Playwright: visor con tres tablas y un mapa, sin errores JavaScript.
  No interpretar esto como garantía de disponibilidad de todas las teselas externas.
- Preparación BDA de fuentes conservadas: 621 registros aceptados, dos rechazados
  por municipio ambiguo; no se sustituye por Bilbao.
- Los originales y los 88 artefactos ML mantienen sus hashes. **No se reentrenó
  ni se volvió a calcular el test del modelo publicado.**

La captura del navegador está en `/workspace/audit-reto1/territorio-browser.png`
en esta máquina. Los resultados regenerables están en `data/analisis_municipal/`
y no se versionan; generarlos otra vez si se restaura un checkout limpio.

## Arranque para continuar

Desde la raíz con Python 3.12:

```bash
uv sync --locked --extra dev
uv run --no-sync python main.py --audit --json
uv run --no-sync python scripts/sync_sources.py --check
uv run --no-sync python main.py --subject bda_sbd --prepare-only
```

En esta máquina se creó el contenedor temporal `reto1-audit-mongo`, MongoDB 7,
puerto local **27018**. Comprobar primero su estado; arrancarlo si está detenido.
En otra máquina preparar MongoDB local o configurar `MONGO_URI`.

```bash
MONGO_URI=mongodb://127.0.0.1:27018 uv run --no-sync python scripts/analyze_municipal.py
uv run --no-sync python main.py --subject bda_sbd --visual --server.port=8502
uv run --no-sync python main.py --subject saa_pia_mia
MONGO_INTEGRATION_URI=mongodb://127.0.0.1:27018 uv run --no-sync python -m pytest integration_tests/test_mongodb_live.py integration_tests/test_municipal_live.py -q
```

No asumir que los procesos siguen vivos tras la pausa. No ejecutar los notebooks
o scripts históricos de entrenamiento para abrir la app. El modelo elegido
`MLP_2_capas` y su evaluación única están en `entrega_ml/` y `docs/TEST_FINAL_EMAL.json`.

## Siguiente orden de trabajo

1. Revisar este incremento y las ejecuciones CI que produzca el push; corregir
   cualquier fallo real sin modificar resultados para que parezcan correctos.
2. Cerrar la ingesta pendiente: scraping verificable de alquiler libre, datos
   brutos y procedencia, respetando acceso y límites de las fuentes. La captura
   de un indicador OVJ no sustituye scraping de anuncios. No inventar registros
   para llenar una tabla ni afirmar que una promoción es un alquiler disponible.
3. Integrar el análisis territorial con el recorrido HDFS → Kafka → MongoDB y
   conservar evidencias de los originales y derivados de extremo a extremo.
   Hay evidencia previa de servicios reales en CI; no presentarla como una nueva
   ejecución local. Ver `docs/BDA_ESTADO.md` e `integration_tests/`.
4. Conciliar los ejercicios con la implementación actual. Los ejercicios nuevos
   usan Keras para MLP y confluent_kafka/hdfs.InsecureClient para transporte;
   la versión publicada usa MLP de sklearn y otros adaptadores. Registrar esta
   diferencia. Si se añade una implementación docente alternativa, no reabrir
   selección ni mejorar resultados mirando el test ya observado.
5. Unificar README y documentos de ambos bloques, reconstruir los JSON/código
   cortados del PDF y regenerar el informe desde resultados comprobados. Eliminar
   afirmaciones históricas de XGBoost ganador, métricas ficticias, salarios
   municipales inventados y concesiones automáticas de ayudas.
6. Revisar el caso completo en Streamlit → reglas → n8n → acción local con
   confirmación e idempotencia. Las pruebas no deben enviar mensajes reales a
   administraciones ni personas. La app orienta; no concede ni deniega ayudas.
7. Preparar entrega por rúbrica, capturas, explicación de límites y defensa de
   15 minutos. Tras validación integral, integrar de forma normal en `test` y
   `main` según AGENTS.md, conservando ramas y trabajo ajeno.

## Documentación y adjuntos revisados

Leer `docs/ESTADO_ENTREGA.md`, `docs/BDA_ESTADO.md`, `docs/METODOLOGIA_ML.md`,
README y las evidencias. La documentación histórica no es fuente de resultados
actuales si contradice artefactos y ejecuciones.

Los adjuntos se descargaron en `/workspace/attachments/`; las extracciones y
el inventario de ejercicios están en `/workspace/audit-reto1/` (fuera de Git).
El segundo `ejercicios2.zip` sí se abrió: 195 archivos, 59 notebooks, 84 CSV.
Sus datasets inmobiliarios son ejemplos docentes (Etxean, King County,
California, Sacramento); no acreditan expedientes personales reales de jóvenes
de Euskadi. No sustituir con ellos las fuentes oficiales EMAL ya conservadas.
