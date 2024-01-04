import cv2
import numpy as np

from libs.pdf_to_image import convert_pdf_to_image
from libs.processing.align_images import compute_closest_point


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
        cv2.imshow("Select Points", image)
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

def align_images(template, target, template_points, target_points):
    template_points = np.float32(template_points)
    target_points = np.float32(target_points)

    matrix = cv2.getPerspectiveTransform(target_points, template_points)
    result = cv2.warpPerspective(target, matrix, (template.shape[1], template.shape[0]))

    return result

def main(template_path, target_path, output_path):
    # Convert PDF images to OpenCV format
    template = np.array(convert_pdf_to_image(template_path))
    target = np.array(convert_pdf_to_image(target_path))

    # Display and select points on the template image
    template_points = select_points(template.copy())
    print(template_points)

    # Display and select points on the target image
    target_points = select_points(target.copy())
    print(target_points)

    # TODO sort by finding closest points to corners
    # compute_closest_point

    # Align the images based on the selected points
    aligned_image = align_images(template, target, template_points, target_points)

    # TODO store as pdf
    # Save the aligned image to the output file
    cv2.imwrite(output_path, aligned_image)

if __name__ == "__main__":
    import sys

    # TODO make proper interface
    # dont touch other pages if present? (backside)

    if len(sys.argv) != 4:
        print("Usage: python manual_alignment_tool.py template.pdf target.pdf output.jpg")
        sys.exit(1)

    template_path, target_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    main(template_path, target_path, output_path)
