from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time


class AzureVision:
    def __init__(self, azure_credentials):
        credentials = CognitiveServicesCredentials(azure_credentials['subscription_key'])
        self.client = ComputerVisionClient(endpoint=azure_credentials['endpoint'], credentials=credentials)

    def annotate_image(self, image):
        image_path = "temp_image.png"
        image.save(image_path, "PNG")
        
        with open(image_path, 'rb') as image_stream:
            # Use the stream to call the API
            rawHttpResponse = self.client.read_in_stream(image_stream, language="en", raw=True)
            # try lower DPI if Bad request (azure.cognitiveservices.vision.computervision.models._models_py3.ComputerVisionOcrErrorException)

        # Get ID from returned headers
        operationLocation = rawHttpResponse.headers["Operation-Location"]
        operationId = operationLocation.split("/")[-1]
        
        # SDK call
        result = self.client.get_read_result(operationId)

        while result.status != OperationStatusCodes.succeeded and result.status != OperationStatusCodes.failed:
            time.sleep(1)  # To avoid making too many requests in a short time
            result = self.client.get_read_result(operationId)

        return result

    def process_output(self, outputs):
        identified = []
        if outputs.status == OperationStatusCodes.succeeded:
            for line in outputs.analyze_result.read_results[0].lines:
                for word in line.words:
                    vertices = word.bounding_box
                    identified.append({'content': word.text, 'coords': vertices[0:2] + vertices[4:6]})
        return identified
