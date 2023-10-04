from easyocr import Reader


def read_content(image, config):
    """
    Top level function to read content of ROIs.

    Args:
        image (Image): given image
        config (LogsheetConfig): configuration of given logsheet

    Returns:
        list: a list of identified content with its confidence
    """
    reader = Reader(['en'], True)
    results = []

    for region in config.regions:
        fragment = image[region.start_y:region.end_y, region.start_x:region.end_x]
        result = reader.readtext(fragment)

        content = ""
        probability = 1

        if result:
            content = result[0][1]
            probability = round(result[0][2], 2)
        
        results.append([region.varname, fragment, content, probability])

    return results
