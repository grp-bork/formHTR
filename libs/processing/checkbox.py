import cv2
import numpy as np


def is_ticked(image_array, edge_ignore_percentage=0.2, threshold_percentage=0.1):
    """Detected whether checkbox is ticked

    Args:
        image_array (np.array): given picture
        edge_ignore_percentage (float, optional): cutoff edges to avoid detecting box. Defaults to 0.2.
        threshold_percentage (float, optional): required amount of dark pixel. Defaults to 0.1.

    Returns:
        bool: True if checkbox is ticked
    """
    # Ensure the image is in grayscale
    if len(image_array.shape) == 3:
        image_gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image_array

    # Calculate the amount to crop
    h, w = image_gray.shape
    crop_x = int(w * edge_ignore_percentage)
    crop_y = int(h * edge_ignore_percentage)

    # Crop the image
    cropped = image_gray[crop_y:h-crop_y, crop_x:w-crop_x]
    
    # Threshold the image (assuming the checkbox is darker)
    _, binary = cv2.threshold(cropped, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate the percentage of black pixels
    black_pixels = np.sum(binary == 255)
    total_pixels = binary.size
    black_percentage = black_pixels / total_pixels

    # Determine if checked
    return black_percentage > threshold_percentage
