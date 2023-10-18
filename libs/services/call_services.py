from PIL import Image
import io

from libs.services.amazon_vision import AmazonVision
from libs.services.azure_vision import AzureVision
from libs.services.google_vision import GoogleVision


def call_services(logsheet_image, credentials, config):
    google = GoogleVision(credentials['google'])
    amazon = AmazonVision(credentials['amazon'])
    azure = AzureVision(credentials['azure'])

    image_pil = Image.fromarray(logsheet_image)
    image_stream = io.BytesIO()
    image_pil.save(image_stream, format='PNG')

    outputs = google.annotate_image(image_stream)
    google_identified = google.process_output(outputs)

    outputs = amazon.annotate_image(image_stream)
    amazon_identified = amazon.process_output(outputs, config.width, config.height)

    outputs = azure.annotate_image(image_stream)
    azure_identified = azure.process_output(outputs)

    return {'google': google_identified,
            'amazon': amazon_identified,
            'azure': azure_identified
           }
