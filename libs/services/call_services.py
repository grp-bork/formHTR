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
    image_pil.save(image_stream, format='JPEG')

    google_identified = google.annotate_image(image_stream)
    google_identified = google.process_output(google_identified)

    amazon_identified = amazon.annotate_image(image_stream)
    amazon_identified = amazon.process_output(amazon_identified, config.width, config.height)

    azure_identified = azure.annotate_image(image_stream)
    if azure_identified:
        azure_identified = azure.process_output(azure_identified)

    return {'google': google_identified,
            'amazon': amazon_identified,
            'azure': azure_identified
           }
