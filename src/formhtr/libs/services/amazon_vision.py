import boto3

from ..region import Rectangle


class AmazonVision:
    def __init__(self, amazon_credentials):
        """Create a Textract client.

        Args:
            amazon_credentials: Dict with ``ACCESS_KEY``, ``SECRET_KEY``, ``REGION``.
        """
        self.client = boto3.client('textract',
                                   aws_access_key_id=amazon_credentials['ACCESS_KEY'],
                                   aws_secret_access_key=amazon_credentials['SECRET_KEY'],
                                   region_name=amazon_credentials['REGION'])

    def annotate_image(self, image_stream):
        """Call ``detect_document_text`` on image bytes.

        Args:
            image_stream: Object with ``getvalue()`` returning raw image bytes.

        Returns:
            Textract API response dict.
        """
        image = image_stream.getvalue()
        response = self.client.detect_document_text(Document={'Bytes': bytearray(image)})
        return response

    def process_output(self, outputs, img_width, img_height):
        """Map Textract ``WORD`` blocks to pixel ``Rectangle`` instances.

        Args:
            outputs: Textract response containing ``Blocks``.
            img_width: Page width in pixels for scaling normalized boxes.
            img_height: Page height in pixels for scaling normalized boxes.

        Returns:
            List of ``Rectangle`` instances (one per word).
        """
        identified = []
    
        # Iterate through detected items in the response
        for item in outputs.get('Blocks', []):
            # Filter for lines or words if desired (also consider 'WORD' if needed)
            if item['BlockType'] in ['WORD']:
                # Extract the text
                text = item.get('Text', '')
                
                # Extract the bounding box coordinates
                box = item.get('Geometry', {}).get('BoundingBox', {})
                
                # Convert relative coordinates to absolute coordinates
                abs_width = box.get('Width', 0) * img_width
                abs_height = box.get('Height', 0) * img_height
                abs_left = box.get('Left', 0) * img_width
                abs_top = box.get('Top', 0) * img_height
                
                # Calculate top-left and bottom-right coordinates
                top_left = [abs_left, abs_top]
                bottom_right = [abs_left + abs_width, abs_top + abs_height]
                
                # Append the extracted data to the list
                identified.append(Rectangle(*top_left, *bottom_right, text))
        
        return identified
