from libs.processing.rtree import RectangleTree


def check_barcode_area(candidates):
    """Check content of barcode

    Make sure there is at most one object and 
    at least one service found something

    Args:
        candidates (list): list of intersected rectangles

    Returns:
        bool: True if area is ok
    """
    sums = [len(item) for item in candidates]
    return all([i <= 1 for i in sums]) and sum(sums) >= 1


def words_to_line(candidates):
    # use Rectangle.is_left
    pass

def general_text_area(candidates):
    rtree_0 = RectangleTree(candidates[0])
    rtree_1 = RectangleTree(candidates[1])
    rtree_2 = RectangleTree(candidates[2])

    intersection = rtree_0 and rtree_1 and rtree_2
