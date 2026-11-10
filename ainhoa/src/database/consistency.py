"""Actualizacion atomica de un documento; no equivale a una transaccion global."""
from datetime import datetime, timezone
from pymongo import ReturnDocument


class MongoConsistencyManager:
    def __init__(self, db):
        self.db = db
        self.viviendas = db['viviendas']
        self.municipios = db['municipios']

    def registrar_interes_joven_atomico(self, vivienda_id_origen, fuente=None):
        query = {'id_origen': vivienda_id_origen}
        if fuente is not None:
            query['fuente'] = fuente
        elif self.viviendas.count_documents(query, limit=2) > 1:
            raise ValueError('Identificador ambiguo: indique tambien la fuente')
        timestamp = datetime.now(timezone.utc)
        result = self.viviendas.find_one_and_update(query, {
            '$inc': {'solicitudes_interes_joven': 1},
            '$set': {'ultima_consulta_timestamp': timestamp},
        }, return_document=ReturnDocument.AFTER)
        return {'id_origen': vivienda_id_origen,
                'solicitudes_interes_joven': result['solicitudes_interes_joven'] if result else None,
                'atomicidad_garantizada': result is not None,
                'modo': 'simulado' if type(self.db).__module__.startswith('mongomock') else 'mongodb'}

    registrar_interes_atomico = registrar_interes_joven_atomico

    def obtener_justificacion_tecnica(self):
        return {
            'decision_arquitectura': 'Incremento atomico de un unico documento',
            'justificacion': 'MongoDB garantiza la actualizacion at\u00f3mica de un documento. El contador y la fecha se actualizan juntos; esta operacion no necesita modificar municipios. Si otra operacion exigiera cambios inseparables entre colecciones, habria que evaluar una transaccion multidocumento.',
            'mecanismo_utilizado': 'find_one_and_update con $inc, $set y ReturnDocument.AFTER',
        }
