from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models._models_py3 import ComputerVisionOcrErrorException
import time

from libs.region import Rectangle
from libs.services.utils import extract_corners


class AzureVision:
    def __init__(self, azure_credentials):
        credentials = CognitiveServicesCredentials(azure_credentials['SUBSCRIPTION_KEY'])
        self.client = ComputerVisionClient(endpoint=azure_credentials['ENDPOINT'], credentials=credentials)

    def annotate_image(self, image_stream):
        image_stream.seek(0)  # Rewind the stream to the beginning

        try:
            rawHttpResponse = self.client.read_in_stream(image_stream, language='en', raw=True)
        except ComputerVisionOcrErrorException as e:
            print(f'AzureVision error: {e.error}')
            # TODO # try lower DPI
            return []

        # Get ID from returned headers
        operationLocation = rawHttpResponse.headers['Operation-Location']
        operationId = operationLocation.split('/')[-1]
        
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
                    start, end = extract_corners([vertices[0:2], vertices[4:6]])
                    identified.append(Rectangle(*start, *end, word.text))
        return identified
