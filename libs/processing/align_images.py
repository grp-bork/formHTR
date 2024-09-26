import numpy as np
import cv2
from math import dist, isclose


def validate_corners(corners, height, width, tol=20):
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
    distances = [dist(point, corner) for corner in corners]
    closest_index = np.argmin(distances)
    return corners[closest_index]


def find_corners(image, filter_grayscale, num=10, gray_filter=20):
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
        box_points += list(np.int0(bounding_box))

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
    # Compute the transformation matrix and apply it
    h, _ = cv2.findHomography(np.array(scanned_points), np.array(template_points))
    return cv2.warpPerspective(scanned, h, (template.shape[1], template.shape[0]))


def align_images(scanned, template, filter_grayscale):
    # Find corners in both images
    template_corners, template_valid = find_corners(template, filter_grayscale)
    scanned_corners, scanned_valid = find_corners(scanned, filter_grayscale)
    if template_valid and scanned_valid:
        return transform(scanned, template, scanned_corners, template_corners)
