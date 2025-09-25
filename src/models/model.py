"""
Model loading and management functionality.
"""
import logging
from pathlib import Path
from ..config.settings import MODEL_PATH, CLASS_LABELS

# Try to import TensorFlow, fallback gracefully if not available
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    load_model = None

logger = logging.getLogger(__name__)

class PneumoniaModel:
    """
    Pneumonia prediction model wrapper.
    """
    
    def __init__(self, model_path: Path = None):
        """
        Initialize the model.
        
        Args:
            model_path: Path to the model file. If None, uses default from settings.
        """
        self.model = None
        self.model_path = model_path or MODEL_PATH
        self.class_labels = CLASS_LABELS
        
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available. Model functionality will be limited.")
        else:
            self._configure_tensorflow()
        
    def _configure_tensorflow(self):
        """Configure TensorFlow settings."""
        tf.config.set_visible_devices([], 'GPU')
        
    def load_model(self):
        """
        Load the Keras model from file.
        
        Returns:
            bool: True if model loaded successfully, False otherwise.
        """
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
            self.model = load_model(str(self.model_path))
            logger.info(f"Model loaded successfully from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(self, image_array):
        """
        Make prediction on preprocessed image array.
        
        Args:
            image_array: Preprocessed image array ready for prediction.
            
        Returns:
            dict: Prediction results containing predictions, predicted_class, and confidence.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        try:
            # Perform inference
            predictions = self.model.predict(image_array)
            
            # Get predicted class (index of highest probability)
            predicted_class_idx = predictions.argmax(axis=-1)[0]
            predicted_class = self.class_labels[predicted_class_idx]
            
            # Get the probability of the predicted class
            confidence = float(predictions[0][predicted_class_idx])
            
            return {
                "predictions": predictions.tolist(),
                "predicted_class": predicted_class,
                "predicted_class_index": int(predicted_class_idx),
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def is_loaded(self):
        """Check if model is loaded."""
        return self.model is not None