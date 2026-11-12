# Captura de anuncios: implementación y límite de la evidencia

La captura del **12 de noviembre de 2026** está acreditada: 17 identidades de
anuncio, 9 de Habitaclia y 8 de Pisos.com, con HTML/robots y SHA-256 en
`data/capturas_anuncios/2026-11-12/`. Los selectores se contrastaron con los bytes
archivados y los campos persistidos en MongoDB real. La muestra no acredita
vigencia posterior, vivienda habitual ni representatividad del mercado.

El bloqueo CONNECT 403 del 11 de noviembre corresponde al entorno anterior.
En el entorno nuevo se consultaron robots HTTP 200 y avisos legales; la primera
captura descubrió rutas 404 y selectores desactualizados. Sus fallos se conservaron,
y las correcciones se probaron antes de capturar el lote final.
Ver [resultados, modalidades y transporte](RESULTADOS_ANUNCIOS.md).

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
semanales. Los céntimos se conservan. Estos filtros son conservadores. La comprobación actual se limita al HTML
archivado del 12 de noviembre y no garantiza futuras versiones del portal.

Cada salida necesita un directorio nuevo. Un error, página de bloqueo o HTML
sin anuncios deja un informe explícito. Una captura parcial conserva candidatos
separados; únicamente una captura interpretable de todos los listados solicitados
produce `vivienda_scraping.json`. Un resultado interpretable no garantiza que
todas las ofertas estén vigentes ni constituye un censo del mercado.

## Nueva captura o reproducción del archivo

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
comprobaron también con los 17 anuncios archivados y las capturas oficiales.
El HTML auxiliar de las pruebas de transporte sigue declarado como fixture.

El modelo, sus particiones y su evaluación única permanecen intactos. La captura
de anuncios no alimenta automáticamente otro entrenamiento.

La prueba con archivo conservado se ejecuta mediante `scripts/analyze_rental_sample.py`:
reinterpreta precios, municipio, identidad y características; valida los originales
y las condiciones textuales antes de contrastar MongoDB. El informe detalla tarjetas
no interpretables, nulos, límite de selección y reentrega sin duplicados. Las señales
temporal/empresas no se interpretan como una clasificación administrativa. La ausencia
de señal tampoco demuestra vivienda habitual.
