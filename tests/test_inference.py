"""
Tests for the inference module.
"""
import pytest
from PIL import Image
import numpy as np
from io import BytesIO

from src.inference.predictor import PneumoniaPredictor
from src.models.utils import preprocess_image, resize_image, convert_one_channel_to_three_channels

class TestPneumoniaPredictor:
    """Tests for PneumoniaPredictor class."""
    
    @pytest.fixture
    def predictor(self):
        """Create a predictor instance for testing."""
        # Note: This will require the model file to exist
        return PneumoniaPredictor()
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing."""
        # Create a sample RGB image
        image_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        return Image.fromarray(image_array)
    
    @pytest.fixture
    def sample_grayscale_image(self):
        """Create a sample grayscale image for testing."""
        image_array = np.random.randint(0, 256, (224, 224), dtype=np.uint8)
        return Image.fromarray(image_array, mode='L')
    
    def test_predictor_initialization(self, predictor):
        """Test that predictor initializes correctly."""
        assert predictor is not None
        assert predictor.model.is_loaded()
    
    def test_predict_from_image(self, predictor, sample_image):
        """Test prediction from PIL Image."""
        result = predictor.predict_from_image(sample_image)
        
        assert "prediction_id" in result
        assert "timestamp" in result
        assert "predicted_class" in result
        assert "confidence" in result
        assert "predictions" in result
        assert result["predicted_class"] in ["No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"]
        assert 0 <= result["confidence"] <= 1
    
    def test_predict_from_file(self, predictor, sample_image):
        """Test prediction from file bytes."""
        # Convert image to bytes
        img_bytes = BytesIO()
        sample_image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        result = predictor.predict_from_file(img_bytes, filename="test.jpg")
        
        assert "prediction_id" in result
        assert "filename" in result
        assert result["filename"] == "test.jpg"
        assert "predicted_class" in result
        assert "confidence" in result
    
    def test_health_check(self, predictor):
        """Test health check functionality."""
        health = predictor.health_check()
        
        assert "status" in health
        assert "model_loaded" in health
        assert "class_labels" in health
        assert "timestamp" in health
        assert health["status"] == "healthy"
        assert health["model_loaded"] is True


class TestImageUtils:
    """Tests for image utility functions."""
    
    @pytest.fixture
    def sample_rgb_image(self):
        """Create a sample RGB image."""
        image_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        return Image.fromarray(image_array)
    
    @pytest.fixture
    def sample_grayscale_image(self):
        """Create a sample grayscale image."""
        image_array = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        return Image.fromarray(image_array, mode='L')
    
    def test_resize_image(self, sample_rgb_image):
        """Test image resizing."""
        original_size = sample_rgb_image.size
        new_size = (200, 150)
        
        resized = resize_image(sample_rgb_image, size=new_size)
        
        assert resized.size == new_size
        assert resized.size != original_size
    
    def test_convert_grayscale_to_rgb(self, sample_grayscale_image):
        """Test converting grayscale to RGB."""
        converted = convert_one_channel_to_three_channels(sample_grayscale_image)
        
        assert converted.mode == 'RGB'
        assert len(np.array(converted).shape) == 3
        assert np.array(converted).shape[2] == 3
    
    def test_convert_rgb_unchanged(self, sample_rgb_image):
        """Test that RGB images remain unchanged."""
        result = convert_one_channel_to_three_channels(sample_rgb_image)
        
        assert result.mode == sample_rgb_image.mode
        assert result.size == sample_rgb_image.size
        assert np.array_equal(np.array(result), np.array(sample_rgb_image))
    
    def test_preprocess_image(self, sample_rgb_image):
        """Test complete image preprocessing."""
        processed = preprocess_image(sample_rgb_image)
        
        # Check that result is a numpy array
        assert isinstance(processed, np.ndarray)
        
        # Check that it has batch dimension
        assert len(processed.shape) == 4
        assert processed.shape[0] == 1  # Batch size
        
        # Check normalization (values should be between 0 and 1)
        assert processed.min() >= 0
        assert processed.max() <= 1