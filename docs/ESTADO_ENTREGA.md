# Estado de entrega y comprobación por asignatura

## Actualización del 11 de noviembre de 2026

Se conserva la decisión del modelo y el test único. La continuación aporta
129 pruebas unitarias, siete pruebas de MongoDB real y cinco pruebas de
HDFS/Kafka/MongoDB sin omisiones. Se transportaron tanto 621 promociones
oficiales como cinco vistas municipales verificadas. Las ejecuciones no son
equivalentes a un scraping vigente de alquileres. Ver
[evidencias locales](evidencias_2026-11-11/) y [contraste docente](CONTRASTE_DOCENTE.md).

El informe corregido se genera con `python main.py --pdf`; lee métricas,
diccionario, figuras y documentos verificados, sin deserializar el modelo.
Produce Markdown, PDF paginado y manifiesto de fuentes en `data/informe_entrega/`.
Los generadores históricos ahora delegan en él. El PDF maestro antiguo sigue
siendo un documento histórico, no el informe vigente.

## Objetivo confirmado

Estimar alquileres con datos observados y orientar al joven mediante reglas. El
modelo conservado estima **renta media municipal trimestral**, no el precio de un
piso ni la solvencia individual. Su selección y evaluación final están cerradas;
abrir la aplicación o ejecutar la auditoría no vuelve a entrenar ni evalúa test.

## Incremento de desarrollo: acceso, integridad y comparación territorial

- `main.py` abre Streamlit y el modelo conservado; conserva los códigos de error,
  ejecuta la suite completa y resuelve rutas desde la raíz del proyecto.
- `python main.py --audit --json` verifica los seis originales, los 88 artefactos
  conservados, el informe de test único y las tres copias académicas de `src/`.
  No carga archivos pickle/joblib ni ejecuta predicciones.
- `scripts/analyze_municipal.py` carga estadísticas EMAL en `rentas_emal` y el
  contexto OVJ en `contextos_ovj`, conservando las huellas. La identidad incluye
  captura, INE y trimestre. La recarga no duplica documentos ni borra colecciones.
- Tres agregaciones MongoDB producen comparación municipal, serie temporal y
  resumen territorial. El `$lookup` cruza cada observación con el contexto
  autonómico documentado; nunca lo etiqueta como salario municipal.
- `app/territorio.py` lee salidas con manifiesto SHA-256, muestra tablas, gráficos,
  CSV descargable y coordenadas de promociones Visesa. La cartografía base usa
  recursos externos; su disponibilidad no está garantizada en una red restringida.

## Cómo ejecutarlo

Python 3.12. Desde la raíz:

```bash
uv sync --locked --extra dev
uv run --no-sync python main.py --audit --json
uv run --no-sync python main.py --subject bda_sbd --prepare-only

# MongoDB local accesible; MONGO_URI permite cambiar el servidor/puerto.
uv run --no-sync python scripts/analyze_municipal.py
uv run --no-sync python main.py --subject bda_sbd --visual
uv run --no-sync python main.py --subject saa_pia_mia

uv run --no-sync python main.py --test -q
# Con MongoDB real configurado en MONGO_INTEGRATION_URI:
uv run --no-sync python -m pytest integration_tests/test_mongodb_live.py integration_tests/test_municipal_live.py -q
```

Las salidas regenerables se guardan en `data/analisis_municipal/`, fuera de Git.
`--simulate-db` permite desarrollo sin servidor y marca el motor como mongomock;
no es evidencia de ejecución en MongoDB real. Se mantiene la alternativa pip
documentada en el README. Las versiones del lock actual no sustituyen el registro
histórico del entorno con el que se entrenó el modelo publicado.

## Resultado descriptivo reproducido: 2024 T4

18 municipios con renta publicada en ese trimestre. La serie completa conservada
tiene 19 municipios; no se rellena el dato ausente para completar la tabla.

| Municipio | Renta media mensual | Contratos | Variación interanual | Esfuerzo del escenario |
|---|---:|---:|---:|---:|
| Vitoria-Gasteiz | 798,57 € | 549 | 2,88 % | 51,06 % |
| Bilbao | 930,31 € | 767 | 6,86 % | 59,48 % |
| Donostia-San Sebastián | 1.147,53 € | 516 | 8,53 % | 73,37 % |

El escenario utiliza 1.564 €/mes, salario neto medio de juventud asalariada de
18–34 años en Euskadi en 2024, incluidas pagas extra (OVJ). Entre estas tres
capitales, la renta media de Vitoria es menor, pero las tres superarían el 30 %
de ese ingreso si una persona pagara íntegramente la renta media municipal.
Esto ilustra una dificultad económica; no demuestra qué proporción de jóvenes
puede emanciparse ni representa todos los hogares o contratos actuales.

Los indicadores son renta mensual, equivalente anual, número de contratos,
variación interanual cuando existe el dato previo, esfuerzo del escenario y
diferencia frente al umbral analítico del 30 %. Este umbral no concede ni deniega
subvenciones. Las medias territoriales son simples entre municipios cubiertos,
no medias de todos los contratos de cada provincia.

## Rúbricas: evidencia y trabajo que permanece

| Asignatura | Evidencia utilizable | Pendiente para cerrar toda la entrega |
|---|---|---|
| BDA | Capturas oficiales, preparación con rechazo explícito, recorrido HDFS/Kafka/MongoDB documentado en `docs/evidencias_bda`. | Muestra vigente de alquiler libre obtenida por scraping y demostración final del recorrido completo. El HTML OVJ es extracción de un indicador, no scraping de anuncios. |
| SBD | Modelado, limpieza, consultas, agregaciones e índices; pruebas con mongod real; nueva comparación EMAL/OVJ. | Incorporar el resultado territorial al paquete final y demostrarlo junto al recorrido BDA. |
| SAA | EDA, cinco familias, MLP y experimentos, SHAP y test único conservado. | Conciliar los documentos históricos. El MLP entregado usa sklearn; los ejercicios nuevos muestran Keras. No cambiar el ganador después de ver test para fingir otra validación. |
| PIA | Pipeline estándar, MLflow, artefacto completo, notebooks y Streamlit; portal y auditoría actualizados. | PDF corregido, documentación conjunta y comprobación de portabilidad completa. |
| MIA | Reglas y n8n con acciones locales e idempotencia, pruebas documentadas. | Ensayo final del caso de negocio y defensa; las acciones de prueba no tramitan ayudas reales. |

Los 33 tests históricos fueron ampliados en `dev-jon`; contar tests no sustituye
revisar qué prueban. Los avisos de convergencia de mini-tests no son resultados de
entrenamiento de entrega. Los originales, los artefactos ML y el test final
permanecen conservados byte a byte.

Se ha preparado [defensa de 15 minutos y preguntas](DEFENSA.md). Permanecen
pendientes el scraping autorizado de anuncios individuales, el CI remoto del
incremento y el ensayo humano. La integración en test/main espera validación
integral, como autorizó el usuario. Las cifras históricas de la tabla anterior
deben leerse junto a esta actualización, no como trabajo aún sin implementar.
