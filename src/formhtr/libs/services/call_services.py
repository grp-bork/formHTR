import io

from PIL import Image
from .amazon_vision import AmazonVision
from .azure_vision import AzureVision
from .google_vision import GoogleVision


def call_services(logsheet_image, credentials, config):
    google = GoogleVision(credentials['google']) if credentials['google'] else None
    amazon = AmazonVision(credentials['amazon']) if credentials['amazon'] else None
    azure = AzureVision(credentials['azure']) if credentials['azure'] else None

    image_pil = Image.fromarray(logsheet_image)
    image_stream = io.BytesIO()
    image_pil.save(image_stream, format='JPEG')

    google_identified = google.annotate_image(image_stream) if google else None
    google_identified = google.process_output(google_identified) if google_identified else None

    amazon_identified = amazon.annotate_image(image_stream) if amazon else None
    amazon_identified = amazon.process_output(amazon_identified, config.width, config.height) if amazon_identified else None
    
    azure_identified = azure.annotate_image(image_stream) if azure else None
    azure_identified = azure.process_output(azure_identified) if azure_identified else None

    return {'google': google_identified,
            'amazon': amazon_identified,
            'azure': azure_identified
           }
