import argparse
import numpy as np

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.logsheet_config import LogsheetConfig
from libs.processing.align_images import align_images
from libs.processing.read_content import process_content
from libs.processing.store_results import store_results
from libs.visualise_regions import annotate_pdfs

from libs.region import Rectangle
from tests.extracted_content import EXTRACTED


def load_stored_results(test_set):
    google_identified = []
    for rect in EXTRACTED[test_set]['REGIONS_GOOGLE']:
        google_identified.append(Rectangle(*rect['coords'], rect['content']))

    amazon_identified = []
    for rect in EXTRACTED[test_set]['REGIONS_AMAZON']:
        amazon_identified.append(Rectangle(*rect['coords'], rect['content']))

    azure_identified = []
    for rect in EXTRACTED[test_set]['REGIONS_AZURE']:
        azure_identified.append(Rectangle(*rect['coords'], rect['content']))
    
    return {'google': google_identified,
            'amazon': amazon_identified,
            'azure': azure_identified
           }


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


def process_logsheet(logsheet, template, config_file, test_set, debug=False, front=True):
    # load CSV config
    config = LogsheetConfig([], [])
    config.import_from_json(config_file)

    page = 0 if front else 1

    # assume PDF and CSV config correspond to each other (QR codes are not reliable anyway)
    logsheet_image = preprocess_input(logsheet, template, config, page)
    # call external OCR services
    test_set = test_set + '_back' if not front else test_set
    identified_content = load_stored_results(test_set)

    if debug:
        annotate_pdfs(identified_content, logsheet_image, front)

    # process contents
    return process_content(identified_content, logsheet_image, config)


def main(scanned_logsheet, template, config_file, output_file, test_set, 
         debug, backside, backside_template, backside_config):
    
    # extract contents from the front page
    contents, artefacts = process_logsheet(scanned_logsheet, template, config_file, test_set, debug=debug)

    # extract contents from the back side (if present)
    if backside:
        contents_back, artefacts_back = process_logsheet(scanned_logsheet, backside_template, backside_config, test_set, debug=debug, front=False)

        # join results
        contents += contents_back
        for key in artefacts.keys():
            artefacts[key] = artefacts[key] + artefacts_back[key]

    # store to Excel sheet
    store_results(contents, artefacts, output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Dry run of logsheet processing.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_logsheet', type=str, required=True, help='Scanned logsheet in PDF format')
    required.add_argument('--pdf_template', type=str, required=True, help='PDF template of the logsheet')
    required.add_argument('--config_file', type=str, required=True, help='Path to JSON file containing config')
    required.add_argument('--output_file', type=str, required=True, help='Path to output xlsx file')
    required.add_argument('--test_set', type=str, required=True, help='TARA or CTD')

    optional.add_argument('--debug', action=argparse.BooleanOptionalAction, default=False, help='Run in debug mode')
    optional.add_argument('--backside', action=argparse.BooleanOptionalAction, default=False, help='Backside page present.')
    optional.add_argument('--backside_template', type=str, help='PDF template of the backside')
    optional.add_argument('--backside_config', type=str, help='Path to JSON file containing config of the backside')

    args = args_parser.parse_args()

    main(args.pdf_logsheet, args.pdf_template, args.config_file, args.output_file, args.test_set,
         args.debug, args.backside, args.backside_template, args.backside_config)
