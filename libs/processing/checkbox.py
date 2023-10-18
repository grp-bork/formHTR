import cv2

def is_ticked(image_array, threshold_percentage=10):
    # Ensure the image is in grayscale
    if len(image_array.shape) == 3:
        image_gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image_array
    
    # Threshold the image to binary
    _, binary_image = cv2.threshold(image_gray, 250, 255, cv2.THRESH_BINARY_INV)
    
    # Count non-zero (black) pixels
    filled_pixels = cv2.countNonZero(binary_image)
    
    # Calculate the percentage of filled pixels
    total_pixels = binary_image.size
    filled_percentage = (filled_pixels / total_pixels) * 100
    
    # Compare against the threshold
    return filled_percentage > threshold_percentage
