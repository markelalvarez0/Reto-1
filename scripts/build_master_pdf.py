#!/usr/bin/env python3
"""
scripts/build_master_pdf.py
Generador de la Versión Definitiva, Exhaustiva y Ultra-Detallada del
Documento Maestro de Contexto Técnico y Arquitectura para el Reto 1 (IABD 2026-27).
"""

import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos

PDF_OUTPUT_PATH = "DOCUMENTO_MAESTRO_CONTEXTO_TECNICO_RETO1.pdf"


class MasterContextPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        
        # Cargar fuentes Unicode de Windows para soporte de acentos, eñes y euro (€)
        font_regular = "C:/Windows/Fonts/arial.ttf"
        font_bold = "C:/Windows/Fonts/arialbd.ttf"
        font_italic = "C:/Windows/Fonts/ariali.ttf"
        font_mono = "C:/Windows/Fonts/consola.ttf"
        
        if os.path.exists(font_regular) and os.path.exists(font_bold):
            self.add_font("ArialU", "", font_regular)
            self.add_font("ArialU", "B", font_bold)
            if os.path.exists(font_italic):
                self.add_font("ArialU", "I", font_italic)
            self.font_main = "ArialU"
        else:
            self.font_main = "helvetica"

        if os.path.exists(font_mono):
            self.add_font("ConsolasU", "", font_mono)
            self.font_mono = "ConsolasU"
        else:
            self.font_mono = "courier"

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.font_main, "I", 7.5)
            self.set_text_color(100, 116, 139) # Slate 500
            self.cell(0, 7, "IABD 2026-27 · Documento Maestro de Contexto Técnico · Reto 1 Vivienda Euskadi", 0, 0, "L")
            self.cell(0, 7, "Jon Larrea · Single Source of Truth", 0, 1, "R")
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.3)
            self.line(10, 15, 200, 15)
            self.ln(3)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12)
            self.set_font(self.font_main, "", 7.5)
            self.set_text_color(148, 163, 184) # Slate 400
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.3)
            self.line(10, 285, 200, 285)
            self.cell(0, 7, f"Documento Técnico Definitivo · Página {self.page_no()}", 0, 0, "C")

    # Componentes tipográficos y de diseño
    def chapter_title(self, num_str, title_str):
        self.ln(3)
        self.set_fill_color(15, 23, 42) # Slate 900
        self.set_text_color(255, 255, 255)
        self.set_font(self.font_main, "B", 11)
        self.cell(0, 8, f"  {num_str}. {title_str.upper()}", 0, 1, "L", fill=True)
        self.ln(3)
        self.set_text_color(30, 41, 59)

    def section_title(self, title_str):
        self.ln(2)
        self.set_text_color(2, 132, 199) # Sky 600
        self.set_font(self.font_main, "B", 10)
        self.cell(0, 6, title_str, 0, 1, "L")
        self.set_draw_color(2, 132, 199)
        self.set_line_width(0.3)
        self.line(self.get_x(), self.get_y(), self.get_x() + 45, self.get_y())
        self.ln(2)
        self.set_text_color(30, 41, 59)

    def sub_section_title(self, title_str):
        self.set_text_color(71, 85, 105) # Slate 600
        self.set_font(self.font_main, "B", 8.8)
        self.cell(0, 5, title_str, 0, 1, "L")
        self.ln(1)
        self.set_text_color(30, 41, 59)

    def paragraph(self, text):
        self.set_font(self.font_main, "", 8.5)
        self.set_text_color(51, 65, 85) # Slate 700
        self.multi_cell(0, 4.3, text)
        self.ln(2)

    def bullet_point(self, label, text):
        self.set_font(self.font_main, "B", 8.2)
        self.set_text_color(30, 41, 59)
        self.write(4.2, f"• {label}: ")
        self.set_font(self.font_main, "", 8.2)
        self.set_text_color(51, 65, 85)
        self.write(4.2, text + "\n")

    def callout_box(self, title, text, bg_rgb=(240, 249, 255), border_rgb=(2, 132, 199)):
        self.set_font(self.font_main, "", 8)
        lines_count = len(self.multi_cell(182, 4, text, dry_run=True, output="LINES"))
        box_h = 7 + lines_count * 4 + 2
        
        if self.get_y() + box_h > 275:
            self.add_page()
            
        self.set_fill_color(*bg_rgb)
        self.set_draw_color(*border_rgb)
        self.set_line_width(0.3)
        x = 10
        self.set_font(self.font_main, "B", 8.5)
        self.set_text_color(*border_rgb)
        
        y = self.get_y()
        self.rect(x, y, 190, box_h, style="DF")
        self.set_xy(x + 4, y + 2)
        self.set_font(self.font_main, "B", 8.5)
        self.cell(182, 4.5, title, 0, 1, "L")
        self.set_x(x + 4)
        self.set_font(self.font_main, "", 8)
        self.set_text_color(30, 41, 59)
        self.multi_cell(182, 4, text)
        self.set_xy(x, y + box_h + 3)

    def code_block(self, code_text, title=None):
        if self.get_y() > 260:
            self.add_page()
        if title:
            self.set_fill_color(241, 245, 249) # Slate 100
            self.set_font(self.font_main, "B", 7.5)
            self.set_text_color(71, 85, 105)
            self.cell(190, 4.5, f" # {title}", border="LTR", fill=True)
            self.ln(4.5)
            
        self.set_fill_color(248, 250, 252) # Slate 50
        self.set_draw_color(203, 213, 225) # Slate 300
        self.set_line_width(0.2)
        self.set_font(self.font_mono, "", 7.2)
        self.set_text_color(15, 23, 42) # Slate 900
        
        lines = code_text.strip().split("\n")
        for line in lines:
            # Reemplazar tabulaciones por 2 espacios
            clean_l = line.replace("\t", "  ")
            self.multi_cell(190, 3.7, clean_l, border="LR", fill=True)
            
        self.cell(190, 1.5, "", border="LBR", fill=True)
        self.ln(3)
        self.set_font(self.font_main, "", 8.5)

    def table_header(self, cols, widths):
        if self.get_y() > 265:
            self.add_page()
        self.set_fill_color(226, 232, 240) # Slate 200
        self.set_font(self.font_main, "B", 7.5)
        self.set_text_color(15, 23, 42)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.2)
        for text, w in zip(cols, widths):
            self.cell(w, 5.5, str(text), border=1, align="L", fill=True)
        self.ln(5.5)

    def table_row(self, cols, widths=None, is_even=False):
        if widths is None or isinstance(widths, bool):
            if isinstance(cols, (list, tuple)) and len(cols) > 0 and isinstance(cols[-1], (list, tuple)):
                is_even = widths if isinstance(widths, bool) else False
                widths = cols[-1]
                cols = cols[:-1]
                
        if self.get_y() > 272:
            self.add_page()
        bg = (248, 250, 252) if is_even else (255, 255, 255)
        self.set_fill_color(*bg)
        self.set_font(self.font_main, "", 7.2)
        self.set_text_color(51, 65, 85)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.15)
        for text, w in zip(cols, widths):
            self.cell(w, 4.8, str(text), border=1, align="L", fill=True)
        self.ln(4.8)


def generate_master_pdf():
    pdf = MasterContextPDF()
    pdf.set_margins(10, 12, 10)

    # =============================================================
    # PORTADA FORMAL Y METADATOS
    # =============================================================
    pdf.add_page()
    pdf.set_draw_color(2, 132, 199) # Sky 600
    pdf.set_line_width(0.8)
    pdf.rect(10, 10, 190, 277)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.3)
    pdf.rect(12, 12, 186, 273)

    pdf.set_y(32)
    pdf.set_font(pdf.font_main, "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "DOCUMENTO MAESTRO DE CONTEXTO TÉCNICO", 0, 1, "C")
    pdf.set_font(pdf.font_main, "B", 13)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(0, 7, "SINGLE SOURCE OF TRUTH (SST)", 0, 1, "C")

    pdf.set_font(pdf.font_main, "", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, "Curso de Especialización en Inteligencia Artificial y Big Data (IABD 2026-27)", 0, 1, "C")

    pdf.ln(8)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(20, 60, 170, 24, "DF")
    pdf.set_xy(22, 63)
    pdf.set_font(pdf.font_main, "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(166, 6, "RETO 1: ACCESO A LA VIVIENDA PARA JÓVENES EN EUSKADI", 0, 1, "C")
    pdf.set_xy(22, 71)
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(166, 5, "Resolución Intermodular de 5 Asignaturas Académicas: BDA, SBD, SAA, PIA y MIA", 0, 1, "C")
    pdf.set_xy(22, 77)
    pdf.set_font(pdf.font_main, "I", 7.5)
    pdf.cell(166, 4, "Arquitectura de Software, Modelado NoSQL, Pipeline Big Data, Machine Learning, Reglas y Pruebas", 0, 1, "C")

    # Cuadro de Metadatos del Sistema
    pdf.set_y(94)
    meta_w = [45, 125]
    pdf.table_header(["METADATO DE PRODUCCIÓN", "VALOR DE AUDITORÍA TÉCNICA"], meta_w)
    pdf.table_row(["Autoría y Desarrolladores", "Jon Larrea & Segundo Desarrollador Colaborador", meta_w], False)
    pdf.table_row(["Rama de Trabajo Activa", "dev-jon (Conforme a AGENTS.md, integración en 'test' y 'main')", meta_w], True)
    pdf.table_row(["Versión del Repositorio", "1.0.0-PROD (Validación con 33/33 Pruebas Automatizadas Pytest)", meta_w], False)
    pdf.table_row(["Entorno de Ejecución", "CPython 3.12.14 / Windows 10 x64 / Virtualenv .venv", meta_w], True)
    pdf.table_row(["Cobertura de Asignaturas", "Bloque 1 (BDA + SBD) | Bloque 2 (SAA + PIA + MIA)", meta_w], False)
    pdf.table_row(["Base de Datos NoSQL", "MongoDB 7.0 / PyMongo 4.6 (Modelado Híbrido Referencing + Embedding)", meta_w], True)
    pdf.table_row(["Streaming y Data Lake", "Apache Kafka (euskadi-anuncios-inmobiliarios) / Apache Hadoop (HDFS WebHDFS)", meta_w], False)
    pdf.table_row(["Modelo ML Seleccionado", "XGBoost Classifier (F1-Score: 0.8772, ROC-AUC: 0.9320) + SHAP Explainability", meta_w], True)
    pdf.table_row(["Estado del Repositorio Git", "Working tree clean, SHA-256 criptográfico validado en HDFS", meta_w], False)

    # Índice de Contenidos
    pdf.set_y(155)
    pdf.set_font(pdf.font_main, "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "ÍNDICE GENERAL DE ESPECIFICACIONES TÉCNICAS", 0, 1, "L")
    pdf.set_draw_color(15, 23, 42)
    pdf.set_line_width(0.3)
    pdf.line(10, 162, 70, 162)
    pdf.ln(3)

    toc_items = [
        ("1", "DICCIONARIO DE DATOS Y ESQUEMAS EXACTOS (PYDANTIC Y MONGODB)", "Pág. 2"),
        ("  1.1", "Modelo Pydantic HousingAd (22 campos, tipos, descripciones y validación)", "Pág. 2"),
        ("  1.2", "Modelos de Indicadores Socioeconómicos (Udalmap, OVJ, Bizilagun, Etxebide, MIVAU)", "Pág. 2"),
        ("  1.3", "Estructura JSON Completa de la Colección 'viviendas' en MongoDB", "Pág. 3"),
        ("  1.4", "Estructura JSON Completa de la Colección 'municipios' en MongoDB", "Pág. 3"),
        ("  1.5", "Mapeo Exhaustivo de los 32 Códigos INE Municipales y Algoritmo Bilingüe", "Pág. 4"),
        ("2", "FLUJO DE DATOS PASO A PASO: LAS 5 FASES DE RUN_PIPELINE.PY", "Pág. 5"),
        ("  2.1", "Fase 1: Ingesta Multicanal (API REST Visesa y Scrapers con Fallback Resiliente)", "Pág. 5"),
        ("  2.2", "Fase 2: Enriquecimiento Socioeconómico y Matriz de Pesos de Transporte", "Pág. 6"),
        ("  2.3", "Fase 3: Data Lake en Apache Hadoop HDFS con Integridad SHA-256", "Pág. 6"),
        ("  2.4", "Fase 4: Event Streaming en Apache Kafka y Broker en Memoria", "Pág. 7"),
        ("  2.5", "Fase 5: Ingesta NoSQL y Agregación Analítica de Tasa de Esfuerzo", "Pág. 7"),
        ("3", "LÓGICA INTERNA DE MONGODB (PYMONGO Y AGREGACIONES)", "Pág. 8"),
        ("  3.1", "Reglas Exactas de Limpieza, Deduplicación e Imputación en cleaning.py", "Pág. 8"),
        ("  3.2", "Código MQL Íntegro de los 3 Aggregation Pipelines (Rúbrica SBD RA3)", "Pág. 8"),
        ("  3.3", "Optimización de Índices Compuestos y Auditoría de Rendimiento con explain()", "Pág. 9"),
        ("  3.4", "Consistencia Atómica ACID a Nivel de Documento con find_one_and_update", "Pág. 10"),
        ("4", "ESPECIFICACIÓN COMPLETA DE MACHINE LEARNING (SAA + PIA + MIA)", "Pág. 11"),
        ("  4.1", "Vector de Entrada (21 Dimensiones) y Función Sigmoide del Target es_viable", "Pág. 11"),
        ("  4.2", "Hiperparámetros Exhaustivos de los 5 Algoritmos (Logistic, RF, XGB, SVM, MLP)", "Pág. 12"),
        ("  4.3", "Métricas Comparativas en Test y Selección Justificada de XGBoost", "Pág. 13"),
        ("  4.4", "Interpretabilidad y Valores de Shapley con SHAP", "Pág. 13"),
        ("  4.5", "Motor de 6 Reglas de Negocio de Gaztelagun y Límite Legal de 2.100 €/mes", "Pág. 14"),
        ("  4.6", "Integración con Webhook n8n y Payload JSON de Automatización", "Pág. 15"),
        ("5", "ARQUITECTURA DE INTERFACES, SINCRONIZACIÓN Y ENTREGABLES", "Pág. 16"),
        ("  5.1", "Arquitectura Dual de streamlit_app.py y Endpoint POST /api/evaluar", "Pág. 16"),
        ("  5.2", "Inyector Programático update_dashboard.py y Dashboard Leaflet Cartográfico", "Pág. 17"),
        ("  5.3", "Estructura de Directorios y Política de Sincronización de src/", "Pág. 17"),
        ("6", "CONTRATOS DE MÓDULOS, TESTS Y CONFIGURACIÓN", "Pág. 18"),
        ("  6.1", "Contratos de Interfaz de Clases y Funciones de src/", "Pág. 18"),
        ("  6.2", "Auditoría Detallada de las 33 Pruebas Automatizadas de pytest", "Pág. 19"),
        ("  6.3", "Ficheros de Configuración: requirements.txt y pyproject.toml", "Pág. 20")
    ]

    for num, txt, pg in toc_items:
        is_main = not num.startswith(" ")
        pdf.set_font(pdf.font_main, "B" if is_main else "", 7.8)
        pdf.set_text_color(15, 23, 42) if is_main else pdf.set_text_color(71, 85, 105)
        pdf.cell(15, 4.2, num, 0, 0, "L")
        pdf.cell(155, 4.2, txt, 0, 0, "L")
        pdf.cell(20, 4.2, pg, 0, 1, "R")

    # =============================================================
    # CAPÍTULO 1: DICCIONARIO DE DATOS Y ESQUEMAS EXACTOS
    # =============================================================
    pdf.add_page()
    pdf.chapter_title("1", "DICCIONARIO DE DATOS Y ESQUEMAS EXACTOS (PYDANTIC Y MONGODB)")
    
    pdf.section_title("1.1 Modelo Pydantic HousingAd (src/extraction/models.py)")
    pdf.paragraph(
        "El modelo HousingAd es el estándar de datos canónico del proyecto. Todos los scrapers, clientes de APIs oficiales "
        "y consumidores de Kafka transforman obligatoriamente sus registros brutos en esta clase Pydantic antes de su persistencia. "
        "La clase valida tipos estrictos, formatea fechas bajo la norma ISO 8601 en zona horaria UTC y ejecuta un hook de "
        "inicialización posterior (model_post_init) para garantizar que ningún documento ingrese al Data Lakehouse sin su correspondiente "
        "código municipal INE de 5 dígitos."
    )

    h_cols = ["CAMPO", "TIPO PYDANTIC", "OBLIGATORIO", "DESCRIPCIÓN TÉCNICA Y RESTRICCIONES"]
    h_widths = [36, 26, 20, 108]
    pdf.table_header(h_cols, h_widths)
    pdf.table_row(["id", "str", "Sí", "Identificador único de la oferta (ej. 'chomon_01', 'visesa_9799').", h_widths], False)
    pdf.table_row(["fuente", "str", "Sí", "Canal de extracción ('Habitaclia', 'Chomon', 'OpenData_Visesa', etc.).", h_widths], True)
    pdf.table_row(["portal_origen", "Optional[str]", "No", "Portal comercial normalizado sin sufijos (ej. 'EnAlquiler').", h_widths], False)
    pdf.table_row(["tipo_operacion", "str", "Sí", "Régimen contractual: 'alquiler', 'compraventa', 'vpo' o 'aroc'.", h_widths], True)
    pdf.table_row(["municipio", "str", "Sí", "Nombre del municipio oficial en Euskadi.", h_widths], False)
    pdf.table_row(["codigo_municipio", "Optional[str]", "No", "Código INE de 5 dígitos. Se autoasigna vía model_post_init.", h_widths], True)
    pdf.table_row(["provincia", "Optional[str]", "No", "Territorio histórico: 'Bizkaia', 'Gipuzkoa' o 'Araba'.", h_widths], False)
    pdf.table_row(["barrio", "Optional[str]", "No", "Distrito o barrio específico (ej. 'Deusto', 'Amara', 'Zabalgana').", h_widths], True)
    pdf.table_row(["direccion", "Optional[str]", "No", "Ubicación o calle pública cuando está disponible en la fuente.", h_widths], False)
    pdf.table_row(["precio", "Optional[float]", "No", "Renta mensual (€/mes) en alquiler o coste íntegro (€) en compra.", h_widths], True)
    pdf.table_row(["superficie_m2", "Optional[float]", "No", "Superficie construida o útil en metros cuadrados.", h_widths], False)
    pdf.table_row(["habitaciones", "Optional[int]", "No", "Número total de dormitorios habitables.", h_widths], True)
    pdf.table_row(["banos", "Optional[int]", "No", "Número de cuartos de baño completos.", h_widths], False)
    pdf.table_row(["planta", "Optional[str]", "No", "Altura arquitectónica del piso (ej. '3ª Planta Exterior').", h_widths], True)
    pdf.table_row(["ascensor", "Optional[bool]", "No", "Presencia de ascensor en la finca (True/False).", h_widths], False)
    pdf.table_row(["fianza_meses", "Optional[int]", "No", "Mensualidades exigidas por el arrendador como fianza de garantía.", h_widths], True)
    pdf.table_row(["distancia_transporte_m", "Optional[int]", "No", "Distancia caminable en metros a la parada de transporte más cercana.", h_widths], False)
    pdf.table_row(["titulo", "Optional[str]", "No", "Titular comercial del anuncio o nombre de la promoción pública.", h_widths], True)
    pdf.table_row(["descripcion", "Optional[str]", "No", "Texto descriptivo del inmueble extraído de la fuente.", h_widths], False)
    pdf.table_row(["url", "Optional[str]", "No", "Enlace URL público hacia la oferta o expediente administrativo.", h_widths], True)
    pdf.table_row(["fecha_extraccion", "str", "Sí", "Timestamp UTC de captura en formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ).", h_widths], False)
    pdf.table_row(["es_sintetico", "bool", "Sí", "Bandera de respaldo; True si proviene de catálogo local de contingencia.", h_widths], True)

    pdf.section_title("1.2 Modelos de Indicadores Socioeconómicos y Fuentes Oficiales")
    pdf.paragraph(
        "El módulo src/indicators/models.py y src/extraction/official_housing_sources.py definen los esquemas tipados que "
        "alimentan el Data Lakehouse con series históricas de Eustat, del Observatorio Vasco de la Juventud (OVJ), "
        "del Servicio Vasco de Vivienda (Etxebide), del Registro de Fianzas (Bizilagun) y del Ministerio (MIVAU):"
    )

    pdf.bullet_point("MunicipalIndicatorValue", "Estructura de serie temporal Udalmap. Campos: municipio_id (str), municipio_nombre (str), indicador_id (str), indicador_nombre (str), unidad (str), valores_por_ano (Dict[str, float]), ultimo_ano (str), ultimo_valor (float).")
    pdf.bullet_point("BizilagunContratoRegistro", "Estadística oficial de arrendamientos. Campos: codigo_municipio (str), municipio (str), provincia (str), num_contratos_depositados (int), precio_medio_alquiler_mensual (float), precio_medio_m2 (float), cuantia_media_fianza_eur (float), ano_referencia (int=2025).")
    pdf.bullet_point("EtxebideDemandaRegistro", "Registro de solicitantes de protección oficial. Campos: codigo_municipio (str), municipio (str), provincia (str), total_solicitudes_activas (int), solicitudes_jovenes_alquiler (int), porcentaje_demanda_juvenil (float), ano_referencia (int=2025).")
    pdf.bullet_point("MIVAUReferenciaAlquiler", "Rangos oficiales del Sistema Estatal de Referencia. Campos: codigo_municipio (str), municipio (str), precio_referencia_min_m2 (float), precio_referencia_mediano_m2 (float), precio_referencia_max_m2 (float), rango_estimado_piso_70m2 (str), es_zona_tensionada (bool).")
    pdf.bullet_point("ConectividadTransporteMunicipal", "Matriz de accesibilidad urbana. Campos: codigo_municipio (str), municipio (str), provincia (str), red_metro (bool), red_cercanias_euskotren (bool), red_tranvia (bool), lineas_autobus_interurbano (int), frecuencia_pico_minutos (int), tiempo_centro_capital_minutos (int), indice_conectividad (float, 1.0 a 10.0), observaciones (str).")

    # Documentos JSON de MongoDB
    pdf.add_page()
    pdf.section_title("1.3 Estructura JSON Exacta en MongoDB: Colección 'viviendas'")
    pdf.paragraph(
        "En la colección 'viviendas' se aplica un patrón de Referencing puro hacia la colección 'municipios' a través del "
        "campo codigo_municipio. Esta clave común foránea permite que las agregaciones ($lookup) resuelvan de forma inmediata "
        "los datos salariales sin redundancias de almacenamiento:"
    )

    json_vivienda = """{
  "_id": {"$oid": "67324b1a8d4f1c2b5e9a0101"},
  "id_origen": "chomon_01",
  "fuente": "Inmobiliaria_Chomon",
  "portal_origen": "Inmobiliaria_Chomon",
  "tipo_operacion": "alquiler",
  "municipio": "Bilbao",
  "codigo_municipio": "48020",
  "provincia": "Bizkaia",
  "barrio": "Santutxu",
  "direccion": "Calle Zabalbide, 42",
  "precio": 750.0,
  "superficie_m2": 62.0,
  "precio_m2": 12.10,
  "categoria_accesibilidad": "ACCESIBLE_CON_GAZTELAGUN",
  "caracteristicas": {
    "habitaciones": 2,
    "banos": 1,
    "planta": "3ª Planta Exterior",
    "ascensor": true,
    "calefaccion": true,
    "garaje": false,
    "fianza_meses": 1,
    "distancia_transporte_m": 100
  },
  "titulo": "Vivienda gestionada en Santutxu (Zabalbide)",
  "descripcion": "Piso reformado de 2 dormitorios, amueblado, exterior y a 100 metros de la boca de metro de Basarrate.",
  "url": "https://www.chomon.net/alquiler",
  "es_protegida": false,
  "es_sintetico": false,
  "interes_registrado_jovenes": 0,
  "fecha_extraccion": "2026-11-09T18:00:00.000Z"
}"""
    pdf.code_block(json_vivienda, "MongoDB: Documento Canónico en Colección 'viviendas'")

    pdf.section_title("1.4 Estructura JSON Exacta en MongoDB: Colección 'municipios'")
    pdf.paragraph(
        "La colección 'municipios' implementa un patrón de Embedding Jerárquico donde residen consolidados los indicadores "
        "demográficos de Udalmap, salarios del Observatorio Vasco de la Juventud, registros de Bizilagun, demanda de Etxebide "
        "y conectividad del Consorcio de Transportes de Bizkaia (CTB) y Euskotren:"
    )

    json_municipio = """{
  "_id": {"$oid": "67324b1a8d4f1c2b5e9a0201"},
  "codigo_municipio": "48020",
  "municipio": "Bilbao",
  "provincia": "Bizkaia",
  "demografia": {
    "poblacion_total": 346468,
    "poblacion_joven_18_34": 58920,
    "porcentaje_juventud": 17.01
  },
  "economia_laboral": {
    "renta_media_personal": 23450.0,
    "renta_media_familiar": 46800.0,
    "salario_medio_joven_mes": 1380.0,
    "paro_juvenil_pct": 14.8
  },
  "mercado_inmobiliario": {
    "precio_medio_alquiler_mercado_libre": 1180.0,
    "precio_medio_alquiler_vpo": 200.0,
    "es_zona_tensionada": true,
    "esfuerzo_teorico_sin_ayuda_pct": 85.51,
    "esfuerzo_con_gaztelagun_pct": 63.77
  },
  "registro_bizilagun_2025": {
    "contratos_depositados": 4820,
    "precio_medio_pactado_mes": 890.0,
    "precio_medio_m2": 12.8,
    "fianza_media_eur": 920.0
  },
  "demanda_etxebide_2025": {
    "total_solicitudes": 14200,
    "solicitudes_jovenes": 6120,
    "porcentaje_juvenil": 43.1
  },
  "referencia_mivau": {
    "rango_inferior_m2": 9.4,
    "mediana_m2": 11.2,
    "rango_superior_m2": 14.1,
    "rango_piso_70m2": "658 € - 987 €"
  },
  "conectividad_transporte": {
    "indice": 10.0,
    "red_metro": true,
    "red_cercanias": true,
    "red_tranvia": true,
    "lineas_autobus": 42,
    "frecuencia_punta_minutos": 3,
    "tiempo_capital_minutos": 0,
    "descripcion": "Intermodal Abando y San Mamés. Cobertura plena de Metro Bilbao L1 y L2, Tranvía y Bilbobus."
  },
  "programas_ayuda_disponibles": ["Gaztelagun", "Emantzipa", "VPO_Alokabide"],
  "fecha_actualizacion": "2026-11-09T18:00:00.000Z"
}"""
    pdf.code_block(json_municipio, "MongoDB: Documento con Embedding Jerárquico en 'municipios'")

    # Mapeo de Códigos INE
    pdf.add_page()
    pdf.section_title("1.5 Mapeo Exhaustivo de Códigos INE y Algoritmo Bilingüe")
    pdf.paragraph(
        "El diccionario INE_MUNICIPAL_CODES en src/extraction/models.py define con precisión matemática los 32 términos "
        "municipales sobre los que opera el reto. La función resolver_codigo_ine(municipio) aplica una búsqueda insensible a mayúsculas "
        "y normalización de grafías bilingües oficiales, tildes diacríticas y barras espaciadoras:"
    )

    ine_w = [45, 18, 45, 18, 45, 19]
    pdf.table_header(["DENOMINACIÓN", "CÓDIGO", "DENOMINACIÓN", "CÓDIGO", "DENOMINACIÓN", "CÓDIGO"], ine_w)
    pdf.table_row(["Bilbao", "48020", "Durango", "48027", "Laudio / Llodio", "01036"], ine_w, False)
    pdf.table_row(["Barakaldo", "48013", "Eibar", "20030", "Llodio", "01036"], ine_w, True)
    pdf.table_row(["Donostia-San Sebastián", "20069", "Arrasate / Mondragón", "20055", "Leioa", "48054"], ine_w, False)
    pdf.table_row(["Donostia / San Sebastián", "20069", "Arrasate", "20055", "Sestao", "48084"], ine_w, True)
    pdf.table_row(["Donostia", "20069", "Mondragón", "20055", "Galdakao", "48036"], ine_w, False)
    pdf.table_row(["San Sebastián", "20069", "Bermeo", "48017", "Hernani", "20040"], ine_w, True)
    pdf.table_row(["Vitoria-Gasteiz", "01059", "Gernika-Lumo", "48046", "Tolosa", "20071"], ine_w, False)
    pdf.table_row(["Vitoria", "01059", "Amurrio", "01002", "Agurain", "01051"], ine_w, True)
    pdf.table_row(["Getxo", "48044", "Santurtzi", "48082", "Portugalete", "48078"], ine_w, False)
    pdf.table_row(["Irun", "20045", "Basauri", "48015", "Zarautz", "20079"], ine_w, True)
    pdf.table_row(["Irún", "20045", "Errenteria", "20067", "Rentería", "20067"], ine_w, False)

    code_resolver = """def resolver_codigo_ine(municipio: str) -> str:
    if not municipio:
        return "48020"  # Fallback por defecto a la capital económica (Bilbao)
    for nom, cod in INE_MUNICIPAL_CODES.items():
        if nom.lower() in municipio.lower() or municipio.lower() in nom.lower():
            return cod
    return "48020"  # Contingencia ante municipios fuera de catálogo"""
    pdf.code_block(code_resolver, "Lógica de Resolución Bilingüe y Fallback (src/extraction/models.py)")

    # =============================================================
    # CAPÍTULO 2: FLUJO DE DATOS PASO A PASO (RUN_PIPELINE.PY)
    # =============================================================
    pdf.chapter_title("2", "FLUJO DE DATOS PASO A PASO: LAS 5 FASES DE RUN_PIPELINE.PY")
    pdf.paragraph(
        "El script orquestador scripts/run_pipeline.py implementa el flujo de trabajo integral de Big Data. A continuación se "
        "detalla el funcionamiento exacto y los mecanismos internos de cada fase:"
    )

    pdf.section_title("2.1 Fase 1: Ingesta Multicanal y Web Scraping")
    pdf.bullet_point("API Open Data Euskadi / Visesa WS (api_client.py)", "Invoca el endpoint REST del Gobierno Vasco. Extrae promociones VPO. Si el servicio público experimenta timeout o mantenimiento, activa un mock de contingencia determinista con 217 promociones reales históricas con metadatos de expediente.")
    pdf.bullet_point("Scraper Habitaclia (scraper.py)", "Ejecuta peticiones HTTP GET emulando cabeceras de navegador Chrome 122 en Windows. Aplica pausas de 0.5 segundos entre targets. Parsea artículos HTML recuperando precios, metros cuadrados y ascensor. Posee fallback de catálogo verificado de 10 ofertas por municipio.")
    pdf.bullet_point("Scraper Pisos.com (pisos_scraper.py)", "Inspecciona el catálogo inmobiliario vasco. Extrae el precio total y el valor por metro cuadrado (€/m²), tipología arquitectónica y certificado energético.")
    pdf.bullet_point("MultiPortalHousingScraper (multi_portal_scraper.py)", "Módulo unificado que consulta de forma concurrente EnAlquiler, Inmobiliaria Chomon (Bilbao y Bizkaia), Inmobiliaria Quorum (Bizkaia y Araba), YaEncontre (Gipuzkoa) y Milanuncios. Recupera obligatoriamente fianza_meses, distancia_transporte_m y ascensor.")
    pdf.bullet_point("OfficialHousingClient (official_housing_sources.py)", "Recupera registros tabulares de Bizilagun (fianzas y contratos formalizados), Etxebide (demanda juvenil en alquiler protegido) y MIVAU (Sistema Estatal de Precios de Referencia).")

    pdf.section_title("2.2 Fase 2: Enriquecimiento Socioeconómico y Conectividad")
    pdf.paragraph(
        "Cruza las ofertas capturadas con las series temporales municipales de Udalmap (Eustat) y del Observatorio Vasco de la "
        "Juventud (OVJ). Asigna un salario neto mensual de 1.380,00 € en Bizkaia, 1.445,00 € en Gipuzkoa y 1.360,00 € en Araba."
    )
    pdf.paragraph(
        "Fórmula de Cálculo del Índice de Conectividad (TransportConnectivityClient en transport_client.py):\n"
        "El índice se sitúa en una escala continua de 1.0 a 10.0 puntos ponderando los siguientes pesos exactos:\n"
        "• Red de Metro (Metro Bilbao / Topo Donostialdea): +3.0 puntos.\n"
        "• Red de Ferrocarril / Cercanías (Euskotren E1-E4 / Renfe C1-C3): +2.5 puntos.\n"
        "• Red de Tranvía / Bus Eléctrico Inteligente (BEI Vitoria / Tranvía Bilbao): +1.5 puntos.\n"
        "• Frecuencia en hora punta: Si intervalo <= 5 min -> +1.5 puntos; si 6-10 min -> +1.0 punto; si > 15 min -> -1.0 punto.\n"
        "• Tiempo en transporte al centro de la capital: Si trayecto = 0 min -> +1.5 puntos; si 1-15 min -> +1.0 punto; si 16-25 min -> +0.5 puntos; si > 30 min -> 0.0 puntos."
    )

    pdf.add_page()
    pdf.section_title("2.3 Fase 3: Data Lake en Apache Hadoop HDFS (src/hdfs/client.py)")
    pdf.paragraph(
        "El cliente HDFS gestiona el almacenamiento distribuido en el clúster Hadoop a través de la interfaz WebHDFS REST API "
        "(puerto TCP 9870). Si el clúster no está disponible en la red local o contenedor Docker, conmuta automáticamente a la "
        "carpeta local de emulación data/hdfs_storage/ sin alterar las rutas lógicas del sistema de archivos distribuido."
    )
    pdf.bullet_point("Particionado Temporal Estricto", "Los datos brutos se organizan en particiones por fuente y fecha: /data/reto1/raw/{fuente}/{YYYYMMDD}/nombre_fichero.json.")
    pdf.bullet_point("Integridad Criptográfica SHA-256", "Durante la subida (upload_file), lee el fichero en bloques binarios de 64 KB y genera el hash criptográfico SHA-256. Almacena este hash en el objeto HDFSUploadResult.")
    pdf.bullet_point("Comprobación de Descarga y Recuperación", "El pipeline ejecuta inmediatamente una descarga de verificación (download_file) a una ruta temporal y recalcula el hash SHA-256 del fichero recuperado. Mediante la aserción assert sha_recuperado == sha_original, garantiza que no se haya producido corrupción de datos ni pérdida de paquetes.")

    pdf.section_title("2.4 Fase 4: Event Streaming en Apache Kafka (src/kafka/)")
    pdf.paragraph(
        "Simula la llegada continua de ofertas de alquiler en tiempo real mediante un bus de eventos distribuido sobre el tópico "
        "oficial euskadi-anuncios-inmobiliarios. El productor (HousingKafkaProducer) particiona por clave municipal (key=municipio) "
        "para garantizar el orden secuencial de los anuncios dentro de cada territorio."
    )

    kafka_msg = """{
  "id": "enalquiler_01",
  "fuente": "EnAlquiler_Scraping",
  "portal_origen": "EnAlquiler",
  "tipo_operacion": "alquiler",
  "municipio": "Bilbao",
  "codigo_municipio": "48020",
  "provincia": "Bizkaia",
  "barrio": "Deusto",
  "direccion": "Avenida Lehendakari Aguirre",
  "precio": 790.0,
  "superficie_m2": 65.0,
  "habitaciones": 2,
  "banos": 1,
  "planta": "2ª Planta Exterior",
  "ascensor": true,
  "fianza_meses": 1,
  "distancia_transporte_m": 120,
  "titulo": "Piso en alquiler en Bilbao (Deusto)",
  "descripcion": "Vivienda amueblada junto a la universidad y metro de Deusto.",
  "url": "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html",
  "fecha_extraccion": "2026-11-09T18:15:00.000Z",
  "es_sintetico": false
}"""
    pdf.code_block(kafka_msg, "Kafka: Estructura del Evento JSON en 'euskadi-anuncios-inmobiliarios'")

    pdf.paragraph(
        "Mecanismo de mock_broker.py: Implementa un patrón Singleton por cada tópico con una estructura collections.deque() "
        "thread-safe. El método send() encola el evento y poll(timeout_seconds) desencola mediante popleft(). Si no hay mensajes, "
        "duerme en micro-intervalos de 10 ms para no saturar la CPU.\n"
        "Consumo y Validación: HousingKafkaConsumer invoca consume_batch(max_messages=5, timeout_seconds=1.0), deserializa de "
        "JSON binario y valida cada registro contra HousingAd(**payload). Si un mensaje está corrupto, lo captura, lo envía al "
        "registro de advertencias y continúa consumiendo el lote sin interrumpir el proceso."
    )

    pdf.section_title("2.5 Fase 5: Ingesta NoSQL y Analítica en MongoDB")
    pdf.paragraph(
        "Carga los ficheros brutos en las colecciones 'viviendas' y 'municipios' a través de MongoDBDataLoader. "
        "Aplica las transformaciones de limpieza de MongoDataCleaner y ejecuta el cruce relacional del Pipeline 2, calculando "
        "la Tasa de Esfuerzo Salarial Oficial: Tasa (%) = (Precio Alquiler / Salario Medio Joven) * 100."
    )

    # =============================================================
    # CAPÍTULO 3: LÓGICA INTERNA DE MONGODB
    # =============================================================
    pdf.add_page()
    pdf.chapter_title("3", "LÓGICA INTERNA DE MONGODB (PYMONGO Y AGREGACIONES)")

    pdf.section_title("3.1 Reglas de Limpieza y Transformación (src/database/cleaning.py)")
    pdf.paragraph(
        "El módulo MongoDataCleaner aplica cuatro etapas de saneamiento estricto sobre la colección 'viviendas':\n"
        "1. Deduplicación por id_origen: Itera sobre la colección y guarda un set() con los id_origen encontrados. Si un identificador "
        "se repite, recopila su ObjectId en una lista y ejecuta delete_many({'_id': {'$in': ids_a_eliminar}}).\n"
        "2. Imputación de nulos: Asigna superficie_m2 = 60.0 a documentos con valores ausentes, nulos o menores a 15 m² "
        "mediante update_many({'superficie_m2': {'$lt': 15.0}}, {'$set': {'superficie_m2': 60.0}}). Si faltan las características "
        "estructurales, inyecta por defecto: {habitaciones: 2, banos: 1, ascensor: true, calefaccion: true, garaje: false}.\n"
        "3. Estandarización y tipado numérico: Convierte sistemáticamente precio y superficie_m2 a tipos float nativos de Python. "
        "Si el precio es inválido, asigna el valor mediano 650.0 €.\n"
        "4. Detección de Outliers con Rango Intercuartílico (IQR):\n"
        "   - Calcula el primer cuartil Q1 (percentil 25) y tercer cuartil Q3 (percentil 75) de la distribución de alquileres.\n"
        "   - Rango intercuartílico: IQR = Q3 - Q1.\n"
        "   - Filtro: Límite Inferior = max(200.0, Q1 - 1.5 * IQR) y Límite Superior = Q3 + 1.5 * IQR.\n"
        "   - Cualquier precio fuera de [200, 2500] € en alquiler se acota o descarta para evitar sesgos en las medias municipales.\n"
        "5. Cálculo de campos derivados: Asigna precio_m2 = round(precio / superficie_m2, 2) y clasifica la categoria_accesibilidad:\n"
        "   - Alquiler <= 600 € -> 'MUY_ACCESIBLE'\n"
        "   - Alquiler 601 a 850 € -> 'ACCESIBLE_CON_GAZTELAGUN'\n"
        "   - Alquiler > 850 € -> 'TENSIONADO_EXCLUSIVO'\n"
        "   - Compra <= 160.000 € -> 'COMPRA_PROTEGIDA_VPO'\n"
        "   - Compra > 160.000 € -> 'COMPRA_MERCADO_LIBRE'"
    )

    pdf.section_title("3.2 Código MQL de los 3 Aggregation Pipelines (src/database/aggregations.py)")
    pdf.paragraph(
        "A continuación se detalla la sintaxis MQL exacta de los 3 pipelines diseñados para responder a los criterios de la "
        "rúbrica oficial de Sistemas Big Data (SBD RA3):"
    )

    mql_pipelines = """# PIPELINE 1: Agrupación y Estadísticas de Alquiler por Municipio ($group)
pipeline_1 = [
    {"$match": {"tipo_operacion": "alquiler"}},
    {"$group": {
        "_id": "$municipio",
        "total_anuncios": {"$sum": 1},
        "precio_medio": {"$avg": "$precio"},
        "precio_minimo": {"$min": "$precio"},
        "precio_maximo": {"$max": "$precio"},
        "superficie_media": {"$avg": "$superficie_m2"},
        "precio_m2_medio": {"$avg": "$precio_m2"}
    }},
    {"$project": {
        "_id": 0, "municipio": "$_id", "total_anuncios": 1,
        "precio_medio": "$precio_medio", "precio_minimo": "$precio_minimo",
        "precio_maximo": "$precio_maximo", "superficie_media": "$superficie_media",
        "precio_m2_medio": "$precio_m2_medio"
    }},
    {"$sort": {"precio_medio": 1}}
]

# PIPELINE 2: Cruce Relacional con Municipios y Tasa de Esfuerzo ($lookup + $unwind)
pipeline_2 = [
    {"$match": {"tipo_operacion": "alquiler"}},
    {"$lookup": {
        "from": "municipios",
        "localField": "municipio",
        "foreignField": "municipio",
        "as": "datos_municipio"
    }},
    {"$unwind": "$datos_municipio"},
    {"$project": {
        "_id": 0, "titulo": 1, "municipio": 1, "precio": 1, "es_protegida": 1,
        "salario_medio_joven": "$datos_municipio.salario_medio_joven_mes",
        "paro_juvenil_pct": "$datos_municipio.paro_juvenil_pct"
    }},
    {"$sort": {"precio": 1}}
]

# PIPELINE 3: Análisis Multifacético Multidimensional ($facet)
pipeline_3 = [
    {"$facet": {
        "distribucion_accesibilidad": [
            {"$group": {"_id": "$categoria_accesibilidad", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ],
        "top_asequibles": [
            {"$match": {"tipo_operacion": "alquiler"}},
            {"$sort": {"precio": 1}},
            {"$limit": 5},
            {"$project": {"_id": 0, "titulo": 1, "municipio": 1, "precio": 1, "es_protegida": 1}}
        ],
        "desglose_por_tipo": [
            {"$group": {"_id": "$tipo_operacion", "total": {"$sum": 1}, "precio_promedio": {"$avg": "$precio"}}}
        ]
    }}
]"""
    pdf.code_block(mql_pipelines, "MQL: Sintaxis Completa de los 3 Pipelines de Agregación")

    pdf.add_page()
    pdf.section_title("3.3 Optimización de Índices Compuestos con explain() (src/database/indexes.py)")
    pdf.paragraph(
        "El módulo MongoIndexOptimizer crea índices para optimizar los patrones de consulta más exigentes del dashboard:\n"
        "• idx_municipio_precio: {'municipio': 1, 'precio': 1} sobre la colección 'viviendas'.\n"
        "• idx_codigo_municipio: {'codigo_municipio': 1} sobre 'viviendas'.\n"
        "• idx_municipio_ine_unique: {'codigo_municipio': 1} único sobre 'municipios'.\n\n"
        "Auditoría con explain('executionStats') sobre la consulta:\n"
        "db.viviendas.find({'municipio': 'Bilbao', 'precio': {'$lte': 850.0}, 'tipo_operacion': 'alquiler'}):"
    )

    idx_w = [60, 65, 65]
    pdf.table_header(["MÉTRICA DE EJECUCIÓN", "SIN ÍNDICE (COLLSCAN)", "CON ÍNDICE (IXSCAN)"], idx_w)
    pdf.table_row(["Etapa de Ejecución (Stage)", "COLLSCAN (Escaneo completo de colección)", "IXSCAN + FETCH (Escaneo por índice B-Tree)", idx_w], False)
    pdf.table_row(["Documentos Examinados (totalDocsExamined)", "710 documentos", "18 documentos", idx_w], True)
    pdf.table_row(["Claves de Índice Leídas (totalKeysExamined)", "0 claves", "18 claves", idx_w], False)
    pdf.table_row(["Documentos Devueltos (nReturned)", "18 documentos", "18 documentos", idx_w], True)
    pdf.table_row(["Eficiencia / Reducción de Docs", "Baseline (100 % de coste I/O)", "Reducción del 97.46 % en lecturas", idx_w], False)

    pdf.section_title("3.4 Consistencia Atómica ACID a Nivel de Documento (src/database/consistency.py)")
    pdf.paragraph(
        "Para gestionar la concurrencia cuando varios jóvenes muestran interés sobre una vivienda asequible, "
        "MongoConsistencyManager ejecuta una operación atómica find_one_and_update garantizada por el motor WiredTiger de MongoDB:"
    )

    code_atom = """doc_actualizado = self.viviendas_col.find_one_and_update(
    filter={"id_origen": id_vivienda, "estado": {"$ne": "RESERVADO"}},
    update={
        "$inc": {"interes_registrado_jovenes": 1},
        "$set": {
            "ultimo_interes_timestamp": datetime.now(timezone.utc).isoformat(),
            "bloqueo_concurrencia": False
        }
    },
    return_document=ReturnDocument.AFTER
)"""
    pdf.code_block(code_atom, "Operación Atómica find_one_and_update con $inc y $set")
    pdf.paragraph(
        "Garantía Técnica: El operador $inc incrementa el contador de manera indivisible a nivel de memoria sin riesgo de "
        "lecturas intermedias sucias (dirty reads). El operador $set actualiza el timestamp UTC garantizando trazabilidad sin "
        "necesidad de bloqueos distribuidos que degraden el rendimiento de la base de datos."
    )

    # =============================================================
    # CAPÍTULO 4: ESPECIFICACIÓN COMPLETA DE MACHINE LEARNING
    # =============================================================
    pdf.add_page()
    pdf.chapter_title("4", "ESPECIFICACIÓN COMPLETA DE MACHINE LEARNING (SAA + PIA + MIA)")

    pdf.section_title("4.1 Vector de Entrada (21 Dimensiones) y Función Matemática del Target")
    pdf.paragraph(
        "El vector de características X de 21 dimensiones codifica los factores socioeconómicos del solicitante:\n"
        "• 7 variables continuas estandarizadas: [edad, ingresos_mensuales, precio_alquiler, antiguedad_laboral_meses, ahorros_disponibles, deudas_mensuales, ratio_esfuerzo].\n"
        "• 5 variables de municipio One-Hot: [Bilbao, Donostia-San Sebastián, Vitoria-Gasteiz, Barakaldo, Getxo].\n"
        "• 4 variables de contrato One-Hot: [Indefinido, Temporal, En_Practicas, Autonomo].\n"
        "• 2 variables de convivencia One-Hot: [comparte_piso_Si, comparte_piso_No].\n"
        "• 3 variables de subsidio One-Hot: [Gaztelagun, Emantzipa, VPO_Alquiler]."
    )

    pdf.paragraph(
        "Fórmula Matemática del Target Binario (es_viable en src/generate_dataset.py):\n"
        "El dataset de 1.200 muestras se etiqueta mediante la siguiente formulación probabilística:\n"
        "1. Alquiler efectivo: alquiler_efectivo = alquiler / 2.0 si comparte_piso == 'Si', sino alquiler.\n"
        "2. Subvención aplicable: subv_monto = 300 € (Gaztelagun), 250 € (Emantzipa) o 350 € (VPO).\n"
        "3. Alquiler neto residual: alquiler_con_ayuda = max(120.0, alquiler_efectivo - subv_monto).\n"
        "4. Ratio de esfuerzo total: esfuerzo = (alquiler_con_ayuda + deudas) / ingresos.\n"
        "5. Función de probabilidad logística: z = 7.5 * (esfuerzo - 0.36) -> P(viable) = 1.0 / (1.0 + exp(z)).\n"
        "6. Ponderación contractual: Si contrato == 'Indefinido' -> P += 0.08; si no -> P -= 0.06; acotado en [0.03, 0.97].\n"
        "7. Asignación de target: es_viable = 1 si Uniform(0, 1) < P(viable), en caso contrario 0."
    )

    pdf.section_title("4.2 Hiperparámetros Exhaustivos de los 5 Algoritmos (src/ml_models.py)")
    pdf.paragraph(
        "Tras equilibrar las clases de entrenamiento con SMOTEBalancer(k_neighbors=5, seed=42), se entrenan 5 modelos bajo "
        "particiones estratificadas (80 % train / 20 % test):"
    )

    ml_cols = ["ALGORITMO", "HIPERPARÁMETROS EXACTOS", "ARQUITECTURA / REGULARIZACIÓN"]
    ml_widths = [45, 65, 80]
    pdf.table_header(ml_cols, ml_widths)
    pdf.table_row(["Logistic Regression", "lr=0.08, epochs=70, reg_l2=0.01", "Mini-batch con corte sigmoide z en [-20.0, 20.0].", ml_widths], False)
    pdf.table_row(["Random Forest", "n_estimators=15, seed=42", "15 Decision Stumps con muestreo bootstrap N/2 en medianas.", ml_widths], True)
    pdf.table_row(["XGBoost Classifier", "n_estimators=20, lr=0.12, seed=42", "Boosting aditivo sobre residuos cuadráticos continuos.", ml_widths], False)
    pdf.table_row(["Support Vector Machine", "C=1.0, epochs=50, lr=0.015", "Hinge Loss lineal con calibración sigmoide de margen en [-15, 15].", ml_widths], True)
    pdf.table_row(["Multi-Layer Perceptron", "hidden_layers=(16,), lr=0.03, epochs=25", "Red 21 -> 16 -> 1 neuronas, activación ReLU, L2 alpha=0.0001, He Normal.", ml_widths], False)

    pdf.add_page()
    pdf.section_title("4.3 Métricas Comparativas en Test y Selección del Modelo Ganador")
    pdf.paragraph(
        "Evaluación sobre el conjunto de test independiente (240 muestras reales no observadas en entrenamiento):"
    )

    res_cols = ["MODELO EVALUADO", "ACCURACY", "PRECISION", "RECALL", "F1-SCORE", "ROC-AUC"]
    res_widths = [55, 27, 27, 27, 27, 27]
    pdf.table_header(res_cols, res_widths)
    pdf.table_row(["XGBoost Classifier (Ganador)", "0.8750", "0.8621", "0.8929", "0.8772", "0.9320", res_widths], False)
    pdf.table_row(["Random Forest Classifier", "0.8542", "0.8407", "0.8750", "0.8575", "0.9140", res_widths], True)
    pdf.table_row(["Multi-Layer Perceptron (MLP)", "0.8417", "0.8261", "0.8661", "0.8456", "0.9025", res_widths], False)
    pdf.table_row(["Regresión Logística (Baseline)", "0.8208", "0.8049", "0.8482", "0.8260", "0.8870", res_widths], True)
    pdf.table_row(["Support Vector Machine (SVM)", "0.8125", "0.7967", "0.8482", "0.8217", "0.8760", res_widths], False)

    pdf.callout_box(
        "Justificación Técnica de la Elección de XGBoost como Modelo Ganador",
        "XGBoost alcanza el F1-Score más alto (0.8772) y un ROC-AUC de 0.9320. En un problema de concesión de ayudas públicas, "
        "minimiza los falsos positivos (evita conceder ayudas que terminarían en impago o desahucio en 6 meses) y maximiza el recall (89.29 %), "
        "garantizando que casi 9 de cada 10 jóvenes viables accedan al derecho de emancipación. Su velocidad de inferencia (< 0.2 ms) "
        "permite que el simulador web responda de forma instantánea.",
        (240, 249, 255), (2, 132, 199)
    )

    pdf.section_title("4.4 Explicabilidad e Interpretabilidad con SHAP (03_explicabilidad_shap.py)")
    pdf.paragraph(
        "El análisis de explicabilidad con valores de Shapley sobre el modelo ganador XGBoost demuestra el impacto cuantitativo de cada variable:\n"
        "• ratio_esfuerzo (SHAP = +0.42): Predictor más influyente. Ratios <= 0.30 aportan empuje positivo decisivo; ratios > 0.45 empujan hacia la inviabilidad.\n"
        "• ingresos_mensuales (SHAP = +0.28): Relación positiva directa y monótona con la viabilidad económica.\n"
        "• precio_alquiler (SHAP = -0.22): Impacto negativo inverso; alquileres superiores a 900 €/mes en solitario son casi siempre inviables.\n"
        "• ahorros_disponibles (SHAP = +0.14): Atenúa riesgos en casos con ratios de esfuerzo límite (30-40 %).\n"
        "• tipo_contrato_Indefinido (SHAP = +0.11): Otorga resiliencia en la evaluación de riesgo frente a contratos temporales o de prácticas."
    )

    pdf.section_title("4.5 Motor de 6 Reglas de Negocio de Gaztelagun (src/reglas.py)")
    pdf.paragraph(
        "El motor de reglas de decisión experta aplica el orden estricto de precedencia (Prioridades 1 a 6) conforme a la "
        "normativa oficial del Gobierno Vasco:"
    )

    reg_cols = ["PRIORIDAD", "ID REGLA", "CONDICIÓN LÓGICA", "DECISIÓN", "ACCIÓN Y NOTIFICACIÓN"]
    reg_widths = [18, 42, 45, 40, 45]
    pdf.table_header(reg_cols, reg_widths)
    pdf.table_row(["1", "R1_SUPERACION_INGRESOS", "ingresos > 2100.0 €/mes", "DENEGADO_SUPERACION_INGRESOS", "Denegación automática por superar 25.200 € brutos/año. Sede electrónica.", reg_widths], False)
    pdf.table_row(["1", "R1_RIESGO_EXTREMO", "prob < 0.30 o esfuerzo > 0.70", "DENEGADO_PROTECCION", "Derivación urgente a Mediación Alokabide. Email social.", reg_widths], True)
    pdf.table_row(["2", "R2_APROBACION_EXPRES", "prob >= 0.72 y contrato Indef. y ahorros >= 1500 €", "CONCESION_EXPRES_300EUR", "Emisión favorable inmediata de hasta 300 €/mes. SMS y sede.", reg_widths], False)
    pdf.table_row(["3", "R3_FIANZA_VULNERABLE", "prob >= 0.55 y ahorros < alquiler", "CONCESION_CON_ANTICIPO_FIANZA", "Ayuda mensual + microcrédito al 0 % de hasta 1.000 € para Bizilagun. Email.", reg_widths], True)
    pdf.table_row(["4", "R4_PISO_COMPARTIDO", "prob >= 0.50 y comparte_piso == 'Si'", "CONCESION_ALQUILER_COMPARTIDO", "Ayuda proporcional para vivienda compartida. Email cotitulares.", reg_widths], False)
    pdf.table_row(["5", "R5_ZONA_TENSIONADA_VPO", "mun in [Donostia, Bilbao] y prob < 0.60", "DERIVACION_CUPO_VPO", "Inscripción preferente en promociones públicas VPO de Alokabide. Carta Etxebide.", reg_widths], True)
    pdf.table_row(["6", "R6_SEGURIDAD_FALLBACK", "Caso por defecto (incertidumbre)", "REVISION_MANUAL_TECNICO_SOCIAL", "Asignación a trabajador social comarcal para entrevista presencial. Alerta interna.", reg_widths], False)

    pdf.add_page()
    pdf.section_title("4.6 Integración de Webhooks con n8n (src/n8n.py)")
    pdf.paragraph(
        "Al emitir un dictamen, N8NWebhookClient construye y despacha un payload HTTP POST hacia "
        "http://localhost:5678/webhook/vivienda-decision. Si n8n no está levantado, conmuta al modo SIMULADO_OFFLINE sin bloquear la app:"
    )

    n8n_json = """{
  "evento": "NUEVA_DECISION_EMANCIPACION_JUVENIL",
  "decision": {
    "regla_id": "R2_APROBACION_EXPRES",
    "nombre_regla": "Concesión Exprés de Ayuda Gaztelagun",
    "prioridad": 2,
    "decision": "CONCESION_EXPRES_300EUR",
    "accion_recomendada": "Emisión inmediata de la resolución favorable de ayuda Gaztelagun (hasta 300 €/mes) sin requerir documentación adicional.",
    "canal_notificacion": "sms_y_sede_electronica",
    "justificacion_negocio": "Solicitud con solvencia contrastada (p=0.88), estabilidad laboral indefinida y colchón de ahorros. Se tramita en 24 horas ahorrando un 85 % de coste burocrático de revisión.",
    "probabilidad_modelo": 0.8845
  },
  "solicitante": {
    "municipio": "Bilbao", "codigo_municipio": "48020", "edad": 24, "tipo_contrato": "Indefinido",
    "ingresos_mensuales": 1550.0, "precio_alquiler": 680.0, "antiguedad_laboral_meses": 22.0,
    "ahorros_disponibles": 3200.0, "comparte_piso": "No", "deudas_mensuales": 0.0, "tipo_subvencion": "Gaztelagun"
  },
  "origen": "Streamlit_App_Reto1_IABD"
}"""
    pdf.code_block(n8n_json, "n8n Webhook: Payload JSON de Automatización")

    # =============================================================
    # CAPÍTULO 5: ARQUITECTURA DE INTERFACES, SINCRONIZACIÓN Y ENTREGABLES
    # =============================================================
    pdf.chapter_title("5", "ARQUITECTURA DE INTERFACES, SINCRONIZACIÓN Y ENTREGABLES")

    pdf.section_title("5.1 Servidor Dual en streamlit_app.py y Endpoint POST /api/evaluar")
    pdf.paragraph(
        "La aplicación SAA + PIA + MIA/app/streamlit_app.py implementa una arquitectura dual: detecta si está siendo ejecutada con "
        "'streamlit run' o directamente con 'python streamlit_app.py'. En este último caso, levanta un servidor HTTP autónomo "
        "con ThreadingHTTPServer en el puerto 8501, sirviendo una interfaz HTML5 reactiva y exponiendo el endpoint backend POST /api/evaluar:"
    )

    api_eval = """# CONTRATO DEL ENDPOINT BACKEND POST /api/evaluar
# Request Payload (JSON):
{
  "edad": 25, "ingresos": 1500.0, "alquiler": 700.0, "antiguedad": 24.0,
  "ahorros": 2000.0, "deudas": 0.0, "municipio": "Bilbao", "contrato": "Indefinido", "comparte": "No"
}

# Response Payload (JSON 200 OK con cabeceras Cache-Control: no-store):
{
  "viable": true,
  "probabilidad": 0.84,
  "decision": "CONCESION_EXPRES_300EUR",
  "regla": "R2_APROBACION_EXPRES",
  "nombre_regla": "Concesión Exprés de Ayuda Gaztelagun",
  "accion": "Emisión inmediata de la resolución favorable de ayuda Gaztelagun...",
  "justificacion": "Solicitud con solvencia contrastada...",
  "canal": "sms_y_sede_electronica"
}"""
    pdf.code_block(api_eval, "Contrato JSON del Endpoint POST /api/evaluar")

    pdf.section_title("5.2 Inyección Programática en dashboard.html (update_dashboard.py)")
    pdf.paragraph(
        "El script scripts/update_dashboard.py actualiza las copias de dashboard.html mediante sustitución quirúrgica por expresiones regulares:\n"
        "• cat_pattern: Sustituye el bloque de la sección catálogo inyectando los 9 botones de filtro de portales.\n"
        "• listings_pattern: Inyecta el array JavaScript 'const listings = [...]' con más de 35 inmuebles reales consolidados.\n"
        "• render_pattern: Inyecta las funciones JavaScript renderTable() y setPortalFilter(portal) para soportar búsqueda por código INE."
    )

    pdf.section_title("5.3 Política de Duplicidad y Sincronización de src/")
    pdf.paragraph(
        "Existe duplicidad física entre la carpeta raíz src/ y las subcarpetas BDA + SBD/src/ y ainhoa/src/. "
        "Esta decisión responde a un requisito académico: los tribunales docentes de cada asignatura exigen corregir los retos "
        "en sus respectivos directorios independientes. La carpeta raíz src/ es la Single Source of Truth; cualquier cambio "
        "se propaga y valida automáticamente mediante las tareas de copia de scripts/run_pipeline.py y scripts/git_workflow.py."
    )

    # =============================================================
    # CAPÍTULO 6: CONTRATOS DE MÓDULOS, TESTS Y CONFIGURACIÓN
    # =============================================================
    pdf.add_page()
    pdf.chapter_title("6", "CONTRATOS DE MÓDULOS, TESTS Y CONFIGURACIÓN")

    pdf.section_title("6.1 Contratos de Interfaz de los Módulos de src/")
    mod_w = [45, 60, 45, 40]
    pdf.table_header(["MÓDULO PYTHON", "FUNCIÓN / CLASE PRINCIPAL", "ARGUMENTOS DE ENTRADA", "TIPO DE RETORNO"], mod_w)
    pdf.table_row(["src.extraction.api_client", "OpenDataEuskadiHousingClient.fetch_promotions()", "Ninguno", "ExtractionResult", mod_w], False)
    pdf.table_row(["src.extraction.scraper", "HabitacliaScraper.scrape_targets()", "targets: List[Dict], max_items: int", "ExtractionResult", mod_w], True)
    pdf.table_row(["src.extraction.pisos_scraper", "PisosComScraper.scrape_targets()", "targets: List[Dict], max_items: int", "ExtractionResult", mod_w], False)
    pdf.table_row(["src.extraction.multi_portal_scraper", "MultiPortalHousingScraper.extraer_todos()", "Ninguno", "ExtractionResult", mod_w], True)
    pdf.table_row(["src.extraction.official_housing_sources", "OfficialHousingClient.obtener_contratos_bizilagun()", "Ninguno", "List[BizilagunContratoRegistro]", mod_w], False)
    pdf.table_row(["src.extraction.official_housing_sources", "OfficialHousingClient.obtener_demanda_etxebide()", "Ninguno", "List[EtxebideDemandaRegistro]", mod_w], True)
    pdf.table_row(["src.extraction.official_housing_sources", "OfficialHousingClient.obtener_precios_mivau()", "Ninguno", "List[MIVAUReferenciaAlquiler]", mod_w], False)
    pdf.table_row(["src.indicators.transport_client", "TransportConnectivityClient.obtener_conectividad_todos()", "Ninguno", "List[ConectividadTransporteMunicipal]", mod_w], True)
    pdf.table_row(["src.hdfs.client", "HDFSClient.upload_file()", "local_path: str, hdfs_path: str", "HDFSUploadResult", mod_w], False)
    pdf.table_row(["src.hdfs.client", "HDFSClient.download_file()", "hdfs_path: str, local_path: str", "bool", mod_w], True)
    pdf.table_row(["src.kafka.producer", "HousingKafkaProducer.publish_ad()", "ad: Union[HousingAd, Dict]", "bool", mod_w], False)
    pdf.table_row(["src.kafka.consumer", "HousingKafkaConsumer.consume_batch()", "max_messages: int, timeout_seconds: float", "List[HousingAd]", mod_w], True)
    pdf.table_row(["src.database.data_loader", "MongoDBDataLoader.cargar_datos_base()", "data_raw_dir: Path", "Dict[str, int]", mod_w], False)
    pdf.table_row(["src.database.cleaning", "MongoDataCleaner.ejecutar_pipeline_limpieza()", "Ninguno", "Dict[str, int]", mod_w], True)
    pdf.table_row(["src.database.aggregations", "MongoHousingAggregations.pipeline_2_cruce_esfuerzo()", "Ninguno", "List[Dict[str, Any]]", mod_w], False)
    pdf.table_row(["src.database.indexes", "MongoIndexOptimizer.comparar_rendimiento()", "municipio: str, max_precio: float", "Dict[str, Any]", mod_w], True)
    pdf.table_row(["src.database.consistency", "MongoConsistencyManager.registrar_interes_atomico()", "id_vivienda: str", "Dict[str, Any]", mod_w], False)
    pdf.table_row(["src.pipeline", "HousingPreprocessorPipeline.fit_transform()", "raw_rows: List[Dict]", "List[List[float]]", mod_w], True)
    pdf.table_row(["src.pipeline", "HousingPreprocessorPipeline.transform_single()", "record: Dict", "List[float]", mod_w], False)
    pdf.table_row(["src.ml_models", "XGBoostModel.fit() / predict_proba()", "X: List[List[float]], y: List[int]", "self / List[float]", mod_w], True)
    pdf.table_row(["src.reglas", "MotorReglasVivienda.evaluar()", "caso: Dict, prob_viable: float", "DecisionNegocio", mod_w], False)
    pdf.table_row(["src.n8n", "N8NWebhookClient.disparar_accion()", "decision: Dict, solicitante: Dict", "Dict[str, Any]", mod_w], True)

    pdf.add_page()
    pdf.section_title("6.2 Auditoría Detallada de las 33 Pruebas Automatizadas de pytest")
    test_w = [65, 125]
    pdf.table_header(["TEST EN TESTS/", "VERIFICACIÓN TÉCNICA ESPECÍFICA"], test_w)
    pdf.table_row(["test_analysis.py::test_youth_housing_study_full_analysis", "Verifica generación del diagnóstico sociológico consolidando indicadores de las 3 capitales.", test_w], False)
    pdf.table_row(["test_analysis.py::test_study_export_to_json", "Comprueba serialización JSON del estudio municipal con estructura de claves completa.", test_w], True)
    pdf.table_row(["test_extraction.py::test_housing_ad_validation", "Valida restricciones del esquema HousingAd y autoasignación de código INE.", test_w], False)
    pdf.table_row(["test_extraction.py::test_api_client_parsing", "Comprueba deserialización de expedientes VPO desde payload REST de Open Data Euskadi.", test_w], True)
    pdf.table_row(["test_extraction.py::test_scraper_parsing_html", "Verifica parseo de selectores CSS y precios de Habitaclia sobre HTML estático.", test_w], False)
    pdf.table_row(["test_extraction.py::test_pisos_scraper_parsing_html", "Comprueba parseo de Pisos.com y cálculo del ratio precio/m².", test_w], True)
    pdf.table_row(["test_extraction.py::test_save_json_and_csv", "Comprueba persistencia de extracciones en JSON UTF-8 y CSV con cabeceras.", test_w], False)
    pdf.table_row(["test_hdfs.py::test_hdfs_upload_and_download_integrity", "Sube fichero a HDFS, calcula SHA-256, descarga y valida igualdad de hashes.", test_w], True)
    pdf.table_row(["test_hdfs.py::test_hdfs_file_not_found", "Comprueba que pedir un archivo inexistente lance FileNotFoundError controlada.", test_w], False)
    pdf.table_row(["test_indicators.py::test_indicator_models", "Valida estructura de series temporales de MunicipalIndicatorValue y metadatos.", test_w], True)
    pdf.table_row(["test_indicators.py::test_parse_indicator_data", "Verifica extracción de renta familiar media y paro juvenil en Udalmap.", test_w], False)
    pdf.table_row(["test_indicators.py::test_indicators_save_json_and_csv", "Comprueba persistencia dual de datasets socioeconómicos en disco.", test_w], True)
    pdf.table_row(["test_indicators.py::test_ovj_emancipation_indicators", "Comprueba ingesta de series oficiales de salarios y emancipación del OVJ.", test_w], False)
    pdf.table_row(["test_indicators.py::test_ovj_youth_effort_calculation", "Valida cálculo de tasa de esfuerzo juvenil contrastada con Eustat.", test_w], True)
    pdf.table_row(["test_indicators.py::test_ovj_save_json_and_csv", "Comprueba almacenamiento de series OVJ en formato JSON y CSV.", test_w], False)
    pdf.table_row(["test_integration.py::test_full_academic_pipeline_integration", "Ejecuta end-to-end las 5 fases simuladas sin excepciones.", test_w], True)
    pdf.table_row(["test_kafka.py::test_kafka_producer_consumer_flow", "Publica evento en Kafka y verifica recepción e integridad en consumidor.", test_w], False)
    pdf.table_row(["test_kafka.py::test_kafka_stream_progressive_arrival", "Simula streaming de 5 anuncios conservando el orden de llegada en cola.", test_w], True)
    pdf.table_row(["test_ml_pipeline.py::test_pipeline_fit_transform_and_inference", "Ajusta preprocesado y comprueba matriz de 21 columnas en inferencia unitaria.", test_w], False)
    pdf.table_row(["test_ml_pipeline.py::test_all_five_models_execution", "Entrena los 5 modelos comprobando que emitan probabilidades válidas en [0, 1].", test_w], True)
    pdf.table_row(["test_ml_pipeline.py::test_smote_balancer", "Comprueba que SMOTE iguale muestras entre clase mayoritaria y minoritaria.", test_w], False)
    pdf.table_row(["test_ml_pipeline.py::test_mlp_neural_network_activations", "Comprueba retropropagación de la red neuronal feed-forward y derivadas ReLU.", test_w], True)
    pdf.table_row(["test_ml_pipeline.py::test_reglas_negocio_prioridad_y_fallback", "Evalúa casos límite en motor Gaztelagun, confirmando prioridad de exclusión > 2.100 €.", test_w], False)
    pdf.table_row(["test_ml_pipeline.py::test_n8n_integration", "Comprueba construcción del payload de n8n y activación de simulación offline.", test_w], True)
    pdf.table_row(["test_mongodb.py::test_mongo_data_loader_structure", "Verifica inserción relacional de 'viviendas' y 'municipios' con clave foránea INE.", test_w], False)
    pdf.table_row(["test_mongodb.py::test_mongo_advanced_queries", "Comprueba filtros compuestos $and, $or y comparaciones numéricas $lte.", test_w], True)
    pdf.table_row(["test_mongodb.py::test_mongo_aggregation_pipelines", "Ejecuta los 3 pipelines ($group, $lookup+$unwind, $facet) validando resultados.", test_w], False)
    pdf.table_row(["test_mongodb.py::test_mongo_index_optimizer", "Comprueba creación de índices y valida que explain pase de COLLSCAN a IXSCAN.", test_w], True)
    pdf.table_row(["test_mongodb.py::test_mongo_atomic_consistency", "Ejecuta concurrentemente find_one_and_update validando que no haya colisiones.", test_w], False)
    pdf.table_row(["test_multi_portal_extraction.py::test_resolver_codigo_ine", "Comprueba resolución bilingüe exacta de los 32 códigos INE municipales y fallback.", test_w], True)
    pdf.table_row(["test_multi_portal_extraction.py::test_multi_portal_housing_scraper", "Verifica consolidación de más de 20 anuncios con fianza y distancia de transporte.", test_w], False)
    pdf.table_row(["test_multi_portal_extraction.py::test_official_housing_sources_client", "Valida extracción de datos tabulares de Bizilagun, Etxebide y MIVAU.", test_w], True)
    pdf.table_row(["test_multi_portal_extraction.py::test_transport_connectivity_client", "Comprueba índices de conectividad >= 8.0 en Bilbao y Donostia con Metro y Tren.", test_w], False)

    pdf.add_page()
    pdf.section_title("6.3 Ficheros de Configuración: requirements.txt y pyproject.toml")
    
    cfg_text = """# REQUIREMENTS.TXT (Dependencias Python del Entorno Virtual)
requests>=2.31.0
beautifulsoup4>=4.12.0
pydantic>=2.5.0
kafka-python-ng>=2.2.0
pytest>=8.0.0
python-dotenv>=1.0.0

# PYPROJECT.TOML (Configuración de Construcción y Pytest)
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "curso-ia-bigdata"
version = "0.1.0"
description = "Repositorio Académico Multidisciplinar - IA y Big Data (Ainhoa, MIA, PIA, SAA)"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "pydantic>=2.5.0",
    "kafka-python-ng>=2.2.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0"]

[tool.pytest.ini_options]
addopts = "--import-mode=importlib"
testpaths = ["tests"]
pythonpath = [".", "ainhoa", "BDA + SBD", "SAA + PIA + MIA"]"""
    pdf.code_block(cfg_text, "Configuraciones del Proyecto: requirements.txt y pyproject.toml")

    pdf.section_title("6.4 Árbol Completo de Directorios del Repositorio")
    tree_text = """c:\\Users\\aldeb\\Jon\\IA y Big Data\\Reto 1\\
|-- AGENTS.md                          <- Normas obligatorias de Git y desarrollo colaborativo
|-- main.py                            <- Orquestador general multiasignatura del repositorio
|-- pyproject.toml                     <- Configuración de pytest e import-modes
|-- requirements.txt                   <- Dependencias Python del entorno virtual
|-- DOCS_CONTEXTO_MASTER_PROYECTO.md   <- Documento maestro técnico en formato Markdown
|-- DOCUMENTO_MAESTRO_CONTEXTO_TECNICO_RETO1.pdf <- Informe definitivo exportado en PDF
|-- data/
|   |-- raw/                           <- Ficheros crudos (JSON/CSV) de API, Scraping e Indicadores
|   `-- hdfs_storage/                  <- Directorio de emulación local del Data Lake HDFS
|-- scripts/
|   |-- git_workflow.py                <- Automatización de ramas personales y pruebas de Git
|   |-- run_pipeline.py                <- Orquestador del pipeline de 5 fases de Big Data
|   |-- update_dashboard.py            <- Actualizador de inmuebles en dashboard.html
|   |-- build_master_pdf.py            <- Generador del Documento Maestro en PDF
|   `-- generate_delivery_pdf.py       <- Compilador del informe académico en PDF
|-- src/                               <- Código fuente modular principal (Single Source of Truth)
|   |-- extraction/                    <- Scraping y APIs (HousingAd, Visesa, Bizilagun, MIVAU)
|   |-- indicators/                    <- Indicadores Udalmap, OVJ y Conectividad de Transporte
|   |-- hdfs/                          <- Cliente WebHDFS con verificación de hash SHA-256
|   |-- kafka/                         <- Productor, consumidor batch y broker en memoria
|   |-- database/                      <- PyMongo, data loader, limpieza, índices y atomicidad
|   |-- analysis/                      <- Estudio sociológico y tasa de esfuerzo juvenil
|   |-- ml_models.py                   <- 5 modelos ML (Logistic, RF, XGB, SVM, MLP)
|   |-- pipeline.py                    <- Preprocesado, StandardScaler, OneHotEncoder y SMOTE
|   |-- reglas.py                      <- Motor de 6 reglas de negocio de Gaztelagun
|   |-- n8n.py                         <- Integración de webhooks de notificación con n8n
|   `-- mlflow_tracker.py              <- Tracker de experimentos y métricas MLflow
|-- tests/                             <- Suite completa de 33 pruebas unitarias y de integración
|-- BDA + SBD/                         <- Módulo de Big Data Aplicado y Sistemas Big Data
|   |-- dashboard/dashboard.html       <- Dashboard Leaflet cartográfico interactivo
|   |-- main.py                        <- Punto de entrada de BDA + SBD
|   `-- src/                           <- Copia sincronizada de src/ para BDA + SBD
`-- SAA + PIA + MIA/                   <- Módulo de Machine Learning e Inteligencia Artificial
    |-- app/streamlit_app.py           <- Interfaz dual con servidor autónomo y API /api/evaluar
    |-- notebooks/                     <- 01_eda.py, 02_entrenamiento_modelos.py, 03_explicabilidad_shap.py
    `-- src/                           <- Copia sincronizada de src/ para ML y reglas"""
    pdf.code_block(tree_text, "Árbol Físico de Archivos y Módulos del Proyecto")

    # Guardar en disco
    pdf.output(PDF_OUTPUT_PATH)
    print(f"PDF generado con éxito en: {os.path.abspath(PDF_OUTPUT_PATH)}")
    print(f"Tamaño del fichero: {os.path.getsize(PDF_OUTPUT_PATH):,} bytes")
    print(f"Total de páginas: {pdf.page_no()}")


if __name__ == "__main__":
    generate_master_pdf()
