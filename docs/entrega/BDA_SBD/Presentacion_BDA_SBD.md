# Presentación BDA y SBD

## 1 Queremos comparar opciones de vivienda

¿Qué podemos decir sobre el acceso a la vivienda joven con datos reales?

En 2024 T4, pagar la renta media de Bilbao supone el 59,48 % del ingreso de referencia.

El ingreso es autonómico: 1.564 €/mes, OVJ 2024.

## 2 No todos los registros son pisos

17 identidades de anuncio archivadas: precio pedido.

621 registros de promociones: no son viviendas disponibles.

EMAL: renta media municipal de contratos, no anuncios.

:::flow Anuncios | Promociones | Estadísticas | Contexto salarial

## 3 Conservamos lo que recibimos

Guardamos originales, URL, fecha y SHA-256.

La API aporta estadísticas monetarias; el scraping aporta anuncios.

Podemos comprobar un dato aunque la página cambie después.

## 4 Cada herramienta tiene una función

:::flow Captura | HDFS | Kafka | MongoDB | Visor

HDFS guarda y recupera; Kafka transporta; MongoDB consulta y agrega.

El tamaño de la muestra no exige un clúster: demostramos el recorrido del reto.

## 5 Repetir no debe crear otra copia

638 registros recibidos y persistidos: 621 promociones + 17 anuncios.

La recarga mantiene 638. La API mantiene sus tres estadísticas por separado.

Guardamos antes de confirmar el mensaje. Identidad: fuente e identificador.

## 6 Los datos desconocidos siguen siendo desconocidos

Cuatro operaciones: duplicados, nulos, tipos y derivados.

Dos registros oficiales ambiguos se rechazan; no les asignamos Bilbao.

Ascensor sin dato no significa que el piso no tenga ascensor.

## 7 Preguntamos y resumimos con MongoDB

Consultas: Bilbao; hasta 750 €; filtros combinados; habitaciones; señal temporal.

Resultados archivados: 6 / 1 / 4 / 10 como máximo / 3.

Tres pipelines: estadísticas municipales, cruce de contexto y distribuciones.

## 8 Medimos qué hace el índice

| Medida | Sin índice | Con índice |
|---|---:|---:|
| Documentos examinados | 638 | 4 |
| Resultados | 4 | 4 |
| Tiempo registrado | 0 ms | 0 ms |

Examinamos menos documentos. No medimos una mejora temporal.

100 incrementos sobre una copia aislada dejan el contador en 100.

## 9 Vitoria requiere menos esfuerzo en este escenario

| Capital 2024 T4 | Renta mensual | Esfuerzo con 1.564 € |
|---|---:|---:|
| Vitoria-Gasteiz | 798,57 € | 51,06 % |
| Bilbao | 930,31 € | 59,48 % |
| Donostia-San Sebastián | 1.147,53 € | 73,37 % |

Las tres superan el 30 %. Es un escenario, no una evaluación de cada joven.

## 10 Demostramos del resultado al original

Abrimos el visor: comparación, evolución, promociones y anuncios archivados.

Seguimos una cifra hasta el JSON, el manifiesto y el archivo original.

Mostramos recarga, consultas y explain. Guion oral separado.

## 11 La conclusión depende de lo que hemos medido

Vitoria tiene menor renta media entre las tres capitales en 2024 T4.

17 anuncios no representan todo el mercado ni garantizan disponibilidad.

Mejoras propuestas: ampliar cobertura, actualizar versiones y estudiar ingresos comparables.

## 12 Evidencias que acompañan la exposición

Datos: data/capturas_oficiales, capturas_anuncios y capturas_api_rentas.

Resultados: docs/evidencias_entrega_2026-11-12 y evidencias_cierre_rubrica_2026-11-12.

Código: src/database, src/hdfs, src/kafka y scripts.

Duración BDA/SBD: el enunciado no fija límite. Lo confirmamos con el profesorado.
