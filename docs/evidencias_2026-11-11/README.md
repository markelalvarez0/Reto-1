# Evidencia local de la continuación del 11 de noviembre

Base remota: f107a0a0d001390299d55b8b92936899926fb72a, rama dev-jon.
Ejecución sobre cambios locales anteriores al commit. `codigo.json` identifica
por SHA-256 los archivos de implementación probados; no afirma que un CI remoto
haya ejecutado un commit todavía sin publicar.

- tests.xml: 129 pruebas, ninguna omitida; fixtures y servicios en memoria.
- mongodb.xml: siete pruebas con MongoDB 7.0 real, bases temporales.
- integracion.xml: cinco pruebas con HDFS 3.4.2 lean/Java 11, Kafka 3.9.1 y
  MongoDB real. El caso básico de transporte usa fixtures declarados; el de
  capturas usa los originales verificados y el municipal usa EMAL/OVJ observados.
- bda-resumen.json: 621 promociones, 80 municipios de catálogos; no son viviendas
  únicas ni anuncios individuales. Incluye los dos rechazos de origen.
- transporte_municipal.json: cinco vistas recuperadas de HDFS y persistidas tras
  Kafka, comparadas byte a byte. El test repite el flujo sin duplicar documentos.
- n8n-live.json: ocho ramas reales con datos de prueba y repetición idempotente.
- streamlit-n8n.json: consentimiento exigido y ficha de seguridad persistida desde
  AppTest. No contiene perfil de ninguna persona real ni envía comunicaciones.
- modelo.png y territorio.png: capturas actuales de Chromium, sin imágenes generadas.

Las salidas completas regenerables están en evidencia_bda_integracion/ y no se
versionan. Los originales y los 88 artefactos ML siguen sujetos a sus manifiestos
anteriores. No se vuelve a evaluar test para generar estas evidencias.
