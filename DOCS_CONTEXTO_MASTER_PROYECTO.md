# DOCUMENTO MAESTRO DE CONTEXTO TÉCNICO Y ARQUITECTURA
## Proyecto: Reto 1 — Acceso a la Vivienda para Jóvenes en Euskadi
### Curso de Especialización en Inteligencia Artificial y Big Data (IABD 2026-27)

---

## 1. RESUMEN EJECUTIVO Y CONTEXTO ACADÉMICO

Este repositorio contiene la resolución técnica completa, modular y documentada para los retos interdisciplinares del **Curso de Especialización en Inteligencia Artificial y Big Data**. 

El proyecto aborda la problemática social del acceso a la vivienda y la emancipación juvenil en la Comunidad Autónoma del País Vasco (Euskadi), integrando dos grandes bloques curriculares:

1. **Bloque 1: Big Data Aplicado (BDA) + Sistemas Big Data (SBD)**
   - *Reto:* «¿Dónde pueden vivir los jóvenes en Euskadi?»
   - *Objetivos:* Ingesta multicanal (Scraping + APIs), almacenamiento distribuido en Apache Hadoop (HDFS), streaming en tiempo real con Apache Kafka, base de datos documental NoSQL con MongoDB y PyMongo (modelado híbrido, limpieza, 3 aggregation pipelines, optimización de índices con `explain()` y operaciones atómicas), y cuadro de mando cartográfico interactivo con Leaflet.
2. **Bloque 2: Sistemas de Aprendizaje Automático (SAA) + Programación de IA (PIA) + Modelos de IA (MIA)**
   - *Reto:* «De la Predicción a la Acción: Vivienda y Emancipación Juvenil»
   - *Objetivos:* Análisis exploratorio de datos (EDA), preprocesamiento y balanceo con SMOTE, entrenamiento y comparativa rigurosa de 5 familias de algoritmos de Machine Learning (incluyendo MLP Deep Learning), tracking de experimentos con MLflow, explicabilidad e interpretabilidad con SHAP, motor de 6 reglas de negocio de la ayuda oficial Gaztelagun (Gobierno Vasco), webhook con n8n y aplicación web interactiva en Streamlit.

---

## 2. ARQUITECTURA Y FUENTES DE DATOS INTEGRADAS

El proyecto implementa una arquitectura **Data Lakehouse** que procesa datos de 4 categorías clave:

### A. Portales Inmobiliarios para Web Scraping (Mercado Real de Alquiler en Euskadi)
- **Habitaclia (`src/extraction/scraper.py`)**: Scraping automatizado de ofertas de alquiler con headers emulados y control de tasa (rate limiting).
- **Pisos.com (`src/extraction/pisos_scraper.py`)**: Extracción de precios totales, €/m² y características en Bizia, Gipuzkoa y Araba.
- **EnAlquiler (`src/extraction/multi_portal_scraper.py`)**: Alquileres reales con fianza exigida, estancias y ubicación precisa.
- **Inmobiliaria Chomon (`src/extraction/multi_portal_scraper.py`)**: Portal líder local en Bizkaia (Bilbao, Barakaldo, Santurtzi, Portugalete, Basauri).
- **Inmobiliaria Quorum (`src/extraction/multi_portal_scraper.py`)**: Inmobiliaria especializada en Bizkaia y Araba (Bilbao Abando, Vitoria-Gasteiz, Getxo, Durango).
- **YaEncontre (`src/extraction/multi_portal_scraper.py`)**: Cobertura en Gipuzkoa (Donostia-San Sebastián, Irun, Zarautz, Errenteria).
- **Milanuncios (`src/extraction/multi_portal_scraper.py`)**: Alquileres de particulares con opciones de menor coste.

### B. APIs y Registros Oficiales de Vivienda (Gobierno Vasco y Ministerio)
- **Open Data Euskadi / Visesa WS (`src/extraction/api_client.py`)**: Promociones oficiales de Vivienda de Protección Oficial (VPO) y régimen de alquiler protegido.
- **Bizilagun (`src/extraction/official_housing_sources.py`)**: Registro Oficial de Contratos y Fianzas de Alquiler del Gobierno Vasco (precios medios reales pactados, volumen de contratos formalizados y fianza media).
- **Etxebide (`src/extraction/official_housing_sources.py`)**: Servicio Vasco de Vivienda. Registro de demanda juvenil de alquiler social por municipio.
- **MIVAU (`src/extraction/official_housing_sources.py`)**: Sistema Estatal de Precios de Referencia del Alquiler (Ministerio de Vivienda y Agenda Urbana), con rangos inferior, mediano y superior en €/m² para zonas de mercado residencial tensionado.

### C. Indicadores Socioeconómicos, Laborales y Juveniles
- **Eustat / Udalmap (`src/indicators/udalmap_client.py`)**: Indicadores municipales de población total y joven (18-34 años), renta familiar media disponible, renta personal y tasas de desempleo juvenil.
- **Observatorio Vasco de la Juventud - OVJ (`src/indicators/ovj_client.py`)**: Salario neto medio mensual de la juventud asalariada en Euskadi (~1.380 €/mes) y tasas oficiales de emancipación.
- **Lanbide**: Estadísticas de paro juvenil y contratación laboral.

### D. Redes de Conectividad y Transporte Público (`src/indicators/transport_client.py`)
- **Consorcio de Transportes de Bizkaia (CTB)**: Metro Bilbao (Líneas 1, 2 y 3).
- **Euskotren / Topo**: Conexión ferroviaria interurbana en Bizkaia y Gipuzkoa.
- **TUVISA**: Red de autobuses urbanos de Vitoria-Gasteiz y BEI (Bus Eléctrico Inteligente).
- **Dbus**: Red de transporte de Donostia-San Sebastián.
- **Cálculo de Conectividad**: Cada municipio recibe un `indice_conectividad` (1 a 10) y cada inmueble incluye la distancia en metros (`distancia_transporte_m`) al nodo de transporte público más cercano.

### E. Estandarización Relacional por Código INE de 5 Dígitos
Para evitar discrepancias tipográficas ("Bilbao" vs "Bilbo", "Donostia" vs "San Sebastián"), todas las entidades se indexan y enlazan mediante el código INE oficial (`src/extraction/models.py` - `resolver_codigo_ine()`):
- **Bilbao**: `48020` | **Donostia-San Sebastián**: `20069` | **Vitoria-Gasteiz**: `01059`
- **Barakaldo**: `48013` | **Getxo**: `48044` | **Portugalete**: `48078` | **Santurtzi**: `48082`
- **Basauri**: `48015` | **Irun**: `20045` | **Errenteria**: `20067` | **Zarautz**: `20079`
- **Durango**: `48027` | **Eibar**: `20030` | **Agurain**: `01051`

---

## 3. ARQUITECTURA TÉCNICA BIG DATA (BDA + SBD)

### 1. Data Lake en Apache Hadoop (HDFS) (`src/hdfs/client.py`)
- **WebHDFS REST API**: Cliente HTTP para interactuar con el NameNode (puerto por defecto 9870).
- **Particionado Temporal Estricto**:
  - `/data/reto1/raw/vivienda/api/{YYYYMMDD}/`
  - `/data/reto1/raw/vivienda/scraping/{YYYYMMDD}/`
  - `/data/reto1/raw/vivienda/multiportal/{YYYYMMDD}/`
  - `/data/reto1/raw/vivienda/bizilagun/{YYYYMMDD}/`
  - `/data/reto1/raw/indicadores/{YYYYMMDD}/`
  - `/data/reto1/raw/transporte/{YYYYMMDD}/`
- **Integridad Criptográfica**: Cada fichero subido genera un hash SHA-256. Al descargar o recuperar, se valida criptográficamente que no haya corrupción de bits.
- **Modo Emulación Local**: Si el clúster Hadoop no está levantado en Docker/red, conmuta transparentemente a `data/hdfs_storage/` manteniendo la misma API y validación de checksums.

### 2. Event Streaming con Apache Kafka (`src/kafka/`)
- **Tópico Oficial**: `euskadi-anuncios-inmobiliarios`.
- **Productor Python (`src/kafka/producer.py`)**: Publica eventos JSON de anuncios inmobiliarios con clave de particionado natural (`key=municipio`).
- **Consumidor Python (`src/kafka/consumer.py`)**: Consume eventos en streaming por lotes (`consume_batch()`), validando cada mensaje contra el esquema Pydantic `HousingAd` y descartando mensajes malformados.
- **Adaptador en Memoria (`src/kafka/mock_broker.py`)**: Permite ejecutar pruebas unitarias continuas sin depender de un daemon Kafka activo.

### 3. Almacenamiento y Analítica NoSQL en MongoDB (`src/database/`)
- **Decisión de Modelado Híbrido**:
  - Colección `viviendas`: Referencing hacia `municipios` mediante el campo `codigo_municipio` (código INE de 5 dígitos).
  - Colección `municipios`: Embedding documental con indicadores Udalmap, salarios OVJ, contratos de Bizilagun, demanda Etxebide y conectividad de transporte.
- **Limpieza Automatizada (`src/database/cleaning.py`)**: Detección de duplicados, casteo de tipos numéricos, imputación de valores faltantes y eliminación de outliers de precio con rango intercuartílico (IQR).
- **Aggregation Pipelines (Rúbrica SBD RA3) (`src/database/aggregations.py`)**:
  - *Pipeline 1 (Agrupación)*: `$match` $\to$ `$group` $\to$ `$project` $\to$ `$sort` para calcular precio medio, mínimo, máximo y €/m² por municipio.
  - *Pipeline 2 (Cruce Relacional)*: `$match` $\to$ `$lookup` $\to$ `$unwind` $\to$ `$project` $\to$ `$sort` para cruzar viviendas con indicadores municipales y calcular la **Tasa de Esfuerzo Salarial**:
    $$\text{Tasa de esfuerzo (\%)} = \left(\frac{\text{Precio Alquiler}}{\text{Salario Medio Joven Mes}}\right) \times 100$$
  - *Pipeline 3 (Multifaceta)*: `$match` $\to$ `$facet` con 3 dimensiones simultáneas (distribución por categoría de accesibilidad, top 5 asequibles y desglose por tipo de operación).
- **Optimización de Índices (`src/database/indexes.py`)**:
  - Creación de índices compuestos: `{municipio: 1, precio: 1}` y `{codigo_municipio: 1}`.
  - Análisis con `explain("executionStats")`, demostrando la transición de `COLLSCAN` (escaneo completo de la colección) a `IXSCAN` con reducción drástica de documentos examinados.
- **Atomicidad y Consistencia (`src/database/consistency.py`)**:
  - Demostración de operaciones atómicas ACID a nivel de documento único con `find_one_and_update` simulando la reserva/manifestación de interés de un joven sobre una vivienda sin colisiones de concurrencia.

---

## 4. ARQUITECTURA DE MACHINE LEARNING E IA (SAA + PIA + MIA)

### 1. Preparación de Datos y Balanceo (`SAA + PIA + MIA/src/pipeline.py`)
- Target binario: `viable` (1) vs `no_viable` (0) para la emancipación juvenil.
- Preprocesamiento con `ColumnTransformer`: `StandardScaler` para variables numéricas (ingresos, precio de alquiler, edad, estabilidad laboral) y `OneHotEncoder` para variables categóricas (municipio, tipo de contrato, régimen de vivienda).
- Balanceo con `SMOTE` (Synthetic Minority Over-sampling Technique) para resolver el desbalance natural de jóvenes con capacidad económica suficiente en zonas tensionadas.

### 2. Comparativa de 5 Modelos de Machine Learning (`src/ml_models.py`)
Se entrenan, evalúan y guardan 5 modelos bajo las mismas particiones estratificadas (80% train / 20% test):
1. **Regresión Logística**: Modelo lineal de referencia (baseline) interpretable.
2. **Random Forest Classifier**: Ensamble no lineal de árboles de decisión con bootstrapping.
3. **XGBoost (Extreme Gradient Boosting)**: Algoritmo de boosting optimizado con regularización L1/L2.
4. **LightGBM**: Gradient boosting basado en histogramas para alta velocidad de convergencia.
5. **Multi-Layer Perceptron (MLP Classifier)**: Red neuronal profunda feed-forward con capas ocultas (64, 32), funciones de activación ReLU y regularización con optimizador Adam.
- Métricas calculadas para cada modelo: **Accuracy, Precision, Recall, F1-Score, ROC-AUC** y Matrices de Confusión.

### 3. MLOps y Experiment Tracking con MLflow (`src/mlflow_tracker.py`)
- Registro centralizado de parámetros de hiperparámetros (`learning_rate`, `n_estimators`, `max_depth`, `hidden_layer_sizes`).
- Registro de métricas de validación y artefactos (matrices de confusión, curvas ROC guardadas como PNG y modelos serializados `.joblib`).

### 4. Explicabilidad del Modelo con SHAP (`notebooks/03_explicabilidad_shap.py`)
- Implementación de **SHAP (SHapley Additive exPlanations)**.
- Generación de gráficos globales (*Summary Plot / Beeswarm*) e individuales (*Force Plot / Waterfall*), demostrando qué variables pesan más en la predicción (precio de alquiler vs salario neto del joven).

### 5. Motor de Reglas de Negocio — Ayuda Gaztelagun (`src/reglas.py`)
Simulador normativo de la ayuda del Gobierno Vasco para jóvenes de 18 a 35 años:
- **Cuantía**: Cubre hasta el 50% de la renta mensual de alquiler con un tope máximo de **300 €/mes**.
- **Límites de Precio de Alquiler Subvencionable**:
  - Bilbao, Donostia-San Sebastián y Vitoria-Gasteiz: Renta máxima de 800 €/mes.
  - Municipios metropolitanos y cabeceras comarcales: Renta máxima de 750 €/mes.
  - Resto de municipios: Renta máxima de 650 €/mes.
- **Regla Estricta de Ingresos (`R1_SUPERACION_INGRESOS`)**:
  - Límite máximo de ingresos brutos anuales de Gaztelagun: **25.200 €/año (~2.100 € netos/mes)**.
  - Si un usuario ingresa más de 2.100 €/mes, la ayuda queda automáticamente denegada por superar el límite legal.
- **Prioridad de Reglas**:
  1. `R1_SUPERACION_INGRESOS`: Denegación por superar ingresos máximos permitidos (> 2.100 €/mes).
  2. `R2_LIMITE_PRECIO_ALQUILER`: Denegación si el alquiler supera el límite municipal (650€ - 800€).
  3. `R3_REQUISITO_EDAD`: Denegación si no está en el rango 18-35 años.
  4. `R4_EMANCIPACION_VIABLE_CON_AYUDA`: Concesión de 300 €/mes si tras la ayuda el esfuerzo $\le 30\%$.
  5. `R5_ESFUERZO_LIMITE`: Concesión con advertencia si tras la ayuda el esfuerzo está entre 30% y 40%.
  6. `R6_INSUFICIENCIA_FINANCIERA`: Denegación si aun con los 300 €/mes el esfuerzo sigue superando el 40%.
- **Integración con n8n (`src/n8n.py`)**: Envío de webhooks automáticos con el dictamen de concesión/denegación para flujos de notificación por email o mensajería.

---

## 5. CAPA DE INTERFACES VISUALES Y CUADROS DE MANDO

El proyecto ofrece dos aplicaciones gráficas interactivas independientes:

### 1. Dashboard Cartográfico Leaflet (`BDA + SBD/dashboard/dashboard.html`)
- Servidor local en puerto `8080` (con selección dinámica si estuviera ocupado).
- Mapa Leaflet centrado en Euskadi con teselas *Esri World Street Map* (mar azul, relieve y carreteras nítidas sin API Key).
- Polígonos de límites provinciales para Bizkaia, Gipuzkoa y Araba.
- **Catálogo Multifuente Estandarizado (35+ inmuebles)**:
  - Chips de filtro por portal (*Todos, EnAlquiler, Inmobiliaria Chomon, Inmobiliaria Quorum, YaEncontre, Milanuncios, Habitaclia, Pisos.com, Visesa VPO*).
  - Buscador reactivo por código INE (`48020`, `20069`, etc.), municipio o barrio.
  - Columnas enriquecidas con fianza exigida (meses) y distancia al transporte público en metros.
- Comparador visual de esfuerzo salarial municipal y simulador del impacto de Gaztelagun (-300 €/mes).

### 2. Aplicación Streamlit / Servidor Dual Web (`SAA + PIA + MIA/app/streamlit_app.py`)
- Diseñada con arquitectura dual: puede ejecutarse tanto con `streamlit run` como directamente con `python streamlit_app.py` gracias a su servidor HTTP autónomo incorporado.
- Comparativa visual de los 5 modelos de Machine Learning (matrices de confusión, curvas ROC y métricas F1).
- Gráficos interactivos de explicabilidad SHAP.
- **Simulador Interactivo de Concesión de Ayudas**:
  - Endpoint backend `POST /api/evaluar` conectado al motor de reglas Python.
  - Validación en vivo de edad, ingresos, precio de alquiler y municipio.

---

## 6. AUTOMATIZACIÓN DE GIT Y NORMAS COMPARTIDAS (AGENTS.MD)

El desarrollo se rige por las directrices obligatorias de [`AGENTS.md`](file:///c:/Users/aldeb/Jon/IA%20y%20Big%20Data/Reto%201/AGENTS.md):

1. **Configuración de Identidades y Ramas**:
   - Cada puesto local define su rama personal (`git config dev.branch dev-<nombre>`). Jon utiliza `dev-jon` y el compañero `dev-companero`.
2. **Flujo de Integración en 4 Niveles**:
   - `dev-jon` / `dev-companero`: Ramas de trabajo diario.
   - `test`: Rama de integración donde se fusionan los cambios de ambos desarrolladores y se valida la estabilidad.
   - `main`: Rama de producción protegida con código 100% probado.
3. **Protocolo Pre-Commit**:
   - Obligatorio pasar la suite completa de pruebas unitarias (`pytest tests/`) antes de crear cualquier commit o merge.
   - Inspección automática para evitar secretos, claves privadas o ficheros `.env`.
4. **Script de Automatización (`scripts/git_workflow.py`)**:
   - Automatiza el ciclo completo: test $\to$ commit en `dev-jon` $\to$ merge en `test` $\to$ test en `test` $\to$ promoción a `main` $\to$ sincronización final de `dev-jon`.
   - **Prohibición estricta**: Prohibido usar `git reset --hard`, `git push --force` o `git clean -fd`.

---

## 7. SUITE DE PRUEBAS AUTOMATIZADAS (PYTEST)

El proyecto cuenta con **33 pruebas unitarias y de integración** automatizadas en `tests/` que se ejecutan en ~8 segundos:

1. `tests/test_analysis.py`: Análisis integral y exportación JSON del estudio municipal.
2. `tests/test_extraction.py`: Esquema `HousingAd`, API Visesa, scraper Habitaclia y Pisos.com.
3. `tests/test_hdfs.py`: Subida, particionado y verificación de integridad criptográfica SHA-256.
4. `tests/test_indicators.py`: Clientes Udalmap, OVJ y cálculo del esfuerzo salarial.
5. `tests/test_integration.py`: Pipeline completo end-to-end simulado.
6. `tests/test_kafka.py`: Productor, consumidor en streaming y broker en memoria.
7. `tests/test_ml_pipeline.py`: Pipeline ML, entrenamiento de 5 modelos, SMOTE, MLP, 6 reglas y n8n.
8. `tests/test_mongodb.py`: DataLoader, consultas, 3 pipelines de agregación, índices y atomicidad.
9. `tests/test_multi_portal_extraction.py`: Scraper multiportal (EnAlquiler, Chomon, Quorum, YaEncontre, Milanuncios), Bizilagun, Etxebide, MIVAU, conectividad de transporte y resolución de códigos INE.

---

## 8. GUÍA RÁPIDA DE COMANDOS DE EJECUCIÓN

| Acción | Comando |
| :--- | :--- |
| **Menú Interactivo Principal** | `python main.py` |
| **Ejecutar Pipeline Big Data Multifuente** | `python scripts/run_pipeline.py` |
| **Abrir Dashboard Cartográfico Leaflet** | `python main.py --subject bda_sbd --visual` |
| **Entrenar Modelos ML y Abrir App** | `python main.py --subject saa_pia_mia` |
| **Ejecutar Suite de Tests (33 tests)** | `pytest tests/ -v` |
| **Generar PDF Técnico de Entrega** | `python main.py --pdf` |
| **Flujo Seguro de Git Automatizado** | `python scripts/git_workflow.py "Mensaje del commit"` |

---

## 9. ÁRBOL DE DIRECTORIOS DEL PROYECTO

```text
c:\Users\aldeb\Jon\IA y Big Data\Reto 1\
├── AGENTS.md                               <- Normas obligatorias de Git y desarrollo colaborativo
├── main.py                                 <- Orquestador general multiasignatura del repositorio
├── pyproject.toml                          <- Configuración de pytest e import-modes
├── requirements.txt                        <- Dependencias Python del entorno virtual
├── data/
│   ├── raw/                                <- Ficheros crudos (JSON/CSV) de API, Scraping e Indicadores
│   └── hdfs_storage/                       <- Directorio de emulación local del Data Lake HDFS
├── scripts/
│   ├── git_workflow.py                     <- Script de automatización de ramas y pruebas de Git
│   ├── run_pipeline.py                     <- Orquestador del pipeline de 5 fases de Big Data
│   ├── update_dashboard.py                 <- Actualizador automático de inmuebles en dashboard.html
│   └── generate_delivery_pdf.py            <- Compilador del informe académico en PDF
├── src/                                    <- Código fuente modular principal
│   ├── extraction/
│   │   ├── models.py                       <- Modelos Pydantic (HousingAd) y resolver_codigo_ine()
│   │   ├── api_client.py                   <- Cliente REST para Visesa / Open Data Euskadi
│   │   ├── scraper.py                      <- Web scraper para Habitaclia
│   │   ├── pisos_scraper.py                <- Web scraper para Pisos.com
│   │   ├── multi_portal_scraper.py         <- Scraper multicanal (EnAlquiler, Chomon, Quorum, etc.)
│   │   └── official_housing_sources.py     <- Extractor de Bizilagun, Etxebide y MIVAU
│   ├── indicators/
│   │   ├── models.py                       <- Modelos de indicadores socioeconómicos
│   │   ├── udalmap_client.py               <- Cliente API Udalmap (Eustat)
│   │   ├── ovj_client.py                   <- Cliente Observatorio Vasco Juventud
│   │   └── transport_client.py             <- Conectividad de Metro, Tren, Tranvía y Bus
│   ├── hdfs/
│   │   └── client.py                       <- Cliente HDFS / WebHDFS con checksum SHA-256
│   ├── kafka/
│   │   ├── producer.py                     <- Productor Kafka con serialización JSON
│   │   ├── consumer.py                     <- Consumidor Kafka con validación de esquema
│   │   └── mock_broker.py                  <- Broker en memoria para CI/CD sin Kafka externo
│   ├── database/
│   │   ├── mongo_client.py                 <- Gestor PyMongo con fallback a mongomock
│   │   ├── data_loader.py                  <- Carga relacional con código INE de 5 dígitos
│   │   ├── cleaning.py                     <- Limpieza y remoción de outliers IQR
│   │   ├── queries.py                      <- Consultas analíticas avanzadas
│   │   ├── aggregations.py                 <- 3 Aggregation Pipelines ($group, $lookup, $facet)
│   │   ├── indexes.py                      <- Optimización de índices con explain()
│   │   └── consistency.py                  <- Operaciones atómicas ACID find_one_and_update
│   ├── analysis/
│   │   └── housing_study.py                <- Estudio sociológico y tasa de esfuerzo juvenil
│   ├── ml_models.py                        <- 5 modelos ML (Logistic, RF, XGB, LGBM, MLP)
│   ├── pipeline.py                         <- Pipeline de preprocesamiento, StandardScaler y SMOTE
│   ├── reglas.py                           <- Motor de 6 reglas de negocio de Gaztelagun
│   ├── n8n.py                              <- Integración de webhooks de notificación con n8n
│   └── mlflow_tracker.py                   <- Tracker de experimentos y métricas MLflow
├── tests/                                  <- Suite completa de 33 pruebas unitarias y de integración
│   ├── test_analysis.py
│   ├── test_extraction.py
│   ├── test_hdfs.py
│   ├── test_indicators.py
│   ├── test_integration.py
│   ├── test_kafka.py
│   ├── test_ml_pipeline.py
│   ├── test_mongodb.py
│   └── test_multi_portal_extraction.py
├── BDA + SBD/                              <- Módulo del Reto BDA + SBD (Estructura académica aislada)
│   ├── dashboard/
│   │   └── dashboard.html                  <- Dashboard Leaflet cartográfico interactivo
│   ├── main.py                             <- Punto de entrada de BDA + SBD
│   ├── scripts/
│   │   └── run_pipeline.py
│   └── src/                                <- Copia sincronizada de src/ para BDA + SBD
└── SAA + PIA + MIA/                        <- Módulo del Reto SAA + PIA + MIA
    ├── app/
    │   └── streamlit_app.py                <- Interfaz interactiva de ML, SHAP y simulador de ayudas
    ├── notebooks/
    │   ├── 01_eda.py                       <- Análisis exploratorio de datos
    │   ├── 02_entrenamiento_modelos.py     <- Entrenamiento y exportación de modelos
    │   └── 03_explicabilidad_shap.py       <- Análisis de explicabilidad con SHAP
    └── src/                                <- Copia sincronizada de src/ para ML y reglas
```
