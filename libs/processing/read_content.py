from libs.processing.rtree import Ensemble
from libs.processing.barcode import read_barcode
from libs.processing.process_area import check_barcode_area, general_text_area


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

    ensemble = Ensemble(indetified_content, config)

    for region in config.regions:
        fragment = logsheet_image[region.start_y:region.end_y, region.start_x:region.end_x]
        content = None

        candidates = ensemble.find_intersection(region.get_coords())
        
        if region.content_type == 'Barcode':
            valid_content = check_barcode_area(candidates)
            if valid_content:
                content = read_barcode(fragment)
        elif region.content_type == 'Checkbox':
            # TODO check percentage pixel content in the region
            # remove from the tree whatever was found there
            # perhaps if it was proper text, store it
            pass
        else:
            content = general_text_area(candidates)

        results.append([region.varname, fragment, content])

    # TODO: in the end investigate what remained in the trees
            
    return results
