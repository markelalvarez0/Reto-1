"""Limpieza con PyMongo sin sustituir medidas ausentes por valores inventados."""
from typing import Any, Dict
from src.extraction.normalization import numero_observado, booleano_observado


class MongoDataCleaner:
    """Deduplica por fuente/id, conserva nulos y calcula derivados en MongoDB."""
    def __init__(self, db):
        self.db = db
        self.viviendas_col = db['viviendas']
        self.municipios_col = db['municipios']

    def ejecutar_pipeline_limpieza(self) -> Dict[str, int]:
        return {
            'duplicados_eliminados': self._eliminar_duplicados(),
            'nulos_tratados': self._tratar_nulos_y_ausentes(),
            'tipos_corregidos': self._estandarizar_tipos_y_formatos(),
            'campos_calculados': self._calcular_campos_derivados(),
        }

    def _eliminar_duplicados(self) -> int:
        pipeline = [
            {'$match': {'id_origen': {'$nin': [None, '']}}},
            {'$sort': {'fecha_extraccion': -1, '_id': -1}},
            {'$group': {'_id': {'fuente': '$fuente', 'id': '$id_origen'}, 'ids': {'$push': '$_id'}, 'n': {'$sum': 1}}},
            {'$match': {'n': {'$gt': 1}}},
        ]
        ids = [oid for group in self.viviendas_col.aggregate(pipeline) for oid in group['ids'][1:]]
        return self.viviendas_col.delete_many({'_id': {'$in': ids}}).deleted_count if ids else 0

    def _tratar_nulos_y_ausentes(self) -> int:
        total = 0
        for field in ('precio', 'superficie_m2'):
            total += self.viviendas_col.update_many({field: {'$exists': False}}, {'$set': {field: None}}).modified_count
        total += self.viviendas_col.update_many(
            {'$or': [{'caracteristicas': {'$exists': False}}, {'caracteristicas': None}]},
            {'$set': {'caracteristicas': {}}},
        ).modified_count
        for field in ('habitaciones', 'banos', 'ascensor', 'fianza_meses', 'distancia_transporte_m'):
            name = f'caracteristicas.{field}'
            total += self.viviendas_col.update_many({name: {'$exists': False}}, {'$set': {name: None}}).modified_count
        return total

    def _estandarizar_tipos_y_formatos(self) -> int:
        total = 0
        for doc in self.viviendas_col.find():
            values = {
                'precio': numero_observado(doc.get('precio'), minimo=0.01),
                'superficie_m2': numero_observado(doc.get('superficie_m2'), minimo=0.01),
                'tipo_operacion': str(doc.get('tipo_operacion') or 'desconocida').strip().lower(),
            }
            changes = {key: value for key, value in values.items() if doc.get(key) != value or type(doc.get(key)) is not type(value)}
            original = dict(doc.get('valores_originales') or {})
            for key in ('precio', 'superficie_m2'):
                if key in changes and key not in original:
                    original[key] = doc.get(key)
            chars = doc.get('caracteristicas') or {}
            for name in ('habitaciones', 'banos', 'fianza_meses', 'distancia_transporte_m'):
                val = numero_observado(chars.get(name), entero=True)
                if chars.get(name) != val:
                    changes[f'caracteristicas.{name}'] = val
            elev = booleano_observado(chars.get('ascensor'))
            if chars.get('ascensor') != elev:
                changes['caracteristicas.ascensor'] = elev
            if changes:
                changes['valores_originales'] = original
                total += self.viviendas_col.update_one({'_id': doc['_id']}, {'$set': changes}).modified_count
        return total

    def _calcular_campos_derivados(self) -> int:
        """La aritmetica se ejecuta en MongoDB; las categorias no son derechos a ayudas."""
        valid = {'$and': [{'$isNumber': '$precio'}, {'$gt': ['$precio', 0]}, {'$isNumber': '$superficie_m2'}, {'$gt': ['$superficie_m2', 0]}]}
        price_valid = {'$and': [{'$isNumber': '$precio'}, {'$gt': ['$precio', 0]}]}
        updates = [{'$set': {
            'precio_m2': {'$cond': [valid, {'$divide': ['$precio', '$superficie_m2']}, None]},
            'calidad.precio_valido': price_valid,
            'calidad.superficie_valida': {'$and': [{'$isNumber': '$superficie_m2'}, {'$gt': ['$superficie_m2', 0]}]},
            'categoria_accesibilidad': {'$switch': {
                'branches': [
                    {'case': {'$eq': [price_valid, False]}, 'then': 'SIN_DATOS'},
                    {'case': {'$ne': ['$tipo_operacion', 'alquiler']}, 'then': 'NO_COMPARABLE_CON_ALQUILER'},
                    {'case': {'$lte': ['$precio', 600]}, 'then': 'ALQUILER_HASTA_600'},
                    {'case': {'$lte': ['$precio', 850]}, 'then': 'ALQUILER_600_850'},
                ], 'default': 'ALQUILER_MAS_850',
            }},
        }}]
        return self.viviendas_col.update_many({}, updates).modified_count
