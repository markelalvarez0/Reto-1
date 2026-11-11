# BDA: ingesta trazable y transporte de las capturas oficiales

## Continuación validada el 11 de noviembre de 2026

En esta máquina se ejecutaron cinco pruebas end-to-end sin skips con Hadoop
3.4.2 lean (SHA512 oficial), Java 11, Kafka 3.9.1 y MongoDB 7.0.
La preparación volvió a aceptar 621 registros (215 Visesa y 406 Etxebide),
rechazando dos de los 623 originales por municipio ambiguo. Llegaron y se
persistieron los 621, con procedencia y recarga idempotente.
Ver [XML](evidencias_2026-11-11/integracion.xml) y
[resumen local](evidencias_2026-11-11/bda-resumen.json).

El análisis territorial se exportó con MongoDB real y se transportaron sus cinco
vistas por separado. `scripts/transport_municipal.py` verifica el manifiesto,
almacena procesados en HDFS, recupera y compara bytes, publica lo recuperado en
Kafka y persiste en `vistas_municipales` antes de confirmar offsets.
La identidad `(archivo, sha256)` permite reentrega sin duplicar. Los mensajes son
vistas agregadas, no HousingAd ni viviendas nuevas. Una nueva huella conserva
otra versión. La prueba repite todo el transporte y comprueba cinco documentos.

```bash
python scripts/analyze_municipal.py --output-dir evidencia_bda_integracion/municipal
python scripts/transport_municipal.py --input-dir evidencia_bda_integracion/municipal --report evidencia_bda_integracion/transporte_municipal.json
```

MONGO_URI debe seleccionar el mismo servidor para ambos comandos. El workflow
registra MONGO_INTEGRATION_URI para la prueba municipal, exporta las vistas,
ejecuta la auditoría y rechaza XML vacíos, errores, fallos, skips y ausencia de
las pruebas municipales. Archiva los resultados y sus huellas. Esta validación
local precede al commit; no se presenta como un CI remoto de checkout limpio.

## Alcance de esta correccion

Este recorrido usa los originales conservados en `data/capturas_oficiales/`, no anuncios inventados. Integra los catalogos de promociones de Visesa y Etxebide, el nomenclator INE y el contexto salarial publicado por el OVJ. **Una promocion no equivale a una vivienda disponible ni a un anuncio individual de alquiler.**

Se distinguen codigo implementado, pruebas con fixtures y pruebas con capturas reales. La evidencia de este recorrido, cuando la validacion termina correctamente, queda en `docs/evidencias_bda/resumen.json` y en el workflow `bda-candidate.yml`.

## Contratos de los datos

| Fuente | Contrato y tratamiento |
|---|---|
| Visesa | La captura verificada usa `rows`. El lector conserva esa compatibilidad y admite por separado `promociones`, sin convertir precios de locales o garajes en rentas. Un contrato desconocido provoca un error, no un exito con cero filas. |
| Etxebide | CSV con `;`, codificacion ISO-8859-1 y columnas `ID_PROM`, `Cod_Prov`, `CODMUNI`, `Municipio` y `Reg Acceso`. No publica una renta mensual individual en esas columnas. |
| INE | XLSX con hojas provinciales: se leen `01`, `20` y `48`. Se concatenan CPRO (2 digitos) y CMUN (3), sin incluir DC. |
| OVJ | Se extrae el salario del parrafo correspondiente a 18-34 anos, 2024, neto mensual e incluidas pagas extraordinarias. Se conserva como referencia de Euskadi, no como salario de cada municipio. |

Los nombres historicos de Etxebide se resuelven por el codigo publicado, si existe en el catalogo INE verificado y no contradice un nombre reconocido. Se conservan el nombre original y el metodo de correspondencia. No se aceptan coincidencias parciales ni se asigna Bilbao como localidad por defecto.

## Integridad de los originales

Se detecto que `* text=auto` normalizaba CRLF a LF al incorporar el CSV de Etxebide y el HTML del OVJ a Git. El contenido textual seguia siendo equivalente, pero la huella de los bytes ya no coincidia con el manifiesto.

La correccion recupera los bytes exactos del artefacto original de captura, sin recapturar la fuente ni modificar las huellas esperadas. La regla `/data/capturas_oficiales/** -text -diff` impide nuevas conversiones. Antes de procesar se verifica SHA-256 de cada original; una diferencia detiene la carga.

## Recorrido reproducible

1. Verificar manifiesto, originales e INE; preparar `vivienda_oficial.json` y `municipios_oficiales.json` fuera de la carpeta de originales.
2. Conservar en HDFS tanto las capturas originales como los derivados en rutas `raw` y `processed` separadas. Recuperar cada fichero y comparar bytes y SHA-256.
3. Publicar registros `HousingAd` con fuente, tipo de registro, procedencia y lote de ingesta. Las claves de particionado son codigos municipales.
4. Consumir solo el lote esperado y confirmar el desplazamiento de Kafka despues de la persistencia en MongoDB.
5. Guardar por `(fuente, id_origen)` sin borrar colecciones ni reiniciar contadores. Comprobar que la procedencia sobrevive al transporte.
6. Exportar recuentos de registros de promociones por municipio y fuente. Las estadisticas de alquiler individual excluyen `tipo_registro=promocion`.

Los recuentos de dos catalogos **no deben sumarse como viviendas unicas**: puede haber promociones presentes en ambas fuentes. Los importes y superficies desconocidos siguen siendo nulos. El salario autonomico se guarda en `contexto_autonomico.salario_ovj`; el campo de salario municipal no se rellena con ese valor.

## Ejecucion

Desde la raiz del repositorio, con el entorno de `requirements-ci.txt` instalado:

```bash
# Solo comprobar y preparar originales; no requiere servicios.
python "BDA + SBD/main.py" --prepare-only

# Recorrido real: requiere HDFS, Kafka y MongoDB accesibles.
python "BDA + SBD/main.py" --pipeline

# Configuracion explicita del lote y salidas.
python scripts/run_pipeline.py --snapshot-dir data/capturas_oficiales --raw-dir data/bda/prepared --output-dir data/bda/processed --db-name reto1_vivienda --interval-seconds 0.1

# Demostracion separada, con datos y servicios simulados identificados.
python scripts/run_pipeline.py --demo

# Regresion y sincronizacion de codigo.
python -m pytest tests/ -q
python scripts/sync_sources.py --check
```

El comando de la raiz `python main.py --subject bda_sbd --pipeline` delega en el mismo recorrido. No es necesario copiar otro `src/` al PYTHONPATH. Las conexiones usan `MONGO_URI`, `MONGO_DB`, `HDFS_NAMENODE_HOST`, `HDFS_NAMENODE_PORT`, `HDFS_USER`, `KAFKA_BOOTSTRAP_SERVERS` y las opciones del cliente; consultar `.env.example`.

## Verificacion y limites pendientes

La validacion usa Hadoop, Apache Kafka y MongoDB temporales en GitHub Actions. Comprueba los originales, el transporte, la persistencia, los recuentos, las uniones municipales y una recarga idempotente. No modifica el modelo ML ni vuelve a evaluar su test reservado.

Esto **no acredita todavia** una muestra vigente de alquiler libre obtenida por scraping ni la descarga verificada de todos los indicadores Udalmap. Los scrapers y clientes antiguos que no intervienen en este recorrido requieren su propia revision, incluido el cliente OVJ heredado con constantes. No deben usarse sus salidas historicas como evidencia observada. La comparación actual emplea EMAL y OVJ verificados, no esas constantes.

El mapa histórico no se abre como si contuviera estos resultados. El visor territorial actual está comprobado con resultados de MongoDB real y muestra promociones localizadas, no ofertas disponibles. Permanecen pendientes los indicadores de mercado libre basados en anuncios individuales.
