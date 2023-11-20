from pdf2image import convert_from_path
import cv2
from io import BytesIO
from PIL import Image


def convert_pdf_to_image(pdf_path, page=0, dpi=300):
    """
    Convert PDF to image (assume only one page).

    Args:
        pdf_path (str): path to given PDF file
        page (int): page number to be extracted. Defaults to 0.
        dpi (int): quality of picture in DPI. Defaults to 300.

    Returns:
        Image: converted image
    """
    return convert_from_path(pdf_path, dpi=dpi)[page]


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


def get_image_size(logsheet_image):
    """Find the size of the image

    Args:
        logsheet_image (np.array): image of interest

    Returns:
        int: size in bytes
    """
    img_file = BytesIO()
    image = Image.fromarray(logsheet_image)
    image.save(img_file, 'png', quality='keep')
    return img_file.tell()
