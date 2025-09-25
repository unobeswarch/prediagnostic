import numpy as np
from PIL import Image
import cv2
from io import BytesIO

def resizeImage(image, size, verbose=False):
    """
    Resizes an in-memory image to the specified size.

    Parameters:
        image (PIL.Image.Image): The image to resize.
        size (tuple): Desired size as (width, height).
        verbose (bool): If True, print detailed messages.

    Returns:
        PIL.Image.Image: Resized image.
    """
    try:
        resized_img = image.resize(size, Image.LANCZOS)
        if verbose:
            print(f"Image resized to {size}.")
        return resized_img
    except Exception as e:
        raise Exception(f"Error resizing image: {e}")


def convertOneChanneltoThreeChannels(image, verbose=False):
    """
    Converts an in-memory image to three channels (RGB) if it has one channel (grayscale).

    Parameters:
        image (PIL.Image.Image): The image to process.
        verbose (bool): If True, print detailed messages.

    Returns:
        PIL.Image.Image: The processed image with three channels (RGB).
    """
    try:
        # Convert PIL image to NumPy array for OpenCV processing
        image_array = np.array(image)

        if verbose:
            print(f"Original image shape: {image_array.shape}")

        # Check if the image is grayscale (one channel)
        if len(image_array.shape) == 2 or (len(image_array.shape) == 3 and image_array.shape[2] == 1):
            # Convert grayscale to RGB
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            if verbose:
                print("Image has been converted to three channels (RGB).")
            # Convert back to PIL Image
            return Image.fromarray(rgb_image)
        elif len(image_array.shape) == 3 and image_array.shape[2] == 3:
            if verbose:
                print("Image already has three channels (RGB).")
            return image  # No conversion needed
        else:
            raise ValueError("Image format not recognized. It must be grayscale or RGB.")
    except Exception as e:
        raise Exception(f"Error converting image: {e}")

#last one
def convert_to_jpeg(image, quality=95):
    """
    Converts an image to JPEG format.

    Parameters:
        image (PIL.Image.Image): The image to convert.
        quality (int): Quality of the resulting JPEG image (default: 95).

    Returns:
        BytesIO: A BytesIO object containing the JPEG image data.
    """
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
        raise Exception(f"Error converting image to JPEG: {e}")