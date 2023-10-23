from libs.processing.rtree import Ensemble
from libs.processing.barcode import read_barcode
from libs.processing.process_area import check_barcode_area, general_text_area
from libs.processing.checkbox import is_ticked


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
            # TODO use barcode value from OCR if everything else fails
            valid_content = check_barcode_area(candidates)
            if valid_content:
                content = read_barcode(fragment)
        elif region.content_type == 'Checkbox':
            content = is_ticked(fragment)
            # TODO remove from the tree whatever was found there
            # perhaps if it was proper text, store it
            pass
        else:
            content = general_text_area(candidates, region)

        results.append([region.varname, content, fragment])

    # TODO: in the end investigate what remained in the trees
            
    return results
