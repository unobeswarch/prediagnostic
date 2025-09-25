"""
Prediction service for pneumonia detection.
"""
from PIL import Image
from io import BytesIO
import logging
from typing import Dict, Any
import uuid
from datetime import datetime

from ..models.model import PneumoniaModel
from ..models.utils import preprocess_image, convert_to_jpeg, validate_image

logger = logging.getLogger(__name__)

class PneumoniaPredictor:
    """
    High-level predictor service for pneumonia detection.
    """
    
    def __init__(self):
        """Initialize the predictor with the model."""
        self.model = PneumoniaModel()
        self._initialize_model()
        
    def _initialize_model(self):
        """Load the model during initialization."""
        success = self.model.load_model()
        if not success:
            raise RuntimeError("Failed to load pneumonia prediction model")
        logger.info("PneumoniaPredictor initialized successfully")
    
    def predict_from_file(self, file_content: bytes, filename: str = None) -> Dict[str, Any]:
        """
        Predict pneumonia from uploaded file content.
        
        Args:
            file_content: Raw bytes of the uploaded image file.
            filename: Original filename (optional).
            
        Returns:
            dict: Prediction results with metadata.
        """
        try:
            # Generate prediction ID for tracking
            prediction_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            # Load image from bytes
            original_image = Image.open(BytesIO(file_content))
            
            # Validate image (create a copy since verify() closes the original)
            image_copy = Image.open(BytesIO(file_content))
            if not validate_image(image_copy):
                raise ValueError("Invalid image format or dimensions")
            
            # Convert to JPEG for consistent processing
            jpeg_image = convert_to_jpeg(original_image)
            
            # Reload the JPEG image for further processing
            processed_image = Image.open(jpeg_image)
            
            # Preprocess the image
            image_array = preprocess_image(processed_image, verbose=False)
            
            # Make prediction
            prediction_result = self.model.predict(image_array)
            
            # Prepare response
            response = {
                "prediction_id": prediction_id,
                "timestamp": timestamp,
                "filename": filename,
                "image_info": {
                    "original_size": original_image.size,
                    "processed_size": processed_image.size,
                    "mode": original_image.mode
                },
                **prediction_result
            }
            
            logger.info(f"Prediction completed: {prediction_id} - {prediction_result['predicted_class']}")
            return response
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise
    
    def predict_from_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predict pneumonia from PIL Image object.
        
        Args:
            image: PIL Image object.
            
        Returns:
            dict: Prediction results.
        """
        try:
            # Generate prediction ID for tracking
            prediction_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            # Validate image
            if not validate_image(image):
                raise ValueError("Invalid image format or dimensions")
            
            # Preprocess the image
            image_array = preprocess_image(image, verbose=False)
            
            # Make prediction
            prediction_result = self.model.predict(image_array)
            
            # Prepare response
            response = {
                "prediction_id": prediction_id,
                "timestamp": timestamp,
                "image_info": {
                    "size": image.size,
                    "mode": image.mode
                },
                **prediction_result
            }
            
            logger.info(f"Prediction completed: {prediction_id} - {prediction_result['predicted_class']}")
            return response
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the predictor is ready to make predictions.
        
        Returns:
            dict: Health status information.
        """
        return {
            "status": "healthy" if self.model.is_loaded() else "unhealthy",
            "model_loaded": self.model.is_loaded(),
            "class_labels": self.model.class_labels,
            "timestamp": datetime.utcnow().isoformat()
        }