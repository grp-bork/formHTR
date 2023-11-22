def extract_corners(points):
    """Identify bounding box for given polygon

    Args:
        points (list): list of coordinates

    Returns:
        list: top-left and bottom-right coordinates
    """
    min_x = min(points, key=lambda pt: pt[0])[0]
    min_y = min(points, key=lambda pt: pt[1])[1]
    max_x = max(points, key=lambda pt: pt[0])[0]
    max_y = max(points, key=lambda pt: pt[1])[1]
    
    return (min_x, min_y), (max_x, max_y)
