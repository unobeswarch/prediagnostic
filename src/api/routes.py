"""
API routes for pneumonia prediction service.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from ..inference.predictor import PneumoniaPredictor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize predictor (this should be done once at startup)
predictor = None

def initialize_predictor():
    """Initialize the predictor instance."""
    global predictor
    try:
        predictor = PneumoniaPredictor()
        logger.info("Predictor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")
        raise


@router.post("/predict", response_model=Dict[str, Any])
async def predict_pneumonia(file: UploadFile = File(...)):
    """
    Predict pneumonia from uploaded image.
    
    Args:
        file: Uploaded image file.
        
    Returns:
        dict: Prediction results including class, confidence, and metadata.
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service not available"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (e.g., max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB"
        )
    
    try:
        # Make prediction
        result = predictor.predict_from_file(file_content, filename=file.filename)
        
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK
        )
        
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during prediction"
        )


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status.
    """
    try:
        if predictor is None:
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "message": "Predictor not initialized"
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        health_info = predictor.health_check()
        status_code = status.HTTP_200_OK if health_info["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=health_info,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "message": str(e)
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/info", response_model=Dict[str, Any])
async def service_info():
    """
    Get service information.
    
    Returns:
        dict: Service metadata and capabilities.
    """
    return {
        "service_name": "Pneumonia Prediction Service",
        "version": "1.0.0",
        "description": "AI-powered pneumonia detection from chest X-ray images",
        "endpoints": {
            "/predict": "POST - Upload image for pneumonia prediction",
            "/health": "GET - Service health check",
            "/info": "GET - Service information"
        },
        "supported_formats": ["JPEG", "PNG", "BMP", "TIFF"],
        "max_file_size": "10MB",
        "model_classes": ["No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"] if predictor else []
    }