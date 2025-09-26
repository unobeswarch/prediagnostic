"""
API routes for prediagnostic case retrieval (HU: Doctor case review).
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from ..services.prediagnostic_service import prediagnostic_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/case/{prediagnostico_id}", response_model=Dict[str, Any])
async def get_case(prediagnostico_id: str):
    """
    Get case details for doctor review (for BusinessLogic).
    
    This endpoint is used by BusinessLogic to retrieve a specific case
    that a doctor wants to review, including X-ray image and AI results.
    
    Args:
        prediagnostico_id: The ID of the prediagnostico case
        
    Returns:
        dict: Case details including X-ray URL and AI model results
    """
    try:
        # Get prediagnostico from MongoDB
        case = await prediagnostic_service.get_prediagnostico(prediagnostico_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with prediagnostico_id '{prediagnostico_id}' not found"
            )
        
        logger.info(f"Retrieved case {prediagnostico_id} for doctor review")
        
        # Convert datetime objects to strings for JSON serialization
        if "fecha_procesamiento" in case and case["fecha_procesamiento"]:
            case["fecha_procesamiento"] = case["fecha_procesamiento"].isoformat()
        if "fecha_subida" in case and case["fecha_subida"]:
            case["fecha_subida"] = case["fecha_subida"].isoformat()
            
        return JSONResponse(
            content=case,
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving case {prediagnostico_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving case"
        )

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint for prediagnostic service.
    
    Returns:
        dict: Service health status.
    """
    try:
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "prediagnostic",
                "message": "Service is running and ready to serve case requests"
            },
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "prediagnostic", 
                "message": str(e)
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/info", response_model=Dict[str, Any])
async def service_info():
    """
    Get prediagnostic service information.
    
    Returns:
        dict: Service metadata for the HU implementation.
    """
    return {
        "service_name": "Prediagnostic Case Service", 
        "version": "1.0.0",
        "description": "Service to retrieve prediagnostic cases for doctor review",
        "hu_implementation": "Doctor case selection by prediagnostico_id",
        "endpoints": {
            "/case/{prediagnostico_id}": "GET - Get case details for doctor review",
            "/health": "GET - Service health check",
            "/info": "GET - Service information"
        },
        "integration": "Designed for BusinessLogic orchestration"
    }