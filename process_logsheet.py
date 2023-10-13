import argparse
import numpy as np

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.logsheet_config import LogsheetConfig
from libs.processing.align_images import align_images
from libs.processing.read_content import read_content
from libs.processing.store_results import store_results


def process_inputs(scanned_logsheet, template, config_file):
    # load CSV config
    config = LogsheetConfig()
    config.import_from_json(config_file)

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

    # read contents
    contents = read_content(logsheet_image, config)
    return contents


def main(scanned_logsheet, template, config_file, output_file):
    # assume PDF and CSV config correspond to each other (QR codes are not reliable anyway)
    contents = process_inputs(scanned_logsheet, template, config_file)
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

    args = args_parser.parse_args()

    main(args.pdf_logsheet, args.pdf_template, args.config_file, args.output_file)
