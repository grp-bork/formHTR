import argparse
import cv2
import numpy as np

from libs.extract_ROI.select_ROIs_widget import SelectROIsWidget
from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.extract_ROI.autodect import detect_rectangles, find_residuals
from libs.logsheet_config import LogsheetConfig
from libs.region import ROI
from libs.extract_ROI.cli_inputs import process_cli


def main(filename, autodetect, autodetect_filter, output_file, config_file, detect_residuals, credentials, display_residuals):
    """Convert given PDF to image, automatically detect rectangles (ROIs)
    and then allow to draw rectagles manually. Coordinates of all
    ROIs are then exported to a CSV file.

    Args:
        filename (str): input PDF
        autodetect (bool): apply automatic detection of ROIs
        autodetect_filter (float): scaling factor to filter out too small ROIs (recommended value between 1 and 3)
        output_file (str): output file for config
        config_file (str): input file with config
        detect_residuals (bool): apply automatic detection of printed text to be ignored from the output
        credentials (dict): credentials for Google vision service
        display_residuals (bool): display residuals in the visualisation
    """
    image = convert_pdf_to_image(filename)
    image = np.array(image)

    config = LogsheetConfig([], [])
    if config_file:
        config.import_from_json(config_file)
        image = resize_image(image, (config.width, config.height))
    else:
        rectangles = []
        residuals = []

        if autodetect:
            rectangles = detect_rectangles(image, autodetect_filter)
            rectangles = [ROI(*rectangle) for rectangle in rectangles]
        if detect_residuals:
            residuals = find_residuals(image, credentials)
            
        height, width, _ = image.shape
        config = LogsheetConfig(rectangles, residuals, height, width)

    ROIs_widget = SelectROIsWidget(image, config, display_residuals)

    process_cli(ROIs_widget)

    cv2.destroyAllWindows()
    ROIs_widget.config.export_to_json(output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Select ROIs in given PDF file.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_file', type=str, required=True, help='PDF template of a logsheet')
    required.add_argument('--output_file', type=str, required=True, help='Path to output JSON file containing config')

    optional.add_argument('--autodetect', action=argparse.BooleanOptionalAction, default=False, help='Apply autodetection algorithm to find ROIs automatically')
    optional.add_argument('--autodetect_filter', type=float, default=3, help='Autodetection parameter: scaling factor to filter out too small ROIs (recommended value between 1 and 3)')
    optional.add_argument('--config_file', type=str, default=None, help='Path to input JSON file containing config')
    optional.add_argument('--detect_residuals', action=argparse.BooleanOptionalAction, default=False, help='Find existing text in the template and flag it as residual (will be always ignored)')
    required.add_argument('--credentials', type=str, help='Path to Google vision credentials')
    optional.add_argument('--display_residuals', action=argparse.BooleanOptionalAction, default=False, help='Display found residuals.')

    args = args_parser.parse_args()

    print(vars(args))
    if args.detect_residuals and not args.credentials:
        args_parser.error('The --detect_residuals argument requires --credentials.')

    main(args.pdf_file, args.autodetect, args.autodetect_filter, args.output_file, args.config_file, args.detect_residuals, args.credentials, args.display_residuals)
