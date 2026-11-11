# Estado de entrega y comprobación por asignatura

## Actualización del 11 de noviembre de 2026

La adquisición de anuncios tiene ahora un CLI trazable y comprobaciones de
robots/TLS/originales antes de ingerir. Sus 153 pruebas incluyen fixtures de
HTML y fallos de acceso; las cinco pruebas de servicios se repitieron sin skips.
El intento real produjo cero anuncios por CONNECT 403. Consultar
[captura y límites](SCRAPING.md) y [evidencias](evidencias_scraping_2026-11-11/).
Los selectores no se declaran validados con páginas actuales inaccesibles.
El [CI BDA 43011875465](https://github.com/markelalvarez0/Reto-1/actions/runs/43011875465)
terminó Success para `a15756c`, sin convertir las pruebas con fixtures en una
captura vigente de mercado.

Se conserva la decisión del modelo y el test único. El incremento anterior aportó
129 pruebas unitarias, siete pruebas de MongoDB real y cinco pruebas de
HDFS/Kafka/MongoDB sin omisiones. Se transportaron tanto 621 promociones
oficiales como cinco vistas municipales verificadas. Las ejecuciones no son
equivalentes a un scraping vigente de alquileres. Ver
[evidencias locales](evidencias_2026-11-11/) y [contraste docente](CONTRASTE_DOCENTE.md).

El informe corregido se genera con `python main.py --pdf`; lee métricas,
diccionario, figuras y documentos verificados, sin deserializar el modelo.
Produce Markdown, PDF paginado y manifiesto de fuentes en `data/informe_entrega/`.
Los generadores históricos ahora delegan en él. El PDF maestro adjunto original
es contexto histórico y no debe confundirse con el informe vigente.

CI remoto del incremento **1c7c45e**: [BDA 43008668473](https://github.com/markelalvarez0/Reto-1/actions/runs/43008668473)
y [n8n 43008668600](https://github.com/markelalvarez0/Reto-1/actions/runs/43008668600),
ambos **Success**. Los cuatro PDF versionados contienen ahora el informe corregido
paginado. No se confunden con el PDF histórico adjunto de la conversación.

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
| BDA | Capturas oficiales y vistas municipales verificadas en HDFS/Kafka/MongoDB reales, con recarga idempotente y CI correcto en 1c7c45e. | Muestra vigente de alquiler libre obtenida por scraping. El HTML OVJ no equivale a anuncios. |
| SBD | Modelado, limpieza, consultas, agregaciones e índices con mongod real; comparación EMAL/OVJ y transporte de vistas incluidos en evidencias. | Ensayo de la demostración y defensa. Las consultas de anuncios se prueban con fixtures identificados. |
| SAA | EDA, cinco familias, MLP y experimentos, SHAP y test único conservado. Contraste docente documentado. | Defensa individual. sklearn no se presenta como Keras; no se cambia el ganador mirando test. |
| PIA | Pipeline, MLflow, notebooks, Streamlit y PDF corregido desde artefactos verificados. Capturas y prueba de reapertura actuales. | Validación de la versión nueva en Windows si se entrega para esa plataforma. |
| MIA | Ocho ramas n8n y recorrido Streamlit → consentimiento → ficha local, con persistencia e idempotencia reales. | Ensayo humano final. Ninguna prueba tramita ayudas ni comunica con personas. |

Los 33 tests históricos fueron ampliados en `dev-jon`; contar tests no sustituye
revisar qué prueban. Los avisos de convergencia de mini-tests no son resultados de
entrenamiento de entrega. Los originales, los artefactos ML y el test final
permanecen conservados byte a byte.

Se ha preparado [defensa de 15 minutos y preguntas](DEFENSA.md). Permanecen
pendientes el scraping autorizado de anuncios individuales y el ensayo humano.
La integración en test/main espera validación
integral, como autorizó el usuario. Las cifras históricas de la tabla anterior
deben leerse junto a esta actualización, no como trabajo aún sin implementar.
