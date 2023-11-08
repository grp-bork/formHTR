import os
import cv2
import xlsxwriter
from shutil import rmtree


def order_results(values):
    output = []
    for key in ['inferred', 'google', 'amazon', 'azure']:
        value = values.get(key, None)
        if value:
            output.append(value)
    return output


def write_header(worksheet):
    worksheet.write('A1', 'Variable name')
    worksheet.write('B1', 'Extracted content')
    worksheet.write('C1', 'Cropped image')


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


def store_results(results, artefacts, output_file):
    """
    Write identified results into an Excel sheet

    Args:
        results (list): identified results
        artefacts (dict): identified artefacts per service 
        output_file (str): path to the output xlsx file
    """
    # create directory to store mini images
    directory = os.path.dirname(output_file)
    images_directory = os.path.join(directory, 'images')

    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

    # create a new Excel file and add a worksheet
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet('Metadata')
    write_header(worksheet)

    max_width = 0

    # fill in data
    for row_number, result in enumerate(results, 2):
        worksheet.write(f'A{row_number}', result[0])
        values = order_results(result[1])
        if len(values) > 1:
            worksheet.data_validation(f'B{row_number}', {'validate': 'list', 'show_error': False, 'source': values})

        inferred = result[1].get('inferred', None)
        if inferred is None and len(values) != 0:
            inferred = values[0]

        worksheet.write(f'B{row_number}', inferred)

        filename = store_image(result[2], images_directory, row_number)
        height, width, _ = result[2].shape
        max_width = max(width, max_width)
        worksheet.insert_image(f'C{row_number}', filename)
        worksheet.set_row_pixels(row_number-1, height)

    worksheet.set_column_pixels(2, 3, max_width)
    worksheet.autofit()

    max_width = 0

    # add extra identified content
    extra_worksheet = workbook.add_worksheet('Extra')
    row_number = 1
    for key in artefacts.keys():
        if len(artefacts[key]) != 0:
            extra_worksheet.write(f'A{row_number}', key)
            row_number += 1
            for extra in artefacts[key]:
                extra_worksheet.write(f'A{row_number}', extra[0])

                filename = store_image(extra[1], images_directory, row_number+1000)
                height, width, _ = extra[1].shape
                max_width = max(width, max_width)
                extra_worksheet.insert_image(f'B{row_number}', filename)
                extra_worksheet.set_row_pixels(row_number-1, height)
                row_number += 1
            row_number += 1
    
    extra_worksheet.set_column_pixels(1, 2, max_width)
    extra_worksheet.autofit()

    workbook.close()
    rmtree(images_directory)
