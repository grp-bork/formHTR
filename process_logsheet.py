import argparse
import numpy as np

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.logsheet_config import LogsheetConfig
from libs.processing.align_images import align_images
from libs.processing.read_content import process_content
from libs.processing.store_results import store_results
from libs.services.call_services import call_services
from libs.visualise_regions import annotate_pdfs


def preprocess_input(scanned_logsheet, template, config):
    # convert pdfs to images
    template_image = convert_pdf_to_image(template)
    template_image = np.array(template_image)

    logsheet_image = convert_pdf_to_image(scanned_logsheet)
    logsheet_image = np.array(logsheet_image)

    # resize images
    logsheet_image = resize_image(logsheet_image, (config.width, config.height))
    template_image = resize_image(template_image, (config.width, config.height))

    # fix logsheet_image (reorient and scale)
    logsheet_image = align_images(logsheet_image, template_image) #, debug=True)
    return logsheet_image


def main(scanned_logsheet, template, config_file, output_file, google_credentials, amazon_credentials, azure_credentials, debug):
    # load CSV config
    config = LogsheetConfig()
    config.import_from_json(config_file)
    # assume PDF and CSV config correspond to each other (QR codes are not reliable anyway)
    logsheet_image = preprocess_input(scanned_logsheet, template, config)
    # call external OCR services
    credentials = {'google': google_credentials, 'amazon': amazon_credentials, 'azure': azure_credentials}
    indetified_content = call_services(logsheet_image, credentials)

    if debug:
        annotate_pdfs(indetified_content, logsheet_image)
    # process contents
    contents = process_content(indetified_content, logsheet_image, config)
    # store to Excel sheet
    store_results(contents, output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Select ROIs in given PDF file.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_logsheet', type=str, required=True, help='Scanned logsheet in PDF format')
    required.add_argument('--pdf_template', type=str, required=True, help='PDF template of the logsheet')
    required.add_argument('--config_file', type=str, required=True, help='Path to CSV file containing config')
    required.add_argument('--output_file', type=str, required=True, help='Path to output xlsx file')

    required.add_argument('--google', type=str, required=True, help='Path to Google vision credentials')
    required.add_argument('--amazon', type=str, required=True, help='Path to Amazon vision credentials')
    required.add_argument('--azure', type=str, required=True, help='Path to Azure vision credentials')

    optional.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False, help='Run in debug mode')

    args = args_parser.parse_args()

    main(args.pdf_logsheet, args.pdf_template, args.config_file, args.output_file, args.google, args.amazon, args.azure, args.debug)
