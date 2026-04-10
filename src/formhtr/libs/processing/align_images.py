from math import dist, isclose

import cv2
import numpy as np


def validate_corners(corners, height, width, tol=20):
    """Check that four corners form a plausible document quad.

    Args:
        corners: Four ``(x, y)`` points in order TL, TR, BR, BL.
        height: Image height in pixels.
        width: Image width in pixels.
        tol: Maximum relative margin (percent of image) for side length mismatch.

    Returns:
        ``True`` if opposite sides match within tolerance.
    """
    top_width = dist(corners[0], corners[1])
    bottom_width = dist(corners[3], corners[2])

    if not isclose(top_width, bottom_width, abs_tol=width/100):
        return False

    percentage_top = 1 - top_width/width
    percentage_bottom = 1 - bottom_width/width

    if percentage_top > tol/100 or percentage_bottom > tol/100:
        return False

    left_height = dist(corners[0], corners[3])
    right_height = dist(corners[1], corners[2])

    if not isclose(left_height, right_height, abs_tol=height/100):
        return False

    percentage_left = 1 - left_height/height
    percentage_right = 1 - right_height/height

    if percentage_left > tol/100 or percentage_right > tol/100:
        return False

    return True


def compute_closest_point(point, corners):
    """Pick the corner nearest to a reference image corner.

    Args:
        point: Reference ``(x, y)``.
        corners: Candidate corner coordinates.

    Returns:
        The closest corner from ``corners``.
    """
    distances = [dist(point, corner) for corner in corners]
    closest_index = np.argmin(distances)
    return corners[closest_index]


def find_corners(image, filter_grayscale, num=10, gray_filter=20):
    """Detect outer document corners via contours and min-area rectangles.

    Args:
        image: BGR ``numpy`` image.
        filter_grayscale: If True, threshold grayscale before edge detection.
        num: Number of largest contours to consider (increased recursively on failure).
        gray_filter: Threshold value when ``filter_grayscale`` is True.

    Returns:
        ``(outer_corners, valid)`` where ``outer_corners`` are four ``(x, y)`` tuples
        and ``valid`` reflects ``validate_corners`` (may recurse with larger ``num``).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    if filter_grayscale:
        _, gray = cv2.threshold(gray, gray_filter, 255, cv2.THRESH_BINARY)

    # Enhanced Edge Detection
    edged = cv2.Canny(gray, 50, 150)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # Find Contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # take num of largest contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:num]

    box_points = []

    for contour in contours:
        rect = cv2.minAreaRect(contour)
        bounding_box = cv2.boxPoints(rect)
        box_points += [tuple(point) for point in bounding_box.astype(int)]

    copy_image = image.copy()
    for corner in box_points:
        copy_image = cv2.circle(copy_image, corner, radius=15, color=(0, 0, 255), thickness=15)
    

    # to determine image corner points
    height, width, _ = image.shape

    # Order of corners is top-left, top-right, bottom-right, bottom-left
    outer_corners = [compute_closest_point((0, 0), box_points),
                     compute_closest_point((width, 0), box_points),
                     compute_closest_point((width, height), box_points),
                     compute_closest_point((0, height), box_points)]
    
    for corner in outer_corners:
        copy_image = cv2.circle(copy_image, corner, radius=15, color=(255, 0, 0), thickness=15)

    corners_valid = validate_corners(outer_corners, height, width)
    if not corners_valid and num < 50:
        return find_corners(image, filter_grayscale, num=num+10, gray_filter=gray_filter+10)

    return outer_corners, corners_valid


def transform(scanned, template, scanned_points, template_points):
    """Apply a homography mapping scan corners to template corners.

    Args:
        scanned: Source BGR image.
        template: Target image defining output size.
        scanned_points: Four scan corner coordinates.
        template_points: Four template corner coordinates.

    Returns:
        Warped ``scanned`` with template dimensions.
    """
    h, _ = cv2.findHomography(np.array(scanned_points), np.array(template_points))
    return cv2.warpPerspective(scanned, h, (template.shape[1], template.shape[0]))


def align_images(scanned, template, filter_grayscale):
    """Align ``scanned`` to ``template`` using automatically detected corners.

    Args:
        scanned: Scanned page BGR image.
        template: Template BGR image.
        filter_grayscale: Passed to ``find_corners`` for the scan and template.

    Returns:
        Warped scan, or ``None`` if corners are invalid for either image.
    """
    template_corners, template_valid = find_corners(template, filter_grayscale)
    scanned_corners, scanned_valid = find_corners(scanned, filter_grayscale)
    if template_valid and scanned_valid:
        return transform(scanned, template, scanned_corners, template_corners)

def format_point(point):
    """Serialize a corner to JSON-friendly ints.

    Args:
        point: ``(x, y)`` numeric pair.

    Returns:
        Dict with ``x`` and ``y`` keys.
    """
    return {
        "x": int(point[0]),
        "y": int(point[1])
    }

def get_alignment_data(scanned, template):
    """Compute template and scan corner sets for external alignment UIs.

    Args:
        scanned: Scanned BGR image.
        template: Template BGR image.

    Returns:
        Dict with ``templatePoints`` and ``targetPoints`` lists of ``{"x","y"}`` dicts.
    """
    template_corners, _ = find_corners(template, False)
    scanned_corners, _ = find_corners(scanned, False)
   
    return {
        "templatePoints": [format_point(p) for p in template_corners],
        "targetPoints": [format_point(p) for p in scanned_corners]
    }
