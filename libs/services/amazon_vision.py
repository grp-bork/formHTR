import boto3


class AmazonVision:
    def __init__(self, amazon_credentials):
        self.client = boto3.client("textract",
                                   aws_access_key_id=amazon_credentials['ACCESS_KEY'],
                                   aws_secret_access_key=amazon_credentials['SECRET_KEY'],
                                   region_name=amazon_credentials['REGION'])

    def annotate_image(self, image):
        response = self.client.detect_document_text(Document={'Bytes': bytearray(image)})
        return response

    def process_output(self, outputs, img_width, img_height):
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
                identified.append({'content': text, 'coords': top_left + bottom_right})
        
        return identified
