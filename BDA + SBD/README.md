# Reto 1 · BDA + SBD · Vivienda joven en Euskadi

Actualización del 12 de noviembre de 2026: [17 anuncios archivados](../docs/RESULTADOS_ANUNCIOS.md)
de dos portales y tres capitales, transportados con HDFS/Kafka/MongoDB reales
junto con 621 promociones. El visor muestra ambos conjuntos con sus unidades
y límites. [Evidencias de la versión actual](../docs/evidencias_entrega_2026-11-12/).

## Pregunta y limites

El proyecto estudia que informacion verificable puede aportar la ingesta de datos publicos a la orientacion sobre vivienda juvenil. **No concede ayudas ni demuestra que una persona pueda independizarse a partir de una media municipal.**

Se distinguen promociones oficiales, anuncios individuales, estadisticas agregadas de alquiler y referencias salariales. No son observaciones intercambiables. Los antiguos porcentajes de esfuerzo, salarios municipales, ahorros y aceleraciones de consultas que no tenian evidencia reproducible se han retirado de este README.

## BDA: lo implementado

- Cliente REST de Visesa y adaptador del CSV oficial de Etxebide. El JSON verificado usa `rows`; se mantiene compatibilidad con ese contrato. Las promociones se identifican como `tipo_registro=promocion`.
- Catalogo completo de las tres hojas INE de Euskadi, codigos de cinco digitos y nombres normalizados sin coincidencias parciales. Los nombres historicos de Etxebide conservan su codigo y denominacion de origen.
- Capturas originales con URL, fecha y SHA-256. Los originales quedan excluidos de la conversion automatica de saltos de linea de Git.
- HDFS: originales y procesados separados, recuperacion y comparacion de bytes/huellas.
- Kafka: productor y consumidor con `HousingAd`, procedencia y lote de ingesta. El consumidor persiste antes de confirmar el desplazamiento.
- Contexto OVJ extraido del HTML capturado: territorio, periodo, tramo de edad, unidad y pagas extra. No se copia como si fuera un salario municipal.

La prueba end-to-end con capturas oficiales se describe en [BDA_ESTADO.md](../docs/BDA_ESTADO.md). Su resultado medido y los rechazos estan en [resumen de evidencia](../docs/evidencias_bda/resumen.json). La existencia del workflow no demuestra exito: consultar sus ejecuciones y el XML de resultados.

## SBD: interfaces disponibles y comprobaciones separadas

La carga en MongoDB utiliza `viviendas` y `municipios`, unidas por `codigo_municipio`. Se conservan fuente, identificador, procedencia, tipo de registro y valores desconocidos como nulos. Las recargas son idempotentes y no borran las colecciones ni los contadores de interes.

Los modulos canonicos `src/database/` implementan limpieza, cinco consultas, tres agregaciones, indices con `explain` y operaciones atomicas. Hay pruebas de MongoDB real separadas de `mongomock`.

El catalogo de promociones se exporta por municipio y fuente, pero sus registros **no se cuentan como anuncios de alquiler individual**. Sin anuncios con renta y salarios municipales observados, las estadisticas de mercado y esfuerzo pueden estar vacias. Ese vacio no se rellena con datos de ejemplo.

## Como ejecutarlo

Desde la raiz del repositorio, con Python 3.12:

```bash
python -m pip install -r requirements-ci.txt
python -m pytest tests/ -q
python scripts/sync_sources.py --check

# Validar y preparar las capturas sin necesitar servicios.
python "BDA + SBD/main.py" --prepare-only

# Recorrido completo con HDFS, Kafka y MongoDB reales ya levantados.
python "BDA + SBD/main.py" --pipeline

# Alternativa equivalente desde el menu de la raiz.
python main.py --subject bda_sbd --pipeline

# Solo para una demostracion identificada como sintetica.
python scripts/run_pipeline.py --demo
```

La configuracion de conexiones usa `MONGO_URI`, `MONGO_DB`, `HDFS_NAMENODE_HOST`, `HDFS_NAMENODE_PORT`, `HDFS_USER`, `KAFKA_BOOTSTRAP_SERVERS` y `KAFKA_TOPIC`. El pipeline pasa explicitamente modo real o demo: una caida de servicios no activa una simulacion silenciosa.

El arranque de esta carpeta delega en `scripts/run_pipeline.py`; ya no utiliza metodos antiguos como `fetch_vivienda_data()` o constructores con `storage_dir` que no existen. `src/` en la raiz es la fuente de verdad y se sincroniza con las carpetas de asignaturas.

## Pendiente antes de la entrega global

Todavia hay que acreditar una muestra real y vigente de anuncios mediante scraping, validar la fuente de indicadores municipales elegida, completar los indicadores de mercado y el dashboard cartografico, conciliar los PDF heredados y realizar la integracion final de ramas. El cliente OVJ antiguo con constantes y los graficos historicos no son la evidencia de la ingesta corregida.

Las pruebas con servicios reales y registros de promociones son un avance verificable, pero no sustituyen esos requisitos. El bloque de ML usa aparte observaciones EMAL de renta municipal; no transforma los catalogos de promociones en expedientes personales.
