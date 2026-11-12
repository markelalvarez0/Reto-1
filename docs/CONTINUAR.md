# Continuación · 12 de noviembre de 2026

## Verificación remota del primer incremento

Publicado **1aad2c0a13ef9b158c6c3885a0346132551ca344**.
[CI actual 43241144554](https://github.com/markelalvarez0/Reto-1/actions/runs/43241144554):
Linux Success; Windows falló en integridad antes de ejecutar la suite. El checkout
convirtió finales de línea de artefactos ML sellados. Corrección: `.gitattributes`
con `-text -diff` para entrega_ml/, docs/evidencias_ml/ y TEST_FINAL_EMAL.json.
No se modificaron sus bytes, manifiestos ni hashes. No cuenta como Windows validado.

La descarga histórica de Hadoop resultó lenta localmente; la descarga oficial desde
`downloads.apache.org` completó 488 MB en unos 21 segundos y verificó la misma SHA512.
El script prefiere ahora esa distribución oficial y conserva el archivo Apache como
alternativa si la versión ya no está publicada allí, con esperas/velocidad acotadas.

Corrección publicada en **4bf7b28**. El [CI actual 43241629033](https://github.com/markelalvarez0/Reto-1/actions/runs/43241629033)
terminó **Success en Linux y Windows**: 159 pruebas, integridad, preparación BDA,
PDF y AppTest del modelo conservado. MongoDB real [43241628598](https://github.com/markelalvarez0/Reto-1/actions/runs/43241628598)
también terminó Success. Esta evidencia valida ese commit; el incremento posterior
de consultas requiere su propio CI.

## Incremento actual: anuncios reales y comprobación del lote

Base remota comprobada: `dev-jon` en c5fdd5d, `test`/`main` en 6e279a4.
No existía checkout en el entorno nuevo: se clonó `dev-jon`, sin worktree,
sin cambios ajenos locales y con dev.branch configurada solo localmente.
El entorno nuevo está operativo y la política efectiva está aplicada en modo
sin lista restrictiva. Los robots de ambos portales y api.github.com responden
200. No se reutilizó el borrador pendiente del entorno anterior ni se eludió TLS,
robots, proxy, CAPTCHA o autenticación.

- Captura final: **17 identidades de anuncio**, 9 Habitaclia y 8 Pisos.com,
  en Bilbao (6), Donostia (6), Vitoria (5). Tres por listado como máximo.
  Originales y normalizados: `data/capturas_anuncios/2026-11-12/`, 22 archivos
  verificados por el nuevo quinto control de `scripts/audit_project.py`.
- Antes se conservó un intento con URLs antiguas 404 y HTML sin interpretar;
  se corrigieron rutas, enlace de vivienda frente al de agencia, tarjetas
  completas frente a subelementos, localización bilingüe/paréntesis y m².
  Los fixtures estructurales nuevos están identificados como sintéticos.
- Tres señales de temporalidad y dos de empresas (solapables); ausencia de
  señal no acredita uso habitual. Las nueve descripciones ausentes de Habitaclia
  quedan nulas; no se reutiliza su ubicación como descripción.
- Recorrido completo **real**: 31 archivos recuperados idénticos de HDFS,
  638 mensajes publicados/recibidos y 638 registros persistidos: 621 promociones
  oficiales y 17 anuncios. Dos rechazos de Abanto en la preparación oficial,
  cero rechazos adicionales de transporte. Segunda carga completa en la misma
  base mantiene 638. Reentrega de los 17 también conserva el recuento.
- Consultas corregidas: antes la consulta Bilbao mezclaba 9 promociones con
  6 anuncios. Ahora las consultas de anuncios excluyen promociones/simulaciones
  y precios no positivos. Cinco consultas útiles devuelven 6/1/4/10/3 (la de habitaciones limita a 10);
  se conservan además los dos ceros de ascensor y programas sin rellenarlos.
- Explain real: COLLSCAN 638 documentos frente a IXSCAN 4, cuatro resultados
  iguales, ambos 0 ms; no se afirma una aceleración temporal medible.
- Atomicidad: 100 incrementos concurrentes en una copia aislada de un anuncio;
  contador 100, sin modificar el contador original ni representar demanda real.
- `scripts/analyze_rental_sample.py` reinterpreta los HTML archivados offline,
  contrasta los campos con MongoDB y exporta informe, consultas, explain y huellas.
- El visor territorial añade comparación y dispersión de la muestra verificada,
  tabla de condiciones y CSV. No mezcla precios de anuncios de 2026 con salario
  OVJ de 2024 ni con contratos EMAL. Informe/PDF y defensa actualizados.
- Añadido CI de la versión actual en Linux/Windows con uv.lock, 159 pruebas,
  integridad, preparación BDA, PDF y AppTest del modelo congelado. No recupera
  artefactos históricos ni ejecuta entrenamiento o evaluación del holdout.

## Validación en esta máquina

- 159 passed en tests/, cinco avisos conocidos, sin skips.
- 12 passed en integración HDFS/Kafka/MongoDB, sin skips.
- Primer intento de integración: 10 passed y 1 fallo al dejar de responder HDFS.
  Reiniciados NameNode/DataNode en sesiones supervisadas, sin reformatear;
  repetición de 11 pruebas correcta y suite final ampliada a 12 correcta.
- n8n 2.47.3 real: ocho ramas con persistencia e idempotencia. AppTest del
  formulario con ceros → R_SEGURIDAD → consentimiento → ficha local, repetición
  del UUID. Es un caso de prueba, no un expediente ni comunicación externa.
- AppTest territorial: cinco tablas y cero excepciones/errores.
- Chromium/Playwright sobre las dos aplicaciones reales; capturas conservadas.
- Auditoría: seis originales oficiales, 88 artefactos ML, test único y 22 archivos
  de la captura intactos; copias académicas sincronizadas.
- Los servicios son temporales de esta máquina: MongoDB 27018, Kafka 9092,
  HDFS 9870/9864, n8n 5678. Comprobar estado al reanudar; no asumir persistencia.

Evidencias: `docs/evidencias_entrega_2026-11-12/`. Los XML y los informes locales
validan este árbol de trabajo; no se etiquetan como CI remoto. No se ha entrenado,
reseleccionado ni reevaluado el test del modelo conservado.

## Próximo cierre

Subir el commit a dev-jon y comprobar el CI de esa revisión, incluido Windows.
Promover normalmente a test/main solo después de las validaciones de la versión
actual, conservando el trabajo remoto. Volver a dev-jon. El ensayo oral humano
cronometrado y las respuestas individuales siguen pendientes: el guion y el
recorrido técnico no sustituyen la intervención del alumnado.

La documentación siguiente es el historial anterior. Sus bloqueos de red y el
scraping pendiente fueron superados en el incremento descrito arriba.

---

# Continuación · 11 de noviembre de 2026

## Incremento posterior: adquisición trazable de anuncios

Publicado en **a15756c** en origin/dev-jon. La validación remota del código
corresponde a [BDA 43011875465](https://github.com/markelalvarez0/Reto-1/actions/runs/43011875465),
separada de los CI anteriores y de las pruebas locales.
Terminó **Success**, comprobado en su página pública; valida el código de
captura con fixtures y el transporte con servicios, no scraping remoto vigente.

Base 8685bbe, remota y local sin cambios ajenos al reanudar. La red sigue con
política restringida, aplicada, sin los dominios de los portales; el borrador
continúa inaccesible (INVALID_ARGUMENT). No se reemplazó una lista desconocida.

- `scripts/capture_rentals.py` prepara lotes nuevos, con estado completo/parcial
  y salida distinta de cero cuando falta alguna captura. El intento actual
  produjo cero anuncios y dos bloqueos CONNECT 403. No generó un JSON ingerible.
- Ambos scrapers usan `src/extraction/scraping_http.py`: HTTPS verificado,
  User-Agent académico, robots previos, pausas y redirecciones controladas.
  Robots desconocidos/denegados o HTML sin anuncios no equivalen a éxito.
- Se conservan bytes, URL, fecha, estado, tamaño y SHA-256 de robots y listados.
  El pipeline revalida esos originales antes de ingerir y los conserva en HDFS
  también cuando acompaña capturas oficiales. Un original alterado detiene la carga.
- Corregidos céntimos, unidades temporales, IDs dependientes de la hora y el
  municipio asumido del target. Se excluyen tipos no residenciales evidentes.
  Son selectores probados con fixtures; su vigencia requiere HTML real accesible.
- Eliminado también el fallback TLS inseguro de Udalmap. No se volvió a descargar
  ni modificar ninguna de las seis capturas oficiales o los 88 artefactos ML.
- 153 pruebas de tests/ superadas, cinco avisos conocidos. Cinco pruebas de
  servicios reales superadas. El caso de fuentes añade un HTML auxiliar declarado
  como fixture para comprobar su almacenamiento; no lo cuenta como anuncio.

Evidencias nuevas: `docs/evidencias_scraping_2026-11-11/`. Instrucciones y límites
en `docs/SCRAPING.md`. El CI de 1c7c45e acredita el incremento anterior; el CI
43011875465 de a15756c acredita por separado este código.

**Siguiente requisito externo:** habilitar www.habitaclia.com y www.pisos.com en
los ajustes de red. Después revisar condiciones/robots, capturar HTML vigente,
contrastar selectores y transportar anuncios observados. No se elude el bloqueo
ni se inventa una muestra. La promoción a test/main sigue esperando esa validación.

## Incremento actual desde f107a0a

Publicado en **1c7c45e404247e242f82099943dcf97bce277655** en origin/dev-jon.
El push disparó [CI BDA 43008668473](https://github.com/markelalvarez0/Reto-1/actions/runs/43008668473);
su estado debe comprobarse por separado de las pruebas locales de abajo.
El [CI n8n 43008668600](https://github.com/markelalvarez0/Reto-1/actions/runs/43008668600)
terminó **Success** para 1c7c45e; se comprobó en su página pública.
El CI BDA **43008668473 también terminó Success** para ese mismo commit.
Las comprobaciones del workflow exigen las pruebas municipales y transporte,
resultados no vacíos y ninguna omisión. No se descargaron sus logs privados.
Los cuatro PDF versionados se sustituyeron por el informe corregido paginado;
el adjunto maestro anterior permanece como referencia histórica del traspaso.

Se comprobó GitHub antes de editar: dev-jon seguía en
f107a0a0d001390299d55b8b92936899926fb72a; main/test en 6e279a4.
Se conservó la corrección UTF-8 y se trabajó en dev-jon con identidad local.
No se sustituyeron archivos por el ZIP adjunto ni se reentrenó el modelo.

- La ejecución 42999928204 terminó **cancelada por timeout de 30 minutos**,
  según su página pública. La API está bloqueada, no se obtuvieron logs privados.
- Workflow bda-candidate ampliado: URI explícitas, prueba municipal, exportación
  real, auditoría, transporte de vistas y validación XML sin skips ni suites vacías.
- Nuevo scripts/transport_municipal.py: manifiesto → HDFS processed → recuperación
  idéntica → Kafka → MongoDB vistas_municipales → commit de offsets. Recarga por
  archivo/huella sin duplicados. No convierte agregados en anuncios.
- Hadoop lean oficial, SHA512 conservada, descarga acotada y reutilización solo
  tras verificar archivo. Se probó en esta máquina con Java 11/HDFS reales.
- n8n usa imagen oficial de Docker Hub, misma versión; el receptor Compose se
  excluye del proxy de Internet. Se verificaron ocho ramas y formulario con
  consentimiento, confirmación e idempotencia. Solo acciones locales de prueba.
- main.py --pdf genera informe vigente desde artefactos verificados, Markdown,
  figuras y manifiesto; los generadores históricos delegan en él. Se comprobó
  extracción de texto y una página renderizada, sin fragmentos cortados.
- Contraste de los PDF, README docente y ambos ZIP en docs/CONTRASTE_DOCENTE.md.
  MLP sklearn y clientes de transporte distintos de los ejemplos: el enunciado
  no fija esas bibliotecas. No se cambia la selección observando test.
- Guion de defensa de 15 minutos y capturas actuales de ambos visores.

Validación de este incremento local, previa al commit:

1. 129 passed en tests/, cinco avisos conocidos; sin errores ni skips.
2. 7 passed con MongoDB real (seis anteriores + una municipal).
3. 5 passed con HDFS/Kafka/MongoDB reales, incluidas capturas y recarga de vistas.
4. 621 registros transportados y persistidos; 2 rechazos de los 623 originales.
5. 18 municipios comparados, 768 observaciones; cinco vistas transportadas.
6. Ocho ramas n8n; AppTest formulario → seguridad → consentimiento → ficha real,
   repetición sin cambios. Las dos apps abren en AppTest y Chromium sin excepciones.
7. Auditoría: seis originales, 88 artefactos ML y test único intactos; copias iguales.

Evidencias: docs/evidencias_2026-11-11/. El resumen indica cambios locales antes
del commit; **no afirma checkout limpio ni CI remoto**. El manifiesto de código
permite identificar los archivos probados. Consultar git log de dev-jon para el
commit de publicación de este incremento.

## Pendientes que bloquean declarar la entrega integral

- Scraping de anuncios individuales: CONNECT a www.habitaclia.com y www.pisos.com
  devuelve 403 de la red. Habilitar esos dominios en ajustes, comprobar robots y
  condiciones y recién entonces capturar. No se inventaron registros.
- api.github.com devuelve Forbidden. La web pública permite consultar estados,
  pero no se dispone de API para dispatch/logs autenticados. Git HTTPS sí funciona.
- La herramienta de borradores sigue devolviendo INVALID_ARGUMENT; no se afirma
  haber guardado nuevos permisos. No pasar secretos en chat ni repetir tokens.
- CI BDA y n8n del commit 1c7c45e correctos; no confundir el timeout anterior ni
  las pruebas locales con esa ejecución. Integrar en test/main solo tras validación
  integral, sin force-push ni scripts de publicación automática.
- Ensayo humano y preguntas individuales. El PDF declara el scraping pendiente.

El resto del checkpoint se conserva como historial; las tareas terminadas arriba
prevalecen sobre la lista antigua de pendientes.

# Historial · punto de reanudación del 10 de noviembre de 2026

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
