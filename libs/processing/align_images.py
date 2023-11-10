import numpy as np
import cv2


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

    # Loop over contours and approximate the shape
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # Assuming the box has 4 sides
        if len(approx) == 4:
            rect = cv2.minAreaRect(approx)
            corners = cv2.boxPoints(rect)
            corners = np.int0(corners)

            return corners

    return None  # No box found


def align_images(template, scanned):
    # Find corners in both images
    template_corners = find_corners(template)
    scanned_corners = find_corners(scanned)

    # Order the corners (top-left, top-right, bottom-right, bottom-left)
    # This step can be refined based on your rectangle's orientation
    template_corners = sorted(template_corners, key=lambda x: x[0] + x[1])
    scanned_corners = sorted(scanned_corners, key=lambda x: x[0] + x[1])

    # Compute the transformation matrix and apply it
    h, _ = cv2.findHomography(np.array(scanned_corners), np.array(template_corners))
    aligned = cv2.warpPerspective(scanned, h, (template.shape[1], template.shape[0]))

    return aligned
