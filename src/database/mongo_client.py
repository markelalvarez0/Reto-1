"""
Cliente y gestor de conexión para MongoDB (PyMongo) con soporte de emulación local.
"""
import os
import logging
from typing import Tuple, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "reto1_vivienda"

class MongoDBManager:
    """Gestiona la conexión a MongoDB con fallback automático a emulación local."""
    
    def __init__(self, uri: str = DEFAULT_MONGO_URI, db_name: str = DATABASE_NAME, force_mock: bool = False):
        self.uri = uri
        self.db_name = db_name
        self.is_mock = force_mock
        self.client, self.db = self._connect(force_mock)

    def _connect(self, force_mock: bool) -> Tuple[Any, Any]:
        if force_mock:
            logger.info("Iniciando MongoDB en modo emulación (mongomock)...")
            import mongomock
            client = mongomock.MongoClient()
            return client, client[self.db_name]
            
        try:
            client = MongoClient(self.uri, serverSelectionTimeoutMS=1500)
            client.admin.command('ping')
            logger.info(f"Conexión exitosa a MongoDB real en {self.uri}")
            return client, client[self.db_name]
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            logger.warning(f"No se pudo conectar a MongoDB en {self.uri} ({e}). Activando emulación local (mongomock).")
            self.is_mock = True
            import mongomock
            client = mongomock.MongoClient()
            return client, client[self.db_name]

    def get_collection(self, name: str):
        return self.db[name]

    def drop_database(self):
        self.client.drop_database(self.db_name)

    def close(self):
        self.client.close()
