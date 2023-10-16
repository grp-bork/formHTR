from libs.services.amazon_vision import AmazonVision
from libs.services.azure_vision import AzureVision
from libs.services.google_vision import GoogleVision


def call_services(logsheet_image, credentials):
    google = GoogleVision(credentials['google'])
    amazon = AmazonVision(credentials['amazon'])
    azure = AzureVision(credentials('azure'))

    print("Calling google...")
    outputs = google.annotate_image(logsheet_image)
    google_indentified = google.process_output(outputs)
    print("done.")

    print("Calling amazon...")
    outputs = amazon.annotate_image(logsheet_image)
    amazon_indentified = amazon.process_output(outputs)
    print("done.")

    print("Calling azure...")
    outputs = azure.annotate_image(logsheet_image)
    azure_indentified = azure.process_output(outputs)
    print("done.")

    return {'google': google_indentified,
            'amazon': amazon_indentified,
            'azure': azure_indentified
           }
