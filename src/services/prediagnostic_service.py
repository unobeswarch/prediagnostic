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

        result = await mongo_manager.prediagnosticos_collection.insert_one(datos)

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

# Global prediagnostic service instance
prediagnostic_service = PrediagnosticService()