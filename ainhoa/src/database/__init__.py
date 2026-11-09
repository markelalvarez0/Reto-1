"""
Módulo de Base de Datos MongoDB y PyMongo para el Reto Intermodular SBD + BDA.
"""
from .mongo_client import MongoDBManager
from .data_loader import MongoDBDataLoader
from .cleaning import MongoDataCleaner
from .queries import MongoHousingQueries
from .aggregations import MongoHousingAggregations
from .indexes import MongoIndexOptimizer
from .consistency import MongoConsistencyManager

__all__ = [
    "MongoDBManager",
    "MongoDBDataLoader",
    "MongoDataCleaner",
    "MongoHousingQueries",
    "MongoHousingAggregations",
    "MongoIndexOptimizer",
    "MongoConsistencyManager"
]
