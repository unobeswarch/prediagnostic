#!/bin/bash
# Startup script for the pneumonia prediction service

echo "Starting Pneumonia Prediction Microservice..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if model exists
if [ ! -f "models/finalModel.keras" ]; then
    echo "Error: Model file not found at models/finalModel.keras"
    echo "Please ensure the model file is in the correct location."
    exit 1
fi

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt .requirements_installed ]; then
    echo "Installing/updating dependencies..."
    pip install -r requirements.txt
    touch .requirements_installed
fi

# Run the server
echo "Starting server on port 8000..."
python cmd/server.py