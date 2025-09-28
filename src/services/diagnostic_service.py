"""
Diagnostic service for HU5: Save and retrieve doctor diagnostics.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..database.mongodb import mongo_manager

logger = logging.getLogger(__name__)

class DiagnosticService:
    """Service for handling diagnostics CRUD operations."""

    async def save_diagnostic(self, diagnostic_document: Dict[str, Any]) -> bool:
        """
        Save a doctor's diagnostic review to MongoDB diagnosticos collection.
        """
        try:
            result = await mongo_manager.diagnosticos_collection.insert_one(diagnostic_document)
            if result.inserted_id:
                logger.info(f"Successfully saved diagnostic: {diagnostic_document['_id']}")
                return True
            else:
                logger.error(f"Failed to save diagnostic: {diagnostic_document['_id']}")
                return False
        except Exception as e:
            logger.error(f"Error saving diagnostic {diagnostic_document.get('_id', 'unknown')}: {e}")
            raise

    async def get_diagnostic_by_prediagnostico(self, prediagnostico_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a diagnostic document by prediagnostico_id.
        """
        try:
            result = await mongo_manager.diagnosticos_collection.find_one(
                {"prediagnostico_id": prediagnostico_id}
            )
            if result:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
                logger.info(f"Retrieved diagnostic for prediagnostico: {prediagnostico_id}")
                return result
            logger.info(f"No diagnostic found for prediagnostico: {prediagnostico_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving diagnostic for prediagnostico {prediagnostico_id}: {e}")
            raise

# Global diagnostic service instance

diagnostic_service = DiagnosticService()
