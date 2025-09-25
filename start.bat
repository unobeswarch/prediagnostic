@echo off
REM Startup script for the pneumonia prediction service (Windows)

echo Starting Pneumonia Prediction Microservice...

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Check if model exists
if not exist "models\finalModel.keras" (
    echo Error: Model file not found at models\finalModel.keras
    echo Please ensure the model file is in the correct location.
    pause
    exit /b 1
)

REM Install dependencies (optional - uncomment if needed)
REM echo Installing/updating dependencies...
REM pip install -r requirements.txt

REM Run the server
echo Starting server on port 8000...
echo Access the API documentation at: http://localhost:8000/docs
echo.
python cmd\server.py

pause