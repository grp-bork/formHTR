from google.cloud import vision_v1
from google.oauth2 import service_account

from libs.region import Rectangle


def extract_corners(points):
    """Identify bounding box for given polygon

    Args:
        points (list): list of coordinates

    Returns:
        list: top-left and bottom-right coordinates
    """
    min_x = min(points, key=lambda pt: pt[0])[0]
    min_y = min(points, key=lambda pt: pt[1])[1]
    max_x = max(points, key=lambda pt: pt[0])[0]
    max_y = max(points, key=lambda pt: pt[1])[1]
    
    return (min_x, min_y), (max_x, max_y)


class GoogleVision:
    def __init__(self, key_path):
        # Authenticate with Google Cloud using the key file
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)

    def annotate_image(self, image_stream):
        image = image_stream.getvalue()

        image_context = vision_v1.ImageContext(language_hints=['en'])
        vision_image = vision_v1.Image(content=image)
        response = self.client.text_detection(image=vision_image, image_context=image_context)
        return response.text_annotations

    def process_output(self, outputs):
        identified = []
        # Iterate through OCR results and annotate the image
        for text in outputs[1:]:  # [1:] to exclude the first element which is the entire text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            string_encode = text.description.encode('ascii', 'ignore')
            start, end = extract_corners(vertices)
            identified.append(Rectangle(*start, *end, string_encode.decode()))
        return identified
