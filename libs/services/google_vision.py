from google.cloud import vision_v1
from google.oauth2 import service_account


class GoogleVision:
    def __init__(self, key_path):
        # Authenticate with Google Cloud using the key file
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)

    def annotate_image(self, image):
        image_context = vision_v1.ImageContext(language_hints=["en"])
        vision_image = vision_v1.Image(content=image)
        response = self.client.text_detection(image=vision_image, image_context=image_context)
        return response.text_annotations

    def process_output(self, outputs):
        identified = []
        # Iterate through OCR results and annotate the image
        for text in outputs[1:]:  # [1:] to exclude the first element which is the entire text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            string_encode = text.description.encode("ascii", "ignore")
            identified.append({'coords': vertices[0] + vertices[2], 'content': str(string_encode)})
        return identified
