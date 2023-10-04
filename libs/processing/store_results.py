import os
import cv2
import xlsxwriter
from shutil import rmtree


def write_header(worksheet):
    worksheet.write(0, 0, 'Variable name')
    worksheet.write(0, 1, 'Extracted content')
    worksheet.write(0, 2, 'Probability')
    worksheet.write(0, 3, 'Cropped image')

def store_image(image, location, index):
    """
    Temporarily store image

    Args:
        image (Image): image to be stored
        location (str): directory where to store the image
        index (int): unique identifier of the image

    Returns:
        _type_: filename of stored image
    """
    filename = f'{location}/cropped_image_{index}.png'
    cv2.imwrite(filename, image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    return filename

def store_results(results, output_file):
    """
    Write identified results into an Excel sheet

    Args:
        results (list): identified results
        output_file (str): path to the output xlsx file
    """
    # create directory to store mini images
    directory = os.path.dirname(output_file)
    images_directory = os.path.join(directory, 'images')

    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    # create a new Excel file and add a worksheet
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet('Data')
    write_header(worksheet)

    max_width = 0

    for row_number, result in enumerate(results, 1):
        worksheet.write(row_number, 0, result[0])
        worksheet.write(row_number, 1, result[2])
        worksheet.write(row_number, 2, result[3])
        filename = store_image(result[1], images_directory, row_number)
        height, width, _ = result[1].shape
        max_width = max(width, max_width)
        worksheet.insert_image(row_number, 3, filename)
        worksheet.set_row_pixels(row_number, height)

    worksheet.set_column_pixels(3, 3, max_width)

    worksheet.autofit()
    workbook.close()
    rmtree(images_directory)
