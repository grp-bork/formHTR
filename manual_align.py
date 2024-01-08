import cv2
import numpy as np
import argparse
from PyPDF2 import PdfReader, PdfWriter
import img2pdf
from PIL import Image
import io

from libs.pdf_to_image import convert_pdf_to_image, resize_image
from libs.processing.align_images import compute_closest_point, transform


def select_points(image, window_name):
    original_image = image.copy()
    points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) < 4:
                points.append((x,y))
                cv2.circle(image, (x,y), 15, (0, 0, 255), -1)
                cv2.imshow(window_name, image)

    keep_running = True
    while keep_running:
        cv2.imshow(window_name, image)
        cv2.setMouseCallback(window_name, click_event)
        key = cv2.waitKey(0)

        if key == ord('r') and points:
            points.pop()  # undo the last point
            image = original_image.copy()
            for (x,y) in points:
                cv2.circle(image, (x,y), 15, (0, 0, 255), -1)
            cv2.imshow(window_name, image)
        elif key in [27, ord('q')]: # Esc or q key to exit 
            cv2.destroyAllWindows()
            keep_running = False

    cv2.destroyAllWindows()
    return points


def to_pdf(image):
    image_pil = Image.fromarray(image)
    image_bytes = io.BytesIO()
    image_pil.save(image_bytes, format='JPEG')
    return img2pdf.convert(image_bytes.getvalue())


def process(target, template, backside=False):
    height, width, _ = target.shape

    target = resize_image(target, (width, height))
    template = resize_image(template, (width, height))

    # Display and select points on the template image
    window_name = 'TEMPLATE' + '(backside)' if backside else 'TEMPLATE'
    template_points = select_points(template.copy(), window_name)
    # template_points = [(29, 233), (2218, 236), (30, 3074), (2213, 3084)]

    # sort by finding closest points to corners
    template_points = [compute_closest_point((0, 0), template_points),
                       compute_closest_point((width, 0), template_points),
                       compute_closest_point((width, height), template_points),
                       compute_closest_point((0, height), template_points)]

    # Display and select points on the target image
    window_name =  'SCAN' + '(backside)' if backside else 'SCAN'
    target_points = select_points(target.copy(), window_name)
    # target_points = [(149, 322), (2435, 338), (107, 3270), (2396, 3306)]

    target_points = [compute_closest_point((0, 0), target_points),
                     compute_closest_point((width, 0), target_points),
                     compute_closest_point((width, height), target_points),
                     compute_closest_point((0, height), target_points)]

    # Align the images based on the selected points
    return transform(target, template, target_points, template_points)


def main(template_path, target_path, output_path, backside_template):
    output_pdf_writer = PdfWriter()

    # Convert PDF images to OpenCV format
    template = np.array(convert_pdf_to_image(template_path))
    target = np.array(convert_pdf_to_image(target_path))

    aligned_frontside = process(target, template)

    frontside_pdf = to_pdf(aligned_frontside)
    frontside_pdf_reader = PdfReader(io.BytesIO(frontside_pdf))
    output_pdf_writer.add_page(frontside_pdf_reader.pages[0])

    if backside_template:
        template = np.array(convert_pdf_to_image(backside_template))
        target = np.array(convert_pdf_to_image(target_path, page=1))

        aligned_backside = process(target, template, backside=True)
        backside_pdf = to_pdf(aligned_backside)
        backside_pdf_reader = PdfReader(io.BytesIO(backside_pdf))
        output_pdf_writer.add_page(backside_pdf_reader.pages[0])
    else:
        original_pdf = PdfReader(target_path)
        output_pdf_writer.add_page(original_pdf.pages[1])

    # Save the aligned image to the output file
    with open(output_path, 'wb') as output_pdf:
        output_pdf_writer.write(output_pdf)


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
