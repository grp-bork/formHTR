import argparse
import cv2
import numpy as np

from libs.annotate_ROI.annotate_ROIs_widget import AnnotateROIsWidget
from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.logsheet_config import LogsheetConfig
from libs.annotate_ROI.cli_inputs import process_cli


def process_inputs(filename, config_file, display_residuals):
    image = convert_pdf_to_image(filename)
    image = np.array(image)

    config = LogsheetConfig([], [])
    config.import_from_json(config_file)

    image = resize_image(image, (config.width, config.height))
        
    return AnnotateROIsWidget(image, config, display_residuals)


def main(filename, config_file, output_file, remove_unannotated, display_residuals):
    annotate_ROIs_widget = process_inputs(filename, config_file, display_residuals)

    process_cli(annotate_ROIs_widget)

    cv2.destroyAllWindows()
    annotate_ROIs_widget.config.export_to_json(output_file, remove_unannotated)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Annotate ROIs in given PDF file.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_file', type=str, required=True, help='PDF template of a logsheet')
    required.add_argument('--config_file', type=str, required=True, help='Path to input JSON file containing config')
    required.add_argument('--output_file', type=str, required=True, help='Path to output JSON file containing config')

    optional.add_argument('--remove_unannotated', action=argparse.BooleanOptionalAction, default=False, help='ROIs with no annotation are removed from the output config file.')
    optional.add_argument('--display_residuals', action=argparse.BooleanOptionalAction, default=False, help='Display read-only residuals.')

    args = args_parser.parse_args()

    main(args.pdf_file, args.config_file, args.output_file, args.remove_unannotated, args.display_residuals)
