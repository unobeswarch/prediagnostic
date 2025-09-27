"""
Service for retrieving prediagnostic cases by user_id.
"""
import logging
from typing import List, Dict, Any

from ..database.mongodb import mongo_manager

logger = logging.getLogger(__name__)

class PrediagnosticCasesService:
    """Service for retrieving prediagnostic cases by user_id."""

    async def get_cases_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all prediagnostic cases for a given user_id.
        Returns a list of cases with selected fields.
        """
        try:
            cursor = mongo_manager.prediagnosticos_collection.find({"user_id": user_id})
            cases = []
            async for doc in cursor:
                case = {
                    "prediagnostico_id": doc.get("prediagnostico_id"),
                    "paciente_nombre": doc.get("paciente_nombre", ""),
                    "fecha": (
                        doc.get("fecha_procesamiento", doc.get("fecha_subida")).isoformat()
                        if doc.get("fecha_procesamiento") or doc.get("fecha_subida") else ""
                    ),
                    "estado": doc.get("estado", ""),
                    "diagnostico_ia": doc.get("resultado_modelo", {}).get("etiqueta", ""),
                    "probabilidad": doc.get("resultado_modelo", {}).get("probabilidad_neumonia", None)
                }
                cases.append(case)
            logger.info(f"Retrieved {len(cases)} cases for user_id: {user_id}")
            return cases
        except Exception as e:
            logger.error(f"Error retrieving cases for user_id {user_id}: {e}")
            raise

# Global instance
prediagnostic_cases_service = PrediagnosticCasesService()