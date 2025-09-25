# Pneumonia Prediction Microservice

AI-powered pneumonia detection microservice that analyzes chest X-ray images to classify pneumonia types.

## Overview

This microservice provides REST API endpoints for pneumonia prediction using a trained Keras model. It can distinguish between:
- No Pneumonia
- Viral Pneumonia 
- Bacterial Pneumonia

## Architecture

```
├── cmd/                    # Entry points
│   └── server.py          # FastAPI server
├── src/                   # Source code
│   ├── models/            # Model management
│   │   ├── model.py       # Model loading and prediction
│   │   └── utils.py       # Image preprocessing utilities
│   ├── inference/         # Prediction logic
│   │   └── predictor.py   # High-level prediction service
│   ├── api/               # REST API
│   │   └── routes.py      # FastAPI routes
│   └── config/            # Configuration
│       └── settings.py    # App settings and environment variables
├── tests/                 # Unit tests
├── notebooks/             # Jupyter notebooks for exploration
├── models/                # Trained model files
│   └── finalModel.keras   # Pre-trained pneumonia detection model
└── requirements.txt       # Python dependencies
```

## Quick Start

### Local Development

1. **Install Dependencies**
I recommend you to create a venv and install the dependencies there.
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**
   ```bash
   python cmd/server.py
   ```
   
   The server will start on `http://localhost:8000`

3. **Access API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Deployment

1. **Build the Docker Image**
   ```bash
   docker build -t pneumonia-prediction .
   ```

2. **Run the Container**
   ```bash
   docker run -p 8000:8000 pneumonia-prediction
   ```

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Service Information
```bash
GET /api/v1/info
```

### Pneumonia Prediction
```bash
POST /api/v1/predict
```

**Request:** Upload an image file (JPEG, PNG, BMP, TIFF)

**Response:**
```json
{
  "prediction_id": "uuid",
  "timestamp": "2023-XX-XXTXX:XX:XX.XXXXXX",
  "filename": "chest_xray.jpg",
  "predicted_class": "Bacterial Pneumonia",
  "confidence": 0.89,
  "predictions": [0.05, 0.06, 0.89],
  "image_info": {
    "original_size": [1024, 1024],
    "processed_size": [500, 720],
    "mode": "RGB"
  }
}
```

## Usage Examples

### Python Client
```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# Make prediction
with open("chest_xray.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/v1/predict", files=files)
    result = response.json()
    print(f"Prediction: {result['predicted_class']} (confidence: {result['confidence']:.2f})")
```

### cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Make prediction
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@chest_xray.jpg"
```

## Configuration

Environment variables can be set to customize behavior:

- `API_HOST`: Server host (default: "0.0.0.0")
- `API_PORT`: Server port (default: 8000) 
- `DEBUG`: Debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: "INFO")

For future integrations:
- `MONGODB_URL`: MongoDB connection string
- `DATABASE_NAME`: Database name for storing predictions
- `BUSINESS_LOGIC_SERVICE_URL`: URL of business logic service

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Model Information

The model (`finalModel.keras`) is a trained neural network that:
- Accepts chest X-ray images of any size
- Preprocesses images to 500x720 RGB format
- Outputs probabilities for 3 classes
- Provides confidence scores for predictions

## Development

### Adding New Features

1. **API Routes**: Add new endpoints in `src/api/routes.py`
2. **Business Logic**: Extend `src/inference/predictor.py`
3. **Configuration**: Update `src/config/settings.py`
4. **Tests**: Add tests in the `tests/` directory

### Integration with Other Services

This microservice is designed to integrate with:
- **MongoDB**: For storing prediction results and history
- **Business Logic Service**: For processing and workflow management
- **Authentication Service**: For API security (future enhancement)

## Monitoring and Logging

The service includes:
- Health check endpoint for monitoring
- Structured logging for debugging
- Request/response tracking with prediction IDs
- Docker health checks

## Security Considerations

- Input validation for uploaded files
- File size limits (10MB maximum)
- Image format validation
- Error handling without information leakage

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]