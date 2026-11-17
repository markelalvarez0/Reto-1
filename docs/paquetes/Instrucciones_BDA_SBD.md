# Instrucciones de ejecución · BDA y SBD

## Qué entregamos

Hemos recogido y conservado datos de vivienda, conectado HDFS, Kafka y MongoDB y preparado una comparación de municipios. Este paquete reúne los documentos y archivos de este bloque.

## Documentos para corregir


- [Memoria en PDF](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/BDA_SBD/Documentacion_BDA_SBD.pdf): fuentes, decisiones, recorrido, consultas, resultados y límites.

- [Presentación en PDF](https://github.com/markelalvarez0/Reto-1/blob/main/docs/entrega/BDA_SBD/Presentacion_BDA_SBD.pdf): 12 diapositivas con gráficos, capturas y explicaciones de qué hicimos y por qué.

- Las fuentes editables `.md` están junto a los PDF.

## Qué contiene

| Carpeta | Contenido |
|---|---|
| `src/`, `scripts/`, `app/` | Código Python, cargas, consultas y visor |
| `data/capturas_oficiales/` | Originales de fuentes oficiales y manifiesto |
| `data/capturas_anuncios/` | 17 anuncios archivados, HTML y procedencia |
| `data/capturas_api_rentas/` | Tres estadísticas EMAL obtenidas por API |
| `docs/evidencias_entrega_2026-11-12/` | Resultados de MongoDB, consultas, índices y transporte |
| `docs/evidencias_cierre_rubrica_2026-11-12/` | Evidencia adicional de la API y servicios |
| `data/exportaciones_entrega_2026-11-17/` | Copia recuperada de HDFS, tres dumps MongoDB y restauración verificada |
| `tests/`, `integration_tests/` | Pruebas del bloque y comprobaciones con servicios reales |
| `infra/` | Script de arranque de HDFS utilizado en integración |

Conservamos las rutas del repositorio para que los scripts encuentren los archivos. La carpeta `src/` es compartida por el proyecto. No se incluyen guiones orales, material de estudio ni informes antiguos.

## Instalar y comprobar

Descomprimir todo el ZIP y abrir una terminal en la carpeta `Entrega_BDA_SBD`, donde está este PDF de instrucciones. Se necesita Python 3.12 y [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --locked --extra dev
uv run --no-sync python verificar_entrega.py
uv run --no-sync python -m pytest tests/ -q
```

El verificador compara los archivos con `MANIFIESTO_ENTREGA.json`. Las pruebas locales pueden usar datos de ejemplo y servicios simulados; las integraciones reales se distinguen en `integration_tests/` y en las evidencias conservadas.

## Abrir el visor con los resultados incluidos

No hace falta arrancar HDFS, Kafka o MongoDB para consultar los resultados archivados. En Linux o macOS, desde la raíz del paquete:

```bash
RETO1_ANALYSIS_DIR=docs/evidencias_entrega_2026-11-12/municipal uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

En Windows PowerShell:

```powershell
$env:RETO1_ANALYSIS_DIR='docs/evidencias_entrega_2026-11-12/municipal'
uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

Abrir http://localhost:8502. Se pueden seleccionar municipios, ver rentas y evolución, consultar el mapa y revisar los anuncios. Ctrl+C detiene el visor. La pantalla muestra resultados reales archivados; abrirla no vuelve a ejecutar el transporte.

## Repetir el recorrido con servicios reales

Preparar HDFS con WebHDFS, Kafka y MongoDB. Los valores predeterminados son `localhost:9870`, `localhost:9092` y `mongodb://localhost:27017`. Si los servicios están en otro equipo, configurar `HDFS_NAMENODE_HOST`, `HDFS_NAMENODE_PORT`, `HDFS_USER`, `KAFKA_BOOTSTRAP_SERVERS` y `MONGO_URI`. La configuración de referencia está en `.github/workflows/bda-candidate.yml` y `infra/start_hdfs_ci.sh`; no se incluye un instalador único de los tres servicios.

Copiar la captura a una carpeta de trabajo nueva y ejecutar:

```bash
uv run --no-sync python -c "import shutil; shutil.copytree('data/capturas_anuncios/2026-11-12', 'data/scraping/entrega')"
uv run --no-sync python scripts/run_pipeline.py --snapshot-dir data/capturas_oficiales --raw-dir data/scraping/entrega --output-dir data/bda/entrega --db-name reto1_entrega
uv run --no-sync python scripts/analyze_rental_sample.py --capture-dir data/capturas_anuncios/2026-11-12 --pipeline-dir data/bda/entrega --db-name reto1_entrega
uv run --no-sync python scripts/transport_rent_api.py --input-dir data/capturas_api_rentas/2026-11-12 --db-name reto1_api_rentas --report data/bda/api-rentas-entrega.json
uv run --no-sync python scripts/analyze_municipal.py
```

Si `data/scraping/entrega` ya existe y conserva esa captura, omitir la primera orden o elegir otro nombre. Los comandos trabajan sobre copias y no cambian los originales.

Para abrir los nuevos resultados, seleccionar `data/analisis_municipal` en `RETO1_ANALYSIS_DIR` y `data/analisis_anuncios` en `RETO1_RENTALS_DIR`. Por ejemplo, en PowerShell:

```powershell
$env:RETO1_ANALYSIS_DIR='data/analisis_municipal'
$env:RETO1_RENTALS_DIR='data/analisis_anuncios'
uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

En Bash:

```bash
RETO1_ANALYSIS_DIR=data/analisis_municipal RETO1_RENTALS_DIR=data/analisis_anuncios uv run --no-sync python main.py --subject bda_sbd --visual --server.port 8502
```

## Qué resultados se comprueban

El lote transportado tiene 621 registros de promociones y 17 identidades de anuncios: 638 registros, no 638 pisos distintos. La recarga conserva el recuento. Las tres estadísticas de la API van en una colección separada. El índice permite revisar cuatro documentos en vez de 638 para la consulta medida; ambas mediciones registraron 0 ms.

En 2024 T4, las rentas medias EMAL de Vitoria, Bilbao y Donostia fueron 798,57 €, 930,31 € y 1.147,53 €. Con el mismo ingreso autonómico de referencia de 1.564 €/mes, los esfuerzos son 51,06 %, 59,48 % y 73,37 %. Es un escenario común, no un salario municipal ni una evaluación individual. La memoria desarrolla fuentes y límites.

## Restaurar los datos entregados

El ZIP incluye 37 archivos recuperados de HDFS y tres copias de MongoDB con documentos e índices. Se ha comprobado su restauración en rutas y bases nuevas. Las bases contienen 638 registros de promociones y anuncios, 80 municipios, 768 observaciones EMAL, un contexto OVJ y tres estadísticas de la API.

Las órdenes de `mongorestore` y `hdfs dfs -put` están en [Instrucciones de restauración](https://github.com/markelalvarez0/Reto-1/blob/main/data/exportaciones_entrega_2026-11-17/Instrucciones_restauracion.pdf). El inventario y las huellas permiten comprobar la copia. No es necesario volver a capturar las webs para recuperar estos datos.


Repositorio completo: https://github.com/markelalvarez0/Reto-1
