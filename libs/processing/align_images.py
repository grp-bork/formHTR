import numpy as np
import cv2
import math


def compute_closest_point(point, corners):
    distances = [math.dist(point, corner) for corner in corners]
    closest_index = np.argmin(distances)
    return corners[closest_index]


def find_corners(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Enhanced Edge Detection
    edged = cv2.Canny(gray, 50, 150)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # Find Contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    all_corners = []

    # Loop over contours and approximate the shape
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # Assuming the box has 4 sides
        if len(approx) == 4:
            rect = cv2.minAreaRect(approx)
            corners = cv2.boxPoints(rect)
            corners = [(int(x), int(y)) for (x, y) in corners]
            all_corners += corners

    # to determine image corner points
    height, width, _ = image.shape

    # Order of corners is top-left, top-right, bottom-right, bottom-left
    outer_corners = [compute_closest_point((0, 0), all_corners),
                     compute_closest_point((width, 0), all_corners),
                     compute_closest_point((width, height), all_corners),
                     compute_closest_point((0, height), all_corners)]

    return outer_corners


def align_images(scanned, template):
    # Find corners in both images
    template_corners = find_corners(template)
    scanned_corners = find_corners(scanned)

    # Compute the transformation matrix and apply it
    h, _ = cv2.findHomography(np.array(scanned_corners), np.array(template_corners))
    aligned = cv2.warpPerspective(scanned, h, (template.shape[1], template.shape[0]))

    return aligned
