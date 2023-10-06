from easyocr import Reader
import cv2
import zxingcpp


def read_content(image, config):
    """
    Top level function to read content of ROIs.

    Args:
        image (Image): given image
        config (LogsheetConfig): configuration of given logsheet

    Returns:
        list: a list of identified content with its confidence
    """
    results = []

    for region in config.regions:
        fragment = image[region.start_y:region.end_y, region.start_x:region.end_x]
        content = ""
        probability = 1
        
        if region.content_type == 'Barcode':
            gray_image = cv2.cvtColor(fragment, cv2.COLOR_BGR2GRAY)

            # Edge detection
            edges = cv2.Canny(gray_image, 100, 200)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            # Get the rotated bounding box of the largest contour
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[-1]

            # Rotate the image to align the barcode
            (h, w) = fragment.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(fragment, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

            # Decode the barcode
            detected_objects = zxingcpp.read_barcodes(rotated_image)

            if detected_objects:
                content = detected_objects[0].text
        elif region.content_type == 'Digit':
            reader = Reader(['en'], True)
            result = reader.readtext(fragment, allowlist='0123456789')

            if result:
                content = result[0][1]
                probability = round(result[0][2], 2)
        else:
            reader = Reader(['en'], True)
            result = reader.readtext(fragment)

            if result:
                content = result[0][1]
                probability = round(result[0][2], 2)
            
        results.append([region.varname, fragment, content, probability])

    return results
