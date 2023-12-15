import cv2
import zxingcpp
from pyzbar.pyzbar import decode


def extract_barcode(candidates):
    barcodes = []
    for key in candidates.keys():
        if len(candidates[key]) == 1:
            barcodes.append(candidates[key][0].content)

    if barcodes:
        return max(set(barcodes), key=barcodes.count)

def read_barcode(image, candidates):
    # try zxingcpp
    detected_objects = zxingcpp.read_barcodes(image)
    if detected_objects:
        return detected_objects[0].text
    
    # try pyzbar
    decoded_objects = decode(image)
    barcodes = [obj.data.decode('utf-8') for obj in decoded_objects]
    if barcodes:
        return barcodes[0]
        
    # try to rotate the image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Edge detection
    edges = cv2.Canny(gray_image, 100, 200)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the rotated bounding box of the largest contour
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[-1]

        # Rotate the image to align the barcode
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Decode the barcode
        detected_objects = zxingcpp.read_barcodes(rotated_image)

        if detected_objects:
            return detected_objects[0].text

    return extract_barcode(candidates)
