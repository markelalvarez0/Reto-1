"""Conexion MongoDB explicita: el modo real falla si el servicio no responde."""
import os
from pymongo import MongoClient

DATABASE_NAME = 'reto1_vivienda'


class MongoDBManager:
    def __init__(self, uri=None, db_name=DATABASE_NAME, force_mock=False):
        self.uri = uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.db_name = db_name
        self.is_mock = bool(force_mock)
        if self.is_mock:
            import mongomock
            self.client = mongomock.MongoClient()
        else:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            try:
                self.client.admin.command('ping')
            except Exception:
                self.client.close()
                raise
        self.db = self.client[db_name]

    def get_collection(self, name):
        return self.db[name]

    def drop_database(self):
        self.client.drop_database(self.db_name)

    def close(self):
        self.client.close()
