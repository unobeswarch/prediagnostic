"""
Image preprocessing utilities for pneumonia prediction.
"""
import numpy as np
from PIL import Image
import cv2
from io import BytesIO
import logging
from ..config.settings import IMAGE_SIZE, JPEG_QUALITY

logger = logging.getLogger(__name__)

def resize_image(image: Image.Image, size: tuple = None, verbose: bool = False) -> Image.Image:
    """
    Resizes an in-memory image to the specified size.

    Args:
        image: The PIL Image to resize.
        size: Desired size as (width, height). If None, uses default from settings.
        verbose: If True, print detailed messages.

    Returns:
        PIL.Image.Image: Resized image.
    """
    size = size or IMAGE_SIZE
    
    try:
        resized_img = image.resize(size, Image.LANCZOS)
        if verbose:
            logger.info(f"Image resized to {size}.")
        return resized_img
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        raise Exception(f"Error resizing image: {e}")


def convert_one_channel_to_three_channels(image: Image.Image, verbose: bool = False) -> Image.Image:
    """
    Converts an in-memory image to three channels (RGB) if it has one channel (grayscale).

    Args:
        image: The PIL Image to process.
        verbose: If True, print detailed messages.

    Returns:
        PIL.Image.Image: The processed image with three channels (RGB).
    """
    try:
        # Convert PIL image to NumPy array for OpenCV processing
        image_array = np.array(image)

        if verbose:
            logger.info(f"Original image shape: {image_array.shape}")

        # Check if the image is grayscale (one channel)
        if len(image_array.shape) == 2 or (len(image_array.shape) == 3 and image_array.shape[2] == 1):
            # Convert grayscale to RGB
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            if verbose:
                logger.info("Image has been converted to three channels (RGB).")
            # Convert back to PIL Image
            return Image.fromarray(rgb_image)
        elif len(image_array.shape) == 3 and image_array.shape[2] == 3:
            if verbose:
                logger.info("Image already has three channels (RGB).")
            return image  # No conversion needed
        else:
            raise ValueError("Image format not recognized. It must be grayscale or RGB.")
    except Exception as e:
        logger.error(f"Error converting image: {e}")
        raise Exception(f"Error converting image: {e}")


def convert_to_jpeg(image: Image.Image, quality: int = None) -> BytesIO:
    """
    Converts an image to JPEG format.

    Args:
        image: The PIL Image to convert.
        quality: Quality of the resulting JPEG image. If None, uses default from settings.

    Returns:
        BytesIO: A BytesIO object containing the JPEG image data.
    """
    quality = quality or JPEG_QUALITY
    
    try:
        # Ensure the image is in RGB mode (required for JPEG)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Create an in-memory file for the JPEG image
        jpeg_image = BytesIO()
        image.save(jpeg_image, format="JPEG", quality=quality)
        jpeg_image.seek(0)  # Reset the pointer to the start of the BytesIO object

        return jpeg_image
    except Exception as e:
        logger.error(f"Error converting image to JPEG: {e}")
        raise Exception(f"Error converting image to JPEG: {e}")


def preprocess_image(image: Image.Image, size: tuple = None, verbose: bool = False) -> np.ndarray:
    """
    Complete preprocessing pipeline for an image.
    
    Args:
        image: The PIL Image to preprocess.
        size: Desired size as (width, height). If None, uses default from settings.
        verbose: If True, print detailed messages.
        
    Returns:
        np.ndarray: Preprocessed image array ready for model prediction.
    """
    try:
        # Apply preprocessing steps
        processed_image = convert_one_channel_to_three_channels(image, verbose=verbose)
        processed_image = resize_image(processed_image, size=size, verbose=verbose)
        
        # Convert to array and normalize
        image_array = np.array(processed_image) / 255.0  # Normalize to [0, 1]
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
        
        if verbose:
            logger.info(f"Preprocessed image shape: {image_array.shape}")
            
        return image_array
        
    except Exception as e:
        logger.error(f"Error in preprocessing pipeline: {e}")
        raise Exception(f"Error in preprocessing pipeline: {e}")


def validate_image(image: Image.Image) -> bool:
    """
    Validate that an image is suitable for processing.
    
    Args:
        image: The PIL Image to validate.
        
    Returns:
        bool: True if image is valid, False otherwise.
    """
    try:
        # Check if image is valid
        image.verify()
        
        # Check image dimensions
        width, height = image.size
        if width < 50 or height < 50:
            logger.warning(f"Image too small: {width}x{height}")
            return False
            
        # Check image mode
        if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
            logger.warning(f"Unsupported image mode: {image.mode}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return False