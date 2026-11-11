# Adquisición: evidencias locales

Base de trabajo 8685bbe. `codigo.json` identifica los archivos probados antes
del commit, sin atribuirles un CI remoto del incremento anterior.

- tests.xml: 153 pruebas, ninguna omitida. Las de scraping usan HTML sintético
  declarado y sesiones HTTP simuladas; no son capturas reales de portales.
- integracion.xml: cinco pruebas con HDFS, Kafka y MongoDB reales. Los anuncios
  transportados del caso oficial son promociones observadas. Un HTML auxiliar
  `fixture_integridad.html` solo comprueba que HDFS conserva originales adicionales;
  no es una captura ni un anuncio. El resto distingue sus fixtures como antes.
- intento_real.json: la captura en esta máquina terminó incompleta por CONNECT
  403 en ambos robots.txt, con cero anuncios. No se generó vivienda_scraping.json.
- fuentes.xml y resumen_fuentes.json: repetición del caso oficial después de
  etiquetar explícitamente el HTML auxiliar de prueba en el informe.

La integridad de las capturas oficiales, artefactos ML y evaluación única se
mantiene mediante `scripts/audit_project.py`. No se reentrenó ni reevaluó test.
