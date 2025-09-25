from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from keras.models import load_model
import tensorflow as tf
import numpy as np
from PIL import Image
from io import BytesIO
from dataTransformation import convertOneChanneltoThreeChannels, resizeImage, convert_to_jpeg
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_ENABLE_ONEDNN_OPTS"]="0"

tf.config.set_visible_devices([], 'GPU')

# Initialize FastAPI app
app = FastAPI()

# Mapping the predicted classes to their labels
class_labels = ["No Pneumonia", "Viral Pneumonia", "Bacterial Pneumonia"]

def preprossesing(image):
    # Apply preprocessing steps (assuming these functions handle the preprocessing)
    image = convertOneChanneltoThreeChannels(image, verbose=False)
    image = resizeImage(image, (500, 720), verbose=False)
    image_array = np.array(image) / 255.0  # Normalize the image to [0, 1]
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    return image_array

# Load the Keras model (ensure the model file is in the same directory or provide a path)
MODEL_PATH = "finalModel.keras"  # Replace with your model's path
model = load_model(MODEL_PATH)

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        original_image = Image.open(BytesIO(await file.read()))

        # Convert the image to JPEG
        jpeg_image = convert_to_jpeg(original_image)

        # Reload the JPEG image for further processing
        processed_image = Image.open(jpeg_image)
        
        # Preprocess the image
        image_array = preprossesing(processed_image)
        
        # Perform inference
        predictions = model.predict(image_array)
        
        # Get predicted class (index of highest probability)
        predicted_class = np.argmax(predictions, axis=-1)[0]
        
        # Get the probability of the predicted class
        predicted_probability = predictions[0][predicted_class]
        
        # Return the result with predicted class label and confidence
        return JSONResponse(content={
            "filename": file.filename,
            "predictions": predictions.tolist(),  # Return the raw predictions (probabilities)
            "predicted_class": class_labels[predicted_class],  # Return the class with highest probability
            "confidence": float(predicted_probability)  # Return the confidence of the prediction
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
