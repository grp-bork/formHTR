from libs.processing.rtree import Ensemble
from libs.processing.barcode import read_barcode
from libs.processing.process_area import general_text_area
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
    artefacts = dict()
    
    ensemble = Ensemble(indetified_content, config)

    for region in config.regions:
        fragment = logsheet_image[region.start_y:region.end_y, region.start_x:region.end_x]
        content = dict()

        candidates = ensemble.find_intersection(region.get_coords())
        
        if region.content_type == 'Barcode':
            content['inferred'] = read_barcode(fragment, candidates)
        elif region.content_type == 'Checkbox':
            content['inferred'] = is_ticked(fragment)
            # TODO remove from the tree whatever was found there
            # perhaps if it was proper text, store it
            pass
        else:
            is_number = region.content_type == 'Number'
            content = general_text_area(candidates, region, is_number)

        results.append([region.varname, content, fragment])
    
    for key, remaining in ensemble.filter_artefacts().items():
        artefacts[key] = []
        for rectangle in remaining:
            artefacts[key].append([rectangle.content, logsheet_image[int(rectangle.start_y):int(rectangle.end_y), 
                                                                     int(rectangle.start_x):int(rectangle.end_x)]])
    
    return results, artefacts
