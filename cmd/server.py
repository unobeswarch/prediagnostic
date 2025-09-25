"""
FastAPI server entry point for pneumonia prediction microservice.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from src.api.routes import router, initialize_predictor
from src.config.settings import API_HOST, API_PORT, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Pneumonia Prediction Service",
    description="AI-powered pneumonia detection from chest X-ray images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Starting Pneumonia Prediction Service...")
        
        # Initialize the predictor
        initialize_predictor()
        
        logger.info("Service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Pneumonia Prediction Service...")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Pneumonia Prediction Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1"
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )