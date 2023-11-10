def is_approximately_square(top_left_x, top_left_y, bottom_right_x, bottom_right_y, max_width, max_height, error_percentage=1.0):
    """Check whether provided rectangle is a square

    Args:
        top_left_x (float): top left corner x-coordinate
        top_left_y (float): top left corner y-coordinate
        bottom_right_x (float): bottom right corner x-coordinate
        bottom_right_y (float): bottom right corner y-coordinate
        max_width (int): page width
        max_height (int): page height
        error_percentage (float, optional): allow error. Defaults to 1.0.

    Returns:
        bool: True if it is a square
    """
    # Calculate width and height of the rectangle
    width = abs(bottom_right_x - top_left_x)
    height = abs(bottom_right_y - top_left_y)

    # Calculate the margin of error
    margin_of_error = min(max_width, max_height) * (error_percentage / 100)

    # Check if width and height are approximately equal within the margin of error
    return abs(width - height) <= margin_of_error
