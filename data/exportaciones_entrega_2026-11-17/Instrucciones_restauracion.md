# Instrucciones de restauración · HDFS y MongoDB

## Origen de las copias

Exportación preparada el 17 de noviembre de 2026 con HDFS 3.4.2, Kafka 3.9.1 y MongoDB 7.0 reales, a partir de los originales archivados del proyecto. No se han recapturado anuncios ni modificado el modelo de IA.

## Qué se incluye


- `hdfs/data/reto1/`: 37 archivos descargados de HDFS y comprobados con SHA-256; 31 del recorrido de promociones y anuncios, y seis de la API de rentas.

- `hdfs_manifest.json`: ruta original de HDFS y huella de cada copia recuperada.

- `mongodb/`: tres copias `mongodump --archive --gzip`, con documentos e índices.

- `mongodb_inventario.json`: colecciones, recuentos e índices exportados.

- `resultados/`: salidas calculadas y evidencia del recorrido de esta ejecución.

- `restauracion_verificada.json`: comprobación de las copias restauradas en bases y rutas nuevas.

| Base exportada | Colecciones y recuentos |
|---|---|
| `reto1_entrega_paquete` | `viviendas`: 638; `municipios`: 80 |
| `reto1_municipal_paquete` | `rentas_emal`: 768; `contextos_ovj`: 1 |
| `reto1_api_paquete` | `rentas_api`: 3 |

Los 638 documentos de viviendas corresponden a 621 promociones y 17 identidades de anuncios. Las 768 filas EMAL son estadísticas de municipio y trimestre. El contexto OVJ es autonómico y la API aporta tres estadísticas separadas.

La carga repetida conserva 638 registros. La comprobación de cien incrementos se hace sobre una copia aislada y no modifica los documentos exportados. Las exportaciones de MongoDB se restauraron en bases nuevas y se compararon todos los documentos e índices. Los 37 archivos HDFS también se subieron a una ruta nueva y se volvieron a descargar con huellas idénticas.

## Restaurar MongoDB

Se necesita un servidor MongoDB y las [MongoDB Database Tools](https://www.mongodb.com/docs/database-tools/installation/), que incluyen `mongorestore`. Las órdenes siguientes se ejecutan desde la raíz del proyecto o del ZIP descomprimido:

```bash
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_entrega_paquete.archive.gz --gzip
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_municipal_paquete.archive.gz --gzip
mongorestore --uri mongodb://localhost:27017 --archive=data/exportaciones_entrega_2026-11-17/mongodb/reto1_api_paquete.archive.gz --gzip
```

Se crean las bases con los nombres de la tabla. Utilizar bases nuevas o elegir otros nombres con `--nsFrom` y `--nsTo` si ya existen. No hace falta borrar ninguna base del servidor para revisar esta entrega.

## Recuperar los archivos en HDFS

Con HDFS y su cliente disponibles, desde la misma raíz:

```bash
hdfs dfs -mkdir -p /data
hdfs dfs -put data/exportaciones_entrega_2026-11-17/hdfs/data/reto1 /data/
hdfs dfs -ls -R /data/reto1
```

La orden de carga supone que `/data/reto1` todavía no existe. Si existe, elegir una ruta de destino nueva para esta copia y conservar el contenido del servidor. `hdfs_manifest.json` recoge las rutas que tenían los archivos al exportarlos.

## Consultar las salidas sin arrancar los servicios

Los JSON de `resultados/municipal/` y `resultados/anuncios/` se pueden abrir directamente o seleccionar en el visor mediante `RETO1_ANALYSIS_DIR` y `RETO1_RENTALS_DIR`. Son resultados conservados de esta ejecución real. Para repetir el recorrido completo se usan los scripts y requisitos del PDF de instrucciones de ejecución incluido en la raíz del paquete.
