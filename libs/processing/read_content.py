from libs.processing.rtree import RectangleTree
from libs.processing.barcode import read_barcode


def process_content(indetified_content, logsheet_image, config):
    """
    Top level function to read content of ROIs.

    Args:
        indetified_content (dict): identified content using OCR services
        logsheet_image (Image): logsheet image
        config (LogsheetConfig): configuration of given logsheet

    Returns:
        list: a list of identified content with its confidence
    """
    results = []

    google_rtree = RectangleTree(indetified_content['google'])
    amazon_rtree = RectangleTree(indetified_content['amazon'])
    azure_rtree = RectangleTree(indetified_content['azure'])

    for region in config.regions:
        fragment = logsheet_image[region.start_y:region.end_y, region.start_x:region.end_x]
        content = None
        
        if region.content_type == 'Barcode':
            # TODO: check whether there is only one hit in the region
            # remove from the tree
            content = read_barcode(fragment)
        elif region.content_type == 'Checkbox':
            # TODO check percentage pixel content in the region
            # remove from the tree whatever was found there
            # perhaps if it was proper text, store it
            pass
        else:
            # TODO: find intersections and remove from the tree
            pass

        results.append([region.varname, fragment, content])

    # TODO: in the end investigate what remained in the trees
            
    return results
