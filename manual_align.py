import cv2
import numpy as np
import argparse

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.processing.align_images import compute_closest_point, transform


def select_points(image):
    points = []

    def click_event(event, x, y, flags, params):
        # TODO dont allow to draw if len(points) > 3
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x,y))
            cv2.circle(image, (x,y), 15, (0, 0, 255), -1)
            cv2.imshow('Select Points', image)

    while len(points) < 4:
        # TODO end only on q or Esc
        cv2.imshow('Select Points', image)
        cv2.setMouseCallback('Select Points', click_event)
        key = cv2.waitKey(0)

        if key == ord('q'):
            break
        elif key == ord('r') and points:
            points.pop()  # undo the last point
            # TODO remove also from the image
        elif key == 27:  # Esc key to exit 
            # TODO join with q
            cv2.destroyAllWindows()
            exit()

    cv2.destroyAllWindows()
    return points

def store_output():
    pass


def process(target, template):
    height, width, _ = target.shape

    target = resize_image(target, (width, height))
    template = resize_image(template, (width, height))

    # Display and select points on the template image
    template_points = select_points(template.copy())
    # template_points = [(29, 233), (2218, 236), (30, 3074), (2213, 3084)]

    # sort by finding closest points to corners
    template_points = [compute_closest_point((0, 0), template_points),
                       compute_closest_point((width, 0), template_points),
                       compute_closest_point((width, height), template_points),
                       compute_closest_point((0, height), template_points)]

    # Display and select points on the target image
    target_points = select_points(target.copy())
    # target_points = [(149, 322), (2435, 338), (107, 3270), (2396, 3306)]

    target_points = [compute_closest_point((0, 0), target_points),
                     compute_closest_point((width, 0), target_points),
                     compute_closest_point((width, height), target_points),
                     compute_closest_point((0, height), target_points)]

    # Align the images based on the selected points
    return transform(target, template, target_points, template_points)


def main(template_path, target_path, output_path, backside_template):
    # Convert PDF images to OpenCV format
    # TODO dont touch other pages if present? (backside)
    template = np.array(convert_pdf_to_image(template_path))
    target = np.array(convert_pdf_to_image(target_path))

    aligned_image = process(template, target)

    # TODO store as pdf
    # Save the aligned image to the output file
    cv2.imwrite(output_path, aligned_image)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Manual alignment tool for PDF files')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')
    optional = args_parser.add_argument_group('optional arguments')

    required.add_argument('--pdf_template', type=str, required=True, help='Path to the template PDF file')
    required.add_argument('--pdf_logsheet', type=str, required=True, help='Path to the target PDF file')
    required.add_argument('--output', type=str, required=True, help='Path to the output aligned image file')

    optional.add_argument('--backside_template', type=str, help='PDF template of the backside')

    args = args_parser.parse_args()
    main(args.pdf_template, args.pdf_logsheet, args.output, args.backside_template)
