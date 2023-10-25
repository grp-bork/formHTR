import cv2
from PIL import Image
import io
from skimage import filters, measure, morphology
from skimage.filters import threshold_triangle
from skimage.color import rgb2gray

from libs.services.google_vision import GoogleVision


def extract_framebox(image):
    """
    Detect the main framebox of the template.
    Used to avoid rectangle detection outside this area.

    Args:
        image (Image): given image

    Returns:
        list: coordinates of the framebox
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    coords = []
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)

        if len(approx) == 4:
            coords.append([w * h, [x, y, w, h]])
    return max(coords)[1]


def detect_rectangles(image, filter_scale):
    """
    Automatically detect rectangle within given image.
    These can be then used as potential candidates for ROIs.

    Args:
        image (Image): image object
        filter_scale (float): scaling factor to filter out too small rectangles (recommended value between 1 and 3)

    Returns:
        list: list of discovered rectangles
    """

    image_gray = rgb2gray(image)
    _, width = image_gray.shape
    framebox = extract_framebox(image)

    gray_cut = image_gray[framebox[1] : framebox[3] + framebox[1],
                          framebox[0] : framebox[2] + framebox[0]]

    thresh = threshold_triangle(gray_cut)
    binary = gray_cut > thresh

    image = binary
    # Binary image, post-process the binary mask and compute labels
    threshold = filters.threshold_otsu(image)
    mask = image > threshold
    mask = morphology.remove_small_objects(mask, width/filter_scale)
    mask = morphology.remove_small_holes(mask, width/(filter_scale*5))
    labels = measure.label(mask)

    rectangles = []

    props = measure.regionprops(labels, image)

    for index in range(1, labels.max()):
        minr, minc, maxr, maxc = props[index].bbox
        rectangles.append((minc + framebox[0], minr + framebox[1], maxc + framebox[0], maxr + framebox[1]))
    
    return rectangles


def find_residuals(image, credentials):
    """Use Google vision service to find existing printed texts (residuals)

    Args:
        image (list): image in numpy array format
        credentials (dict): credentials for Google vision service

    Returns:
        list: list of identified residuals
    """

    google = GoogleVision(credentials)

    image_pil = Image.fromarray(image)
    image_stream = io.BytesIO()
    image_pil.save(image_stream, format='PNG')

    identified = google.annotate_image(image_stream)
    identified = google.process_output(identified)
    return [rectangle.to_residual() for rectangle in identified]
