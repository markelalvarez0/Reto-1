"""
Módulo de limpieza, validación y transformación de datos en MongoDB usando PyMongo.
Cumple con la rúbrica SBD RA1:
- Tratamiento de nulos / valores ausentes
- Eliminación de registros duplicados
- Conversión y normalización de tipos/formatos
- Enriquecimiento con campos calculados (precio_m2, categoria_accesibilidad)
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MongoDataCleaner:
    """Ejecuta transformaciones y limpieza automatizada sobre colecciones MongoDB."""

    def __init__(self, db):
        self.db = db
        self.viviendas_col = db["viviendas"]
        self.municipios_col = db["municipios"]

    def ejecutar_pipeline_limpieza(self) -> Dict[str, int]:
        """Ejecuta todas las operaciones de limpieza y retorna resumen de impacto."""
        logger.info("Iniciando pipeline de limpieza y transformación en MongoDB...")
        
        # Operación 1: Eliminación de duplicados
        duplicados_eliminados = self._eliminar_duplicados()
        
        # Operación 2: Tratamiento de nulos / campos ausentes
        nulos_tratados = self._tratar_nulos_y_ausentes()
        
        # Operación 3: Estandarización y casteo de tipos
        tipos_corregidos = self._estandarizar_tipos_y_formatos()
        
        # Operación 4: Cálculo de campos derivados (precio_m2 y categoría accesibilidad)
        campos_calculados = self._calcular_campos_derivados()

        resumen = {
            "duplicados_eliminados": duplicados_eliminados,
            "nulos_tratados": nulos_tratados,
            "tipos_corregidos": tipos_corregidos,
            "campos_calculados": campos_calculados
        }
        logger.info(f"Limpieza finalizada con éxito: {resumen}")
        return resumen

    def _eliminar_duplicados(self) -> int:
        """Elimina documentos que tengan el mismo id_origen conservando el primero."""
        seen = set()
        ids_a_eliminar = []
        for doc in self.viviendas_col.find({}, {"_id": 1, "id_origen": 1}):
            id_orig = doc.get("id_origen")
            if not id_orig:
                continue
            if id_orig in seen:
                ids_a_eliminar.append(doc["_id"])
            else:
                seen.add(id_orig)

        if ids_a_eliminar:
            res = self.viviendas_col.delete_many({"_id": {"$in": ids_a_eliminar}})
            return res.deleted_count
        return 0

    def _tratar_nulos_y_ausentes(self) -> int:
        """Asigna valores coherentes por defecto a registros con datos incompletos."""
        # 1. Asignar superficie por defecto si es nula o menor a 15 m2
        res1 = self.viviendas_col.update_many(
            {"$or": [{"superficie_m2": {"$exists": False}}, {"superficie_m2": None}, {"superficie_m2": {"$lt": 15.0}}]},
            {"$set": {"superficie_m2": 60.0}}
        )

        # 2. Asignar características estructurales si faltan
        res2 = self.viviendas_col.update_many(
            {"caracteristicas": {"$exists": False}},
            {"$set": {
                "caracteristicas": {
                    "habitaciones": 2,
                    "banos": 1,
                    "ascensor": True,
                    "calefaccion": True,
                    "garaje": False
                }
            }}
        )
        return res1.modified_count + res2.modified_count

    def _estandarizar_tipos_y_formatos(self) -> int:
        """Asegura que precios y superficies sean numéricos de punto flotante."""
        count = 0
        for doc in self.viviendas_col.find():
            precio_raw = doc.get("precio", 0.0)
            sup_raw = doc.get("superficie_m2", 50.0)
            tipo_raw = doc.get("tipo_operacion", "alquiler")
            
            try:
                precio_clean = float(precio_raw)
            except (ValueError, TypeError):
                precio_clean = 650.0
                
            try:
                sup_clean = float(sup_raw)
            except (ValueError, TypeError):
                sup_clean = 60.0

            tipo_clean = str(tipo_raw).strip().lower()

            self.viviendas_col.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "precio": precio_clean,
                    "superficie_m2": sup_clean,
                    "tipo_operacion": tipo_clean
                }}
            )
            count += 1
        return count

    def _calcular_campos_derivados(self) -> int:
        """Calcula el precio/m2 y clasifica la vivienda según esfuerzo juvenil."""
        count = 0
        for doc in self.viviendas_col.find():
            precio = float(doc.get("precio", 0.0))
            sup = float(doc.get("superficie_m2", 1.0))
            if sup <= 0:
                sup = 1.0
            precio_m2 = round(precio / sup, 2)

            tipo_op = doc.get("tipo_operacion", "alquiler")
            if tipo_op == "alquiler":
                if precio <= 600.0:
                    categoria = "MUY_ACCESIBLE"
                elif precio <= 850.0:
                    categoria = "ACCESIBLE_CON_GAZTELAGUN"
                else:
                    categoria = "TENSIONADO_EXCLUSIVO"
            else:
                if precio <= 160000.0:
                    categoria = "COMPRA_PROTEGIDA_VPO"
                else:
                    categoria = "COMPRA_MERCADO_LIBRE"

            self.viviendas_col.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "precio_m2": precio_m2,
                    "categoria_accesibilidad": categoria
                }}
            )
            count += 1
        return count
