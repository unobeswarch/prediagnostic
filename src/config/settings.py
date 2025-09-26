"""
Configuration settings for the pneumonia prediction microservice.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "finalModel.keras"

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Model Configuration
CLASS_LABELS = ["No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"]

# Image Processing Configuration
IMAGE_SIZE = (500, 720)  # (width, height)
JPEG_QUALITY = 95

# TensorFlow Configuration
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU by default
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "prediagnostic_db")

# Collection names matching real schema
PREDIAGNOSTICOS_COLLECTION = os.getenv("PREDIAGNOSTICOS_COLLECTION", "prediagnosticos")
DIAGNOSTICOS_COLLECTION = os.getenv("DIAGNOSTICOS_COLLECTION", "diagnosticos")

MONGODB_CONNECTION_TIMEOUT: int = int(os.getenv("MONGODB_CONNECTION_TIMEOUT", "10000"))
MONGODB_SERVER_SELECTION_TIMEOUT: int = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "5000"))
# Business Logic Service Configuration (for future integration)
BUSINESS_LOGIC_SERVICE_URL = os.getenv("BUSINESS_LOGIC_SERVICE_URL", "http://localhost:8001")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")