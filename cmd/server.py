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
from src.api.routes import router
from src.config.settings import API_HOST, API_PORT, DEBUG
from src.database.mongodb import mongo_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Prediagnostic Case Service",
    description="Service to retrieve prediagnostic cases for doctor review",
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
app.include_router(router, prefix="/prediagnostic")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Starting Prediagnostic Service...")
        
        # Initialize MongoDB connection
        await mongo_manager.connect()
        logger.info("MongoDB connected successfully")
        
        logger.info("Service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Prediagnostic Service...")
    
    # Disconnect from MongoDB
    await mongo_manager.disconnect()
    logger.info("MongoDB disconnected")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Prediagnostic Case Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/prediagnostic"
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )