"""
API routes for prediagnostic case retrieval (HU: Doctor case review).
"""
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form, Body
from fastapi.responses import JSONResponse
import shutil
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import uuid
from pydantic import BaseModel, Field
import random
import string


from ..services.prediagnostic_service import prediagnostic_service
from ..services.diagnostic_service import diagnostic_service
from ..services.prediagnostic_cases_service import prediagnostic_cases_service

# Pydantic model for diagnostic request
class DiagnosticRequest(BaseModel):
    """Request model for doctor diagnostic submission"""
    aprobacion: bool = Field(..., description="Doctor's approval of AI prediction (True/False)")
    comentario: str = Field(..., min_length=10, description="Doctor's medical comments (minimum 10 characters)")

# Logger setup
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

STORAGE_DIR = Path("storage/radiografias")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/diagnostic/{prediagnostic_id}", response_model=Dict[str, Any])
async def save_diagnostic(prediagnostic_id: str, diagnostic: DiagnosticRequest = Body(...)):
    """
    Save a doctor's diagnostic review for a prediagnostic case (HU5).
    
    This endpoint allows a doctor to approve/reject the AI model prediction
    and provide medical comments for a specific prediagnostic case.
    
    Args:
        prediagnostic_id (str): The ID of the prediagnostic case to review
        diagnostic (DiagnosticRequest): Request body containing doctor's decision and comments
    
    Returns:
        JSONResponse: Created diagnostic record with ID, approval, comments, and timestamp
        
    Raises:
        HTTPException 404: If prediagnostic case not found
        HTTPException 500: If internal server error occurs
    """
    try:
        logger.info(f"Processing diagnostic submission for prediagnostic_id: {prediagnostic_id}")
        
        # Step 1: Verify that the prediagnostic case exists and is in "procesado" state
        prediagnostic_case = await prediagnostic_service.get_prediagnostico(prediagnostic_id)
        if not prediagnostic_case:
            logger.warning(f"Prediagnostic case not found: {prediagnostic_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediagnostic case with id '{prediagnostic_id}' not found"
            )
        
        # Step 2: Verify case is in correct state for diagnostic review
        current_state = prediagnostic_case.get("estado", "")
        if current_state != "procesado":
            logger.warning(f"Invalid case state for diagnostic: {current_state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Case must be in 'procesado' state for diagnostic review. Current state: '{current_state}'"
            )

        # Step 3: Generate unique diagnostic ID
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        diagnostic_id = f"D{datetime.now().strftime('%Y%m%d%H%M%S')}_{random_suffix}"
        
        # Step 4: Create diagnostic document according to HU5 specifications
        diagnostic_document = {
            "_id": diagnostic_id,
            "prediagnostico_id": prediagnostic_id,  # Using Spanish naming as per requirements
            "aprobacion": diagnostic.aprobacion,     # Boolean: True for approval, False for rejection
            "comentarios": diagnostic.comentario,    # Doctor's medical comments
            "fecha_revision": datetime.now().isoformat()  # ISO timestamp of review
        }
        
        logger.info(f"Creating diagnostic document: {diagnostic_id}")

        # Step 5: Save diagnostic to MongoDB diagnosticos collection
        await diagnostic_service.save_diagnostic(diagnostic_document)
        
        # Step 6: Update prediagnostic case status from "procesado" to "Validado"
        await prediagnostic_service.update_prediagnostic_status(prediagnostic_id, "Validado")
        
        logger.info(f"Successfully saved diagnostic {diagnostic_id} and updated case status to Validado")

        # Step 7: Return success response to BusinessLogic
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "_id": diagnostic_id,
                "prediagnostico_id": prediagnostic_id,
                "aprobacion": diagnostic.aprobacion,
                "comentarios": diagnostic.comentario,
                "fecha_revision": diagnostic_document["fecha_revision"],
                "message": "Diagnostic saved successfully"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (404, 400, etc.)
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving diagnostic for {prediagnostic_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while saving diagnostic"
        )

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


@router.get("/diagnostic/{case_id}", response_model=Dict[str, Any])
async def get_diagnostic(case_id: str):
    """
    Get diagnostic details for a specific case (HU7 - Patient radiograph detail view).
    
    This endpoint retrieves medical diagnostic information for cases that have been
    reviewed by doctors. Only validated cases will have diagnostic information.
    
    Args:
        case_id: The ID of the case to get diagnostic information for
        
    Returns:
        dict: Diagnostic details including doctor approval, comments, and review date
        
    Raises:
        404: If no diagnostic information exists for the case (normal for unreviewed cases)
        500: Internal server error
    """
    try:
        # Get diagnostic from MongoDB using prediagnostico_service
        diagnostic = await prediagnostic_service.get_diagnostic_by_case_id(case_id)
        
        if not diagnostic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diagnostic not found for case '{case_id}'"
            )
        
        logger.info(f"Retrieved diagnostic for case {case_id}")
        
        # Convert datetime objects to strings for JSON serialization
        if "fecha_revision" in diagnostic and diagnostic["fecha_revision"]:
            diagnostic["fecha_revision"] = diagnostic["fecha_revision"].isoformat()
            
        return JSONResponse(
            content=diagnostic,
            status_code=status.HTTP_200_OK
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving diagnostic for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving diagnostic"
        )

@router.get("/cases", response_model=List[Dict[str, Any]])
async def get_processed_cases():
    """
    Get all prediagnostic cases with 'procesado' status for doctor review (HU3).
    
    This endpoint implements the requirement:
    "Como usuario (doctor) quiero ver una lista de casos pendientes de pacientes para ser revisados"
    
    Filters the MongoDB prediagnosticos collection for cases with estado="procesado"
    and returns formatted results with only relevant fields: id, paciente, fecha, estado.
    
    Returns:
        List[Dict]: List of processed cases ready for doctor review
        [
            {
                "id": "prediagnostico_id",
                "paciente": "user_id", 
                "fecha": "2023-XX-XXTXX:XX:XX.XXXXXX",
                "estado": "procesado"
            },
            ...
        ]
        
    Raises:
        HTTPException 500: If database query fails
    """
    try:
        logger.info("Retrieving all processed cases for doctor review (HU3)")
        
        # Get processed cases from the service
        processed_cases = await prediagnostic_service.get_processed_cases()
        
        logger.info(f"Successfully retrieved {len(processed_cases)} processed cases")
        
        return JSONResponse(
            content=processed_cases,
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error retrieving processed cases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving processed cases"
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
        "description": "Service to retrieve prediagnostic cases and diagnostics for patient/doctor review",
        "hu_implementation": "Patient radiograph detail view + Doctor case selection",
        "endpoints": {
            "/cases": "GET - Get all processed cases for doctor review (HU3)",
            "/case/{prediagnostico_id}": "GET - Get case details for doctor review",
            "/health": "GET - Service health check",
            "/info": "GET - Service information"
        },
        "integration": "Designed for BusinessLogic orchestration via REST → GraphQL"
    }


@router.get("/cases/{user_id}", response_model=Dict[str, Any])
async def get_cases_by_user(user_id: str):
    """
    Get all prediagnostic cases for a given user_id.
    Returns an array of cases with selected fields.
    """
    try:
        cases = await prediagnostic_cases_service.get_cases_by_user(user_id)
        return JSONResponse(content={"cases": cases}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error retrieving cases for user_id {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving cases"
        )

@router.post("/process") 
async def process_image(imagen: UploadFile = File(...), user_id: str = Form(...)):

    prediagnostico_id = str(uuid.uuid4())
    nombre_imagen = f"RAD-{str(uuid.uuid4())}.jpg"
    ruta = STORAGE_DIR / nombre_imagen

    try:
        with open(ruta, "wb") as w:
            shutil.copyfileobj(imagen.file, w)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"No fue posible guardar la imagen"
        )

    entrada = {
        "user_id": user_id,
        "prediagnostico_id": prediagnostico_id,
        "radiografia_ruta": str(ruta),
        "resultado_modelo": {
            "probabilidad_neumonia": 0,
            "etiqueta": ""
        },
        "estado": "pendiente",
        "fecha_procesamiento": 0,
        "fecha_subida": str(datetime.utcnow())
    }

    try:
        await prediagnostic_service.create_prediagnostico(entrada)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Ocurrio un problema durante el guardado del prediagnostico"
        )

    try:
        await prediagnostic_service.process_image_ai(entrada)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Ocurrio un problema durante el guardado del prediagnostico"
        )

    return {
        "ruta_prediagnostico": entrada["radiografia_ruta"],
        "prediagnostico_id": entrada["prediagnostico_id"]
    }
