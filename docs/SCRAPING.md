# Captura de anuncios: implementación y límite de la evidencia

La captura vigente todavía no está acreditada. El 11 de noviembre de 2026 la
máquina rechazó ambos CONNECT a robots.txt con 403 del proxy. El intento terminó
con salida 2, estado `incompleta`, cero registros y ningún fichero listo para
ingerir. No se afirma que el servidor del portal haya recibido la petición.

## Recorrido preparado

`scripts/capture_rentals.py` solicita un listado de alquiler por cada capital,
con un límite de 1 a 20 anuncios por listado y un User-Agent académico explícito.
Antes de cada destino comprueba el dominio HTTPS y robots.txt. Las redirecciones
vuelven a pasar esos controles; un destino externo se rechaza. La demora mínima
es 1,5 segundos y respeta crawl-delay/request-rate publicados. No se desactiva
TLS ni se recurre a proxies alternativos, CAPTCHA o endpoints privados.

Se guardan los bytes de robots y HTML en `sources/`, junto con URL, fecha UTC,
estado HTTP, tamaño, SHA-256 y estado TLS. Los ficheros tienen nombres únicos.
Cada anuncio lleva la referencia del HTML y de los robots que permitieron su
captura. Los IDs derivados de URL son estables; no dependen de la hora.

El municipio debe estar publicado en la ubicación y ser reconocible; no se
reemplaza por el municipio del listado. Se excluyen candidatos sin precio o
municipio, tipos no residenciales evidentes, habitaciones y precios diarios o
semanales. Los céntimos se conservan. Estos filtros son conservadores, no una
validación de selectores sobre HTML actual: esta sigue pendiente.

Cada salida necesita un directorio nuevo. Un error, página de bloqueo o HTML
sin anuncios deja un informe explícito. Una captura parcial conserva candidatos
separados; únicamente una captura interpretable de todos los listados solicitados
produce `vivienda_scraping.json`. Un resultado interpretable no garantiza que
todas las ofertas estén vigentes ni constituye un censo del mercado.

## Ejecución cuando el acceso esté habilitado

Revisar primero las condiciones de uso de los portales; robots no equivale a
licencia. Desde la raíz, con el entorno instalado:

```bash
python scripts/capture_rentals.py --output-dir data/scraping/mi_captura --max-items 10
```

Si termina correctamente, se puede combinar con las capturas oficiales sin
alterarlas y recorrer los servicios reales ya preparados:

```bash
python scripts/run_pipeline.py --snapshot-dir data/capturas_oficiales --raw-dir data/scraping/mi_captura --output-dir data/bda/con_scraping
```

Antes de ingerir anuncios de estos portales, el pipeline vuelve a comprobar los
bytes y metadatos de HTML/robots y que sus reglas permiten la ruta. También
almacena esos originales auxiliares en HDFS cuando utiliza la captura oficial.
Los mensajes, documentos y estadísticas mantienen `tipo_registro=anuncio`,
separado de las promociones oficiales. No ejecutar este segundo comando para
presentar como completa una captura con salida 2.

## Qué se ha comprobado

Las pruebas nuevas usan HTML sintético identificado: robots denegado o no
verificable, fallo de certificado sin fallback, redirecciones, integridad de
bytes, céntimos, unidades, municipio desconocido, garajes y ausencia de anuncios.
No se publican esos fixtures como una muestra real. Los servicios reales se
comprueban por separado con las capturas oficiales; un HTML auxiliar declarado
como fixture solo verifica que HDFS conserva también fuentes adicionales.

El modelo, sus particiones y su evaluación única permanecen intactos. La captura
de anuncios no alimenta automáticamente otro entrenamiento.
