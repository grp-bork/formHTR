import argparse
import numpy as np
import json

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.logsheet_config import LogsheetConfig
from libs.processing.align_images import align_images
from libs.processing.read_content import process_content
from libs.processing.store_results import store_results
from libs.services.call_services import call_services
from libs.visualise_regions import annotate_pdfs


def load_credentials(google_credentials, amazon_credentials, azure_credentials):
    with open(amazon_credentials, 'r') as f:
        amazon_credentials = json.load(f)

    with open(azure_credentials, 'r') as f:
        azure_credentials = json.load(f)

    return {'google': google_credentials, 'amazon': amazon_credentials, 'azure': azure_credentials}

def preprocess_input(scanned_logsheet, template, config, page):
    # convert pdfs to images
    template_image = convert_pdf_to_image(template)
    template_image = np.array(template_image)

    logsheet_image = convert_pdf_to_image(scanned_logsheet, page)
    logsheet_image = np.array(logsheet_image)

    # resize images
    logsheet_image = resize_image(logsheet_image, (config.width, config.height))
    template_image = resize_image(template_image, (config.width, config.height))

    # fix logsheet_image (reorient and scale)
    logsheet_image = align_images(logsheet_image, template_image)
    return logsheet_image


def process_logsheet(logsheet, template, config_file, credentials, debug=False, front=True):
    # load CSV config
    config = LogsheetConfig([], [])
    config.import_from_json(config_file)

    page = 0 if front else 1

    # assume PDF and CSV config correspond to each other (QR codes are not reliable anyway)
    logsheet_image = preprocess_input(logsheet, template, config, page)
    # call external OCR services
    identified_content = call_services(logsheet_image, credentials, config)

    if debug:
        annotate_pdfs(identified_content, logsheet_image, front)

    # process contents
    return process_content(identified_content, logsheet_image, config)


def main(scanned_logsheet, template, config_file, output_file, google_credentials, amazon_credentials, azure_credentials, 
         debug, backside, backside_template, backside_config):
    
    credentials = load_credentials(google_credentials, amazon_credentials, azure_credentials)
    
    # extract contents from the front page
    contents, artefacts = process_logsheet(scanned_logsheet, template, config_file, credentials, debug=debug)

    # extract contents from the back side (if present)
    if backside:
        contents_back, artefacts_back = process_logsheet(scanned_logsheet, backside_template, backside_config, credentials, debug=debug, front=False)

        # join results
        contents += contents_back
        for key in artefacts.keys():
            artefacts[key] = artefacts[key] + artefacts_back[key]

    # store to Excel sheet
    store_results(contents, artefacts, output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Extract medatada from logsheet.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_logsheet', type=str, required=True, help='Scanned logsheet in PDF format')
    required.add_argument('--pdf_template', type=str, required=True, help='PDF template of the logsheet')
    required.add_argument('--config_file', type=str, required=True, help='Path to JSON file containing config')
    required.add_argument('--output_file', type=str, required=True, help='Path to output xlsx file')

    required.add_argument('--google', type=str, required=True, help='Path to Google vision credentials')
    required.add_argument('--amazon', type=str, required=True, help='Path to Amazon vision credentials')
    required.add_argument('--azure', type=str, required=True, help='Path to Azure vision credentials')

    optional.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False, help='Run in debug mode - output annotated PDF files.')
    optional.add_argument('--backside', action=argparse.BooleanOptionalAction, default=False, help='Backside page present.')
    optional.add_argument('--backside_template', type=str, help='PDF template of the backside')
    optional.add_argument('--backside_config', type=str, help='Path to JSON file containing config of the backside')

    args = args_parser.parse_args()

    if args.backside and (not args.backside_template or not args.backside_config):
        args_parser.error('The --backside argument requires --backside_template and --backside_config.')

    main(args.pdf_logsheet, args.pdf_template, args.config_file, args.output_file, args.google, args.amazon, args.azure, 
         args.debug, args.backside, args.backside_template, args.backside_config)
