import numpy as np
import cv2
from math import dist


def compute_closest_point(point, corners):
    distances = [dist(point, corner) for corner in corners]
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
    largest_contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]

    rect = cv2.minAreaRect(largest_contour)
    bounding_box = cv2.boxPoints(rect)
    bounding_box = np.int0(bounding_box)

    # to determine image corner points
    height, width, _ = image.shape

    # Order of corners is top-left, top-right, bottom-right, bottom-left
    outer_corners = [compute_closest_point((0, 0), bounding_box),
                     compute_closest_point((width, 0), bounding_box),
                     compute_closest_point((width, height), bounding_box),
                     compute_closest_point((0, height), bounding_box)]

    return outer_corners


def transform(scanned, template, scanned_points, template_points):
    # Compute the transformation matrix and apply it
    h, _ = cv2.findHomography(np.array(scanned_points), np.array(template_points))
    return cv2.warpPerspective(scanned, h, (template.shape[1], template.shape[0]))


def align_images(scanned, template):
    # Find corners in both images
    template_corners = find_corners(template)
    scanned_corners = find_corners(scanned)
    return transform(scanned, template, scanned_corners, template_corners)
