from .rtree import Ensemble
from .barcode import read_barcode
from .process_area import general_text_area
from .checkbox import is_ticked


def process_content(indetified_content, logsheet_image, config, checkbox_edges):
    """Fill each configured ROI using OCR unions, barcodes, or checkbox heuristics.

    Args:
        indetified_content: Dict ``google`` / ``amazon`` / ``azure`` -> word lists or ``None``.
        logsheet_image: Full-page aligned image as ``numpy`` array.
        config: ``LogsheetConfig`` with ``regions`` and ``residuals``.
        checkbox_edges: Fraction of ROI border to ignore when scoring checkbox ink.

    Returns:
        ``(results, artefacts)`` where ``results`` is a list of
        ``[varname, content_dict, fragment]`` and ``artefacts`` maps each service
        to leftover OCR snippets not assigned to ROIs.
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
            content['inferred'] = is_ticked(fragment, edge_ignore_percentage=checkbox_edges)
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
