"""Medicion con explain real: nunca fabrica tiempos ni elimina indices ajenos."""
from typing import Any, Dict


class MongoIndexOptimizer:
    def __init__(self, db, is_mock: bool = False):
        self.db = db
        self.viviendas = db['viviendas']
        self.is_mock = is_mock or type(db).__module__.startswith('mongomock')

    def crear_indices(self) -> Dict[str, str]:
        return {
            'indice_simple': self.viviendas.create_index([('codigo_municipio', 1)], name='idx_codigo_municipio'),
            'indice_compuesto': self.viviendas.create_index([('municipio', 1), ('tipo_operacion', 1), ('precio', 1)], name='idx_municipio_operacion_precio'),
            'identidad_anuncio': self.viviendas.create_index([('fuente', 1), ('id_origen', 1)], name='idx_fuente_id', unique=True, partialFilterExpression={'fuente': {'$type': 'string'}, 'id_origen': {'$type': 'string'}}),
            'identidad_municipio': self.db['municipios'].create_index('codigo_municipio', name='idx_ine_unique', unique=True),
        }

    @staticmethod
    def _stages(node):
        found = []
        if isinstance(node, dict):
            if 'stage' in node:
                found.append(node['stage'])
            for value in node.values():
                found.extend(MongoIndexOptimizer._stages(value))
        elif isinstance(node, list):
            for value in node:
                found.extend(MongoIndexOptimizer._stages(value))
        return found

    def comparar_rendimiento_consulta(self, municipio='Bilbao', precio_max=850.0):
        if self.is_mock:
            return {'estado': 'NO_DISPONIBLE_EN_MOCK', 'sin_indice': None, 'con_indice': None,
                    'motivo': 'mongomock no ejecuta planes ni mide rendimiento de MongoDB.'}
        self.crear_indices()
        query = {'municipio': municipio, 'tipo_operacion': 'alquiler', 'precio': {'$gt': 0, '$lte': precio_max}}
        result = {'estado': 'MEDIDO_EN_MONGODB', 'consulta': query}
        for name, hint in [('sin_indice', {'$natural': 1}), ('con_indice', 'idx_municipio_operacion_precio')]:
            explain = self.db.command('explain', {'find': self.viviendas.name, 'filter': query, 'hint': hint}, verbosity='executionStats')
            stats = explain['executionStats']
            stages = self._stages(explain.get('queryPlanner', {}).get('winningPlan', {}))
            result[name] = {
                'stage': 'IXSCAN' if 'IXSCAN' in stages else 'COLLSCAN' if 'COLLSCAN' in stages else '/'.join(stages),
                'stages': stages, 'totalDocsExamined': stats['totalDocsExamined'],
                'totalKeysExamined': stats['totalKeysExamined'], 'nReturned': stats['nReturned'],
                'executionTimeMillis': stats['executionTimeMillis'], 'explain': explain,
            }
        before, after = result['sin_indice']['totalDocsExamined'], result['con_indice']['totalDocsExamined']
        result['reduccion_documentos_examinados_pct'] = 100 * (before - after) / before if before else None
        return result

    comparar_rendimiento = comparar_rendimiento_consulta
