from pdf2image import convert_from_path
import cv2


def convert_pdf_to_image(pdf_path, page=0):
    """
    Convert PDF to image (assume only one page).

    Args:
        pdf_path (str): path to given PDF file
        page (int): page number to be extracted. Defaults to 0.

    Returns:
        Image: converted image
    """
    return convert_from_path(pdf_path, dpi=300)[page]


def resize_image(image, size):
    """
    Resize image to given size.

    Args:
        image (Image): image object
        size ((int, int)): Provide pair of dimentions to scale the image.

    Returns:
        Image: scaled image
    """
    return cv2.resize(image, size, interpolation = cv2.INTER_AREA)
