# Evidencias locales · 12 de noviembre de 2026

Los originales de la muestra están en `data/capturas_anuncios/`, sellados por
manifiesto y excluidos de normalización de Git. La unidad son 17 identidades de
anuncio en dos portales; no 17 viviendas únicas ni expedientes de jóvenes.

- `tests-final.xml` y log: 159 pruebas, cinco avisos conocidos, cero omisiones.
- `integracion-final.xml` y log: 12 pruebas con HDFS, Kafka y MongoDB reales,
  cero omisiones. Los casos CI del XML emplean fixtures declarados.
- `integracion.log`: primer intento, 10 correctas y un fallo de disponibilidad
  HDFS. Conservado como fallo, separado de la suite final correcta.
- `transporte/manifest.json`: lote observado, 31 archivos recuperados idénticos,
  638 mensajes/documentos (621 promociones + 17 anuncios). `recarga.json`
  conserva la segunda carga completa en la misma base, sin crecimiento.
- `anuncios/`: comprobación offline de HTML, campos, nulos y modalidades;
  consultas reales, explain y reentrega de 17 anuncios sin duplicados.
- `transporte-municipal.json` y `municipal/`: cinco vistas agregadas por un
  recorrido separado; las vistas no se convierten en HousingAd ni anuncios.
- `n8n-live.json`: ocho ramas con servicio real y fixtures sin datos personales.
- `app-n8n.json`: formulario de demostración con ceros, consentimiento obligatorio,
  acción persistida e idempotencia. No es un expediente real ni envía comunicaciones.
- `browser.json`, `territorio.png` y `modelo.png`: Chromium/Playwright contra
  las dos aplicaciones locales; captura del archivo de anuncios y del test conservado.
- `muestra_anuncios.png`: figura descriptiva de precios pedidos y superficies
  de esta muestra, sin salarios municipales ni entrenamiento.
- `integridad.json`: seis originales oficiales, 88 artefactos ML, test único,
  copias canónicas y 22 archivos de la nueva captura verificados.
- `codigo_validado.json`: huellas del código comprobado localmente. No afirma
  que un CI histórico haya validado esta revisión.

No se reentrenó, reseleccionó ni reevaluó el test del modelo. La prueba atómica
ejecuta 100 operaciones sobre una copia aislada; no representa intereses reales.
La captura archivada es histórica desde su fecha y no garantiza disponibilidad.

La evidencia remota de Windows/Linux se registra por commit en `docs/CONTINUAR.md`
después del push; la existencia del workflow no se considera un resultado.
