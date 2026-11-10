"""Indicadores calculados mediante MongoDB. Datos demo excluidos por defecto."""
from typing import Any, Dict, List


class MongoHousingAggregations:
    def __init__(self, db, include_synthetic: bool = False):
        self.db = db
        self.viviendas = db['viviendas']
        self.municipios = db['municipios']
        self.include_synthetic = include_synthetic

    def _filtro(self, alquiler=True):
        result = {'precio': {'$type': 'number', '$gt': 0}, 'codigo_municipio': {'$type': 'string', '$regex': r'^[0-9]{5}$'}}
        if alquiler:
            result['tipo_operacion'] = 'alquiler'
        if not self.include_synthetic:
            result['es_sintetico'] = False
        return result

    def pipeline_1_estadisticas_alquiler_por_municipio(self) -> List[Dict[str, Any]]:
        """Une variantes bilingues mediante INE; separa compra de alquiler."""
        return list(self.viviendas.aggregate([
            {'$match': self._filtro()},
            {'$group': {'_id': '$codigo_municipio', 'municipio': {'$first': '$municipio'},
                        'total_anuncios': {'$sum': 1}, 'precio_medio': {'$avg': '$precio'},
                        'precio_minimo': {'$min': '$precio'}, 'precio_maximo': {'$max': '$precio'},
                        'superficie_media': {'$avg': '$superficie_m2'}, 'precio_m2_medio': {'$avg': '$precio_m2'}}},
            {'$project': {'_id': 0, 'codigo_municipio': '$_id', 'municipio': 1, 'total_anuncios': 1,
                          'precio_medio': 1, 'precio_minimo': 1, 'precio_maximo': 1, 'superficie_media': 1, 'precio_m2_medio': 1}},
            {'$sort': {'precio_medio': 1, 'codigo_municipio': 1}},
        ]))

    def _pipeline_esfuerzo(self):
        pipeline = [
            {'$match': self._filtro()},
            {'$lookup': {'from': 'municipios', 'localField': 'codigo_municipio', 'foreignField': 'codigo_municipio', 'as': 'datos_municipio'}},
            {'$unwind': {'path': '$datos_municipio', 'preserveNullAndEmptyArrays': True}},
        ]
        salary = {'$ifNull': ['$datos_municipio.economia_laboral.salario_medio_joven_mes', '$datos_municipio.salario_medio_joven_mes']}
        if not self.include_synthetic:
            salary = {'$cond': [{'$eq': ['$datos_municipio.es_sintetico', False]}, salary, None]}
        pipeline += [
            {'$set': {'salario_medio_joven': salary}},
            {'$set': {'tasa_esfuerzo_pct': {'$cond': [
                {'$and': [{'$isNumber': '$salario_medio_joven'}, {'$gt': ['$salario_medio_joven', 0]}]},
                {'$multiply': [{'$divide': ['$precio', '$salario_medio_joven']}, 100]}, None,
            ]}}},
            {'$project': {'_id': 0, 'id_origen': 1, 'fuente': 1, 'titulo': 1, 'municipio': 1, 'codigo_municipio': 1,
                          'precio': 1, 'precio_m2': 1, 'es_protegida': 1, 'salario_medio_joven': 1, 'tasa_esfuerzo_pct': 1,
                          'paro_juvenil_pct': {'$ifNull': ['$datos_municipio.economia_laboral.paro_juvenil_pct', '$datos_municipio.paro_juvenil_pct']},
                          'procedencia_salario': '$datos_municipio.procedencia', 'url': 1, 'es_sintetico': 1}},
        ]
        return pipeline

    def pipeline_2_cruce_esfuerzo_salarial(self) -> List[Dict[str, Any]]:
        """Cruce por INE. Sin salario medido no existe porcentaje de esfuerzo."""
        return list(self.viviendas.aggregate(self._pipeline_esfuerzo() + [{'$sort': {'precio': 1, 'id_origen': 1}}]))

    def pipeline_2_cruce_esfuerzo(self):
        """Alias documentado en el Documento Maestro."""
        return self.pipeline_2_cruce_esfuerzo_salarial()

    def pipeline_3_facet_distribucion_y_top(self) -> Dict[str, Any]:
        """Tres conjuntos visualizables; medias separadas por tipo de operacion."""
        rows = list(self.viviendas.aggregate([
            {'$match': self._filtro(alquiler=False)},
            {'$facet': {
                'distribucion_accesibilidad': [
                    {'$match': {'tipo_operacion': 'alquiler'}},
                    {'$group': {'_id': '$categoria_accesibilidad', 'total': {'$sum': 1}}}, {'$sort': {'_id': 1}},
                ],
                'top_asequibles': [
                    {'$match': {'tipo_operacion': 'alquiler'}}, {'$sort': {'precio': 1, 'id_origen': 1}}, {'$limit': 5},
                    {'$project': {'_id': 0, 'titulo': 1, 'municipio': 1, 'codigo_municipio': 1, 'precio': 1, 'es_protegida': 1}},
                ],
                'desglose_por_tipo': [{'$group': {'_id': '$tipo_operacion', 'total': {'$sum': 1}, 'precio_promedio': {'$avg': '$precio'}}}],
            }},
        ]))
        return rows[0] if rows else {}

    def indicadores_municipales(self):
        """Cinco indicadores y cobertura: oferta, precio, EUR/m2, esfuerzo y asequibilidad."""
        valid = {'$isNumber': '$tasa_esfuerzo_pct'}
        pipeline = self._pipeline_esfuerzo() + [
            {'$group': {'_id': '$codigo_municipio', 'municipio': {'$first': '$municipio'},
                        'total_anuncios': {'$sum': 1}, 'precio_medio': {'$avg': '$precio'},
                        'precio_m2_medio': {'$avg': '$precio_m2'}, 'esfuerzo_medio_pct': {'$avg': '$tasa_esfuerzo_pct'},
                        'anuncios_con_salario': {'$sum': {'$cond': [valid, 1, 0]}},
                        'asequibles_30_pct': {'$sum': {'$cond': [{'$and': [valid, {'$lte': ['$tasa_esfuerzo_pct', 30]}]}, 1, 0]}}}},
            {'$project': {'_id': 0, 'codigo_municipio': '$_id', 'municipio': 1, 'total_anuncios': 1, 'precio_medio': 1,
                          'precio_m2_medio': 1, 'esfuerzo_medio_pct': 1, 'anuncios_con_salario': 1,
                          'porcentaje_asequibles': {'$cond': [{'$gt': ['$anuncios_con_salario', 0]},
                              {'$multiply': [{'$divide': ['$asequibles_30_pct', '$anuncios_con_salario']}, 100]}, None]}}},
            {'$sort': {'codigo_municipio': 1}},
        ]
        return list(self.viviendas.aggregate(pipeline))
