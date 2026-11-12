# Cierre de los puntos de la revisión docente

## MIA: predicción que sí cambia la orientación

R_REFERENCIA, prioridad 65, recomienda BUSCAR_ALTERNATIVAS cuando la renta media
municipal predicha supera el 40% del ingreso declarado en el escenario de pagarla
íntegra. Es una señal interna de orientación territorial, no una evaluación de
solvencia ni un requisito de ayudas. Seguridad, vigencia normativa, esfuerzo
real crítico y revisión documental conservan prioridad mayor.

El esfuerzo declarado sigue usando contrato y deudas. El esfuerzo de referencia
usa la predicción municipal y se muestra por separado. El motor tiene diez reglas
y mantiene ocho ramas n8n. La ficha local conserva regla y referencia estimada;
no se transmiten salario, nombre, dirección ni perfil personal.

Prueba contrafactual inventada: ingreso 1.500 €, contrato 500 €, documentación
completa. Predicción de prueba 600 € → CONSULTAR_GAZTELAGUN; predicción 1.600 € →
BUSCAR_ALTERNATIVAS por R_REFERENCIA. Esfuerzo declarado 33,33% en ambos casos;
esfuerzo de referencia 40% / 106,67%. No se ejecuta el modelo para esta prueba.
La prueba AppTest con el modelo conservado comprueba además el caso completo
hasta una ficha n8n real, con consentimiento y repetición sin duplicados.

## BDA: API que aporta precios monetarios

Se incorpora el servicio JSON que utiliza el visor público oficial EMAL:
https://eremutentsionatua.euskadi.eus/ad23aConsultaWar/consulta/emal

Su uso se identifica en el visor público y su JavaScript público:
https://eremutentsionatua.euskadi.eus/webzte00-municipios/es/ad23aConsultaWar/emal?locale=es

GET con ambito=4 (municipio), tipoDatoContratos=4 (firmados por trimestre),
tipoContrato=1 (vivienda habitual), tipoHueco=0 (edificio colectivo), y códigos de
provincia/municipio publicados. No necesita autenticación. No es una conversión
local del Excel a JSON ni se utilizó un servicio privado.

Se conserva la respuesta original de cada capital, con URL completa, filtros,
fecha, HTTP, tamaño y SHA-256, junto con la página que documenta el visor, en
`data/capturas_api_rentas/2026-11-12/`. Los normalizados seleccionan 2024 T4:

| Municipio | Renta mensual API | Contratos |
|---|---:|---:|
| Vitoria-Gasteiz | 798,6 € | 549 |
| Donostia-San Sebastián | 1.147,5 € | 516 |
| Bilbao | 930,3 € | 767 |

La API redondea importes a una décima; el Excel conservado publica más decimales.
No se reemplazan sus bytes ni los 768 datos de entrenamiento/validación/test.
Son tres estadísticas de renta municipal; no son anuncios ni promociones.
Se transportan por HDFS → recuperación idéntica → Kafka → MongoDB `rentas_api`.
La reentrega mantiene tres documentos. Los 638 anuncios/promociones previos
mantienen su recuento y colecciones; no se suman ambas unidades.

Reproducción sin recapturar ni entrenar, con servicios reales disponibles:

```bash
python scripts/transport_rent_api.py --input-dir data/capturas_api_rentas/2026-11-12 --report data/bda/api-rentas.json
```

Una nueva captura solo usa un directorio nuevo:

```bash
python scripts/capture_emal_api.py --output-dir data/capturas_api_rentas/otra_fecha
```

## SAA y PIA: contenido obligatorio visible

Los README principal y del bloque IA incorporan el problema cuantificado y su
usuario, el esquema del recorrido, la tabla de nueve modelos con métricas de
train/validación y tiempos históricos, dos gráficos EDA comentados, captura
histórica de MLflow y gráfico de la única evaluación final. Se explican IA débil
frente a fuerte y aprendizaje supervisado frente a no supervisado.

Los ejercicios de redes usan Keras y el proyecto MLPRegressor; Kafka y HDFS usan
APIs diferentes de las prácticas. Se explica la equivalencia sin decir que son
la misma API. TimeSeriesSplit está mencionado en el PDF de validación de clase.
SHAP y la comparación auxiliar SMOTE amplían los ejercicios aportados, pero no
se garantiza el criterio de novedad de todo el curso. El resultado conservado
SMOTE no mejora F1; no se reabre la selección buscando otro resultado.

## Defensa

El guion de 15 minutos y las preguntas se actualizan en DEFENSA.md. Los recorridos
se comprueban con software y casos de demostración identificados. El ensayo oral
cronometrado de la pareja y las tres respuestas individuales de cada alumno no
pueden acreditarse con pruebas automatizadas y permanecen a cargo del alumnado.

Validación local del cierre: 168 pruebas, cinco avisos conocidos, 12 integraciones
reales sin omisiones, dos transportes de API y ocho ramas n8n. El caso de prueba
AppTest del modelo conservado produjo R_REFERENCIA y una ficha real idempotente.
Los XML y JSON están en docs/evidencias_cierre_rubrica_2026-11-12/.
