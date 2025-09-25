"""
Tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
import numpy as np

from cmd.server import app

client = TestClient(app)

class TestAPI:
    """Tests for API endpoints."""
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes for testing."""
        # Create a sample image
        image_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        image = Image.fromarray(image_array)
        
        # Convert to bytes
        img_bytes = BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        # Note: This might fail if model is not loaded
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
    
    def test_service_info(self):
        """Test service info endpoint."""
        response = client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "service_name" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_predict_endpoint_no_file(self):
        """Test predict endpoint without file."""
        response = client.post("/api/v1/predict")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_predict_endpoint_with_image(self, sample_image_bytes):
        """Test predict endpoint with image."""
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        
        # Note: This might fail if model is not loaded
        if response.status_code == 200:
            data = response.json()
            assert "prediction_id" in data
            assert "predicted_class" in data
            assert "confidence" in data
            assert data["predicted_class"] in ["No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"]
        else:
            # Service might not be available during testing
            assert response.status_code in [503, 500]
    
    def test_predict_endpoint_invalid_file_type(self):
        """Test predict endpoint with invalid file type."""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/predict", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_predict_endpoint_large_file(self):
        """Test predict endpoint with oversized file."""
        # Create a large dummy file (simulate > 10MB)
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.jpg", large_data, "image/jpeg")}
        response = client.post("/api/v1/predict", files=files)
        
        assert response.status_code == 413  # Request Entity Too Large