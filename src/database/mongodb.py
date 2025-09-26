"""
MongoDB connection and database operations.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from ..config.settings import (
    MONGODB_URL,
    DATABASE_NAME,
    PREDIAGNOSTICOS_COLLECTION,
    DIAGNOSTICOS_COLLECTION,
    MONGODB_CONNECTION_TIMEOUT,
    MONGODB_SERVER_SELECTION_TIMEOUT
)

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB connection manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.prediagnosticos_collection = None
        self.diagnosticos_collection = None
    
    async def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(
                MONGODB_URL,
                connectTimeoutMS=MONGODB_CONNECTION_TIMEOUT,
                serverSelectionTimeoutMS=MONGODB_SERVER_SELECTION_TIMEOUT
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.database = self.client[DATABASE_NAME]
            self.prediagnosticos_collection = self.database[PREDIAGNOSTICOS_COLLECTION]
            self.diagnosticos_collection = self.database[DIAGNOSTICOS_COLLECTION]
            
            logger.info(f"Connected to MongoDB: {DATABASE_NAME} with collections: {PREDIAGNOSTICOS_COLLECTION}, {DIAGNOSTICOS_COLLECTION}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> bool:
        """Check MongoDB connection health."""
        try:
            if not self.client:
                return False
            
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False


# Global MongoDB manager instance
mongo_manager = MongoDBManager()