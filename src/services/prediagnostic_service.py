"""
Prediction service with MongoDB operations for HU: Get case by prediagnostico_id.
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from PIL import Image
from ..inference.predictor import PneumoniaPredictor
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
        


    async def create_prediagnostico(self, datos: Dict[str, Any]):
        """
        Create and save a new prediagnostico in MongoDB.
        """

        await mongo_manager.prediagnosticos_collection.insert_one(datos)

    async def process_image_ai(self, datos: Dict[str, Any]):
        """
        Process the image by using the ai model
        """

        ruta_imagen = Path(datos["radiografia_ruta"])
        img = Image.open(ruta_imagen).convert("RGB")
        predictor_ia = PneumoniaPredictor()

        resultado = predictor_ia.predict_from_image(img)

        datos_actualizados = {
            "resultado_modelo": {
                "probabilidad_neumonia": resultado["confidence"],
                "etiqueta": resultado["predicted_class"],
            },
            "estado": "procesado",
            "fecha_procesamiento": datetime.utcnow(),
        }

        await mongo_manager.prediagnosticos_collection.update_one(
            {"prediagnostico_id": datos["prediagnostico_id"]},
            {"$set": datos_actualizados}
        )


    async def update_prediagnostic_status(self, prediagnostico_id: str, new_status: str) -> bool:
        """
        Update the status of a prediagnostico case.
        
        This method implements the HU5 requirement:
        "Actualizar en la colección de prediagnósticos el estado del caso 
        de 'Procesado' a 'Validado'"
        
        Args:
            prediagnostico_id: ID of the prediagnostico to update
            new_status: New status to set (typically "Validado" for HU5)
            
        Returns:
            bool: True if updated successfully, False if not found or failed
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Update the estado field in prediagnosticos collection
            update_result = await mongo_manager.prediagnosticos_collection.update_one(
                {"prediagnostico_id": prediagnostico_id},
                {
                    "$set": {
                        "estado": new_status,
                        "fecha_actualizacion": datetime.now().isoformat()  # Track when status changed
                    }
                }
            )
            
            if update_result.matched_count > 0:
                if update_result.modified_count > 0:
                    logger.info(f"Successfully updated prediagnostico {prediagnostico_id} status to {new_status}")
                    return True
                else:
                    logger.warning(f"Prediagnostico {prediagnostico_id} was found but not modified (already {new_status}?)")
                    return True
            else:
                logger.warning(f"Prediagnostico {prediagnostico_id} not found for status update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating prediagnostico {prediagnostico_id} status to {new_status}: {e}")
            raise


    async def verify_connection(self) -> Dict[str, Any]:
        """
        Verify MongoDB connection and collection accessibility.
        
        Returns:
            dict: Connection status information
        """
        try:
            # Test prediagnosticos collection
            pred_count = await mongo_manager.prediagnosticos_collection.count_documents({})
            
            # Test diagnosticos collection
            diag_count = await mongo_manager.diagnosticos_collection.count_documents({})
            
            return {
                "status": "connected",
                "prediagnosticos_count": pred_count,
                "diagnosticos_count": diag_count,
                "collections_accessible": True
            }
            
        except Exception as e:
            logger.error(f"MongoDB connection verification failed: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "collections_accessible": False
            }

# Global prediagnostic service instance
prediagnostic_service = PrediagnosticService()