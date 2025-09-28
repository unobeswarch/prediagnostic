"""
Prediction service with MongoDB operations for HU: Get case by prediagnostico_id.
"""
import logging
from typing import Optional, Dict, Any

from ..database.mongodb import mongo_manager

logger = logging.getLogger(__name__)


class PrediagnosticService:
    """Service for handling prediagnosticos CRUD operations."""
    
    async def get_prediagnostico(self, prediagnostico_id: str) -> Optional[Dict[str, Any]]:
        """
        Get prediagnostico by ID for doctor review.
        
        This is the main functionality for the HU:
        "Como doctor, quiero seleccionar un caso de cualquier paciente 
        para ver su radiografía y resultados del modelo"
        
        Args:
            prediagnostico_id: Prediagnostico ID sent by BusinessLogic
            
        Returns:
            dict: Prediagnostico data with radiografía URL and AI results, or None if not found
        """
        try:
            result = await mongo_manager.prediagnosticos_collection.find_one(
                {"prediagnostico_id": prediagnostico_id}
            )
            
            if result:
                # Convert ObjectId to string if present
                if "_id" in result:
                    result["_id"] = str(result["_id"])
                logger.info(f"Retrieved prediagnostico: {prediagnostico_id} for doctor review")
                return result
            
            logger.warning(f"Prediagnostico not found: {prediagnostico_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving prediagnostico {prediagnostico_id}: {e}")
            raise

    async def get_diagnostic_by_case_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get diagnostic information by case ID for HU7 (Patient radiograph detail view).
        
        This method retrieves medical diagnostic information for cases that have been
        reviewed by doctors. Used in HU7 to show doctor's validation of AI results.
        
        Args:
            case_id: Case/prediagnostico ID to get diagnostic information for
            
        Returns:
            dict: Diagnostic data with doctor approval, comments, review date, or None if not found
        """
        try:
            result = await mongo_manager.diagnosticos_collection.find_one(
                {"case_id": case_id}
            )
            
            if result:
                # Convert ObjectId to string if present
                if "_id" in result:
                    result["_id"] = str(result["_id"])
                logger.info(f"Retrieved diagnostic for case: {case_id}")
                return result
            
            logger.debug(f"Diagnostic not found for case: {case_id} (normal for unreviewed cases)")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving diagnostic for case {case_id}: {e}")
            raise


# Global prediagnostic service instance
prediagnostic_service = PrediagnosticService()