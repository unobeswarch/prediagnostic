"""
Minimal server for testing the project structure without TensorFlow.
This is useful for verifying the architecture works before dealing with TensorFlow installation issues.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import configuration
from src.config.settings import API_HOST, API_PORT, DEBUG, CLASS_LABELS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Pneumonia Prediction Service (Test Mode)",
    description="AI-powered pneumonia detection service - Test mode without TensorFlow",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Pneumonia Prediction Service (Test Mode)",
        "version": "1.0.0-test",
        "status": "running",
        "mode": "test",
        "docs": "/docs",
        "note": "This is test mode without TensorFlow. Install TensorFlow for full functionality."
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "test",
        "model_loaded": False,
        "class_labels": CLASS_LABELS,
        "note": "Running in test mode - TensorFlow not loaded"
    }

@app.get("/api/v1/info")
async def service_info():
    """Get service information."""
    return {
        "service_name": "Pneumonia Prediction Service",
        "version": "1.0.0-test",
        "mode": "test",
        "description": "AI-powered pneumonia detection from chest X-ray images",
        "endpoints": {
            "/": "Root endpoint",
            "/api/v1/health": "Service health check",
            "/api/v1/info": "Service information"
        },
        "supported_formats": ["JPEG", "PNG", "BMP", "TIFF"],
        "max_file_size": "10MB",
        "classes": CLASS_LABELS,
        "note": "Install TensorFlow to enable prediction endpoints"
    }

@app.post("/api/v1/predict")
async def predict_pneumonia_mock():
    """Mock prediction endpoint for testing."""
    raise HTTPException(
        status_code=503,
        detail="Prediction endpoint not available in test mode. Install TensorFlow to enable predictions."
    )

if __name__ == "__main__":
    logger.info("Starting Pneumonia Prediction Service in TEST MODE...")
    logger.info("Install TensorFlow to enable full functionality")
    
    uvicorn.run(
        "test_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )