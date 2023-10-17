from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time

from libs.logsheet_config import Rectangle


class AzureVision:
    def __init__(self, azure_credentials):
        credentials = CognitiveServicesCredentials(azure_credentials['SUBSCRIPTION_KEY'])
        self.client = ComputerVisionClient(endpoint=azure_credentials['ENDPOINT'], credentials=credentials)

    def annotate_image(self, image_stream):
        image_stream.seek(0)  # Rewind the stream to the beginning

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
                    identified.append(Rectangle(*vertices[0:2], *vertices[4:6], word.text))
        return identified
