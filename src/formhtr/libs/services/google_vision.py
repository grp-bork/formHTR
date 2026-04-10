from google.cloud import vision_v1
from google.oauth2 import service_account

from ..region import Rectangle
from .utils import extract_corners


class GoogleVision:
    def __init__(self, key_path):
        """Create a Vision client from a service-account JSON path.

        Args:
            key_path: Filesystem path to Google Cloud service account JSON.
        """
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)

    def annotate_image(self, image_stream):
        """Run document text detection on a JPEG byte stream.

        Args:
            image_stream: Binary stream with ``getvalue()`` returning JPEG bytes.

        Returns:
            ``text_annotations`` from the Vision API (protobuf-like objects).
        """
        image = image_stream.getvalue()

        image_context = vision_v1.ImageContext(language_hints=['en'])
        vision_image = vision_v1.Image(content=image)
        response = self.client.text_detection(image=vision_image, image_context=image_context)
        return response.text_annotations

    def process_output(self, outputs):
        """Convert Vision annotations to ``Rectangle`` words (skips full-page block).

        Args:
            outputs: Iterable of text annotation objects (index 0 = full text).

        Returns:
            List of ``Rectangle`` instances with text and axis-aligned boxes.
        """
        identified = []
        # Iterate through OCR results and annotate the image
        for text in outputs[1:]:  # [1:] to exclude the first element which is the entire text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            string_encode = text.description.encode('ascii', 'ignore')
            start, end = extract_corners(vertices)
            identified.append(Rectangle(*start, *end, string_encode.decode()))
        return identified
