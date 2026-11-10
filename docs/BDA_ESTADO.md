# BDA: ingesta trazable y transporte de las capturas oficiales

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

Esto **no acredita todavia** una muestra vigente de alquiler libre obtenida por scraping, la descarga verificada de todos los indicadores Udalmap, el dashboard final ni el cumplimiento completo de la rubrica de BDA/SBD. Los scrapers y clientes antiguos que no intervienen en este recorrido requieren su propia revision, incluido el cliente OVJ heredado con constantes. No deben usarse sus salidas historicas como evidencia observada.

El mapa historico no se abre automaticamente como si contuviera estos resultados. La entrega cartografica y los indicadores de mercado libre se cerraran por separado con datos y unidades comprobados.
