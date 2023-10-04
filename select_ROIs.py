import argparse
import cv2
from pathlib import Path
import numpy as np

from libs.extract_ROI.select_ROIs_widget import SelectROIsWidget
from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.extract_ROI.autodect import detect_rectangles
from libs.logsheet_config import LogsheetConfig
from libs.extract_ROI.cli_inputs import process_cli


def process_inputs(filename, autodetect, autodetect_filter, config_file):
    image = convert_pdf_to_image(filename)
    image = np.array(image)
    
    config = LogsheetConfig()

    if config_file:
        config.import_from_csv(config_file)
        image = resize_image(image, (config.width, config.height))
    else:
        rectangles = []
        if autodetect:
            rectangles = detect_rectangles(image, autodetect_filter)
        height, width, _ = image.shape
        config.set_attributes(rectangles, Path(filename).stem + '.csv', height, width)

    return SelectROIsWidget(image, config)


def main(filename, autodetect, autodetect_filter, output_file, config_file):
    """
    Convert given PDF to image, automatically detect rectangles (ROIs)
    and then allow to draw rectagles manually. Coordinates of all
    ROIs are then exported to a CSV file.

    Args:
        filename (str): input PDF
        autodetect (bool): apply automatic detection of ROIs
        autodetect_filter (float): scaling factor to filter out too small ROIs (recommended value between 1 and 3)
    """
    ROIs_widget = process_inputs(filename, autodetect, autodetect_filter, config_file)

    process_cli(ROIs_widget)

    cv2.destroyAllWindows()
    ROIs_widget.config.export_to_csv(output_file)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Select ROIs in given PDF file.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_file', type=str, required=True, help='PDF template of a logsheet')
    required.add_argument('--output_file', type=str, required=True, help='Path to output CSV file containing config')

    optional.add_argument('--autodetect', action=argparse.BooleanOptionalAction, default=False, help='Apply autodetection algorithm to find ROIs automatically')
    optional.add_argument('--autodetect_filter', type=float, default=3, help='Autodetection parameter: scaling factor to filter out too small ROIs (recommended value between 1 and 3)')
    optional.add_argument('--config_file', type=str, default=None, help='Path to input CSV file containing config')

    args = args_parser.parse_args()

    main(args.pdf_file, args.autodetect, args.autodetect_filter, args.output_file, args.config_file)
