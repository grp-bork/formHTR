from Bio import pairwise2
import numpy as np


def is_a_number(string):
    """Polish given string and check if can be converted to float.

    Args:
        string (str): given string possibly containing a float

    Returns:
        str: polished string
    """
    string = string.replace(" ", "")
    string = string.replace(",", ".")
    try:
        float(string)
    except ValueError:
        return None
    return string


def identify_number(values):
    """If some number were found, give them priority

    Otherwise we will handle the region is general text area

    Args:
        values (list): list of identified values

    Returns:
        str: identified number (as string for compatibility)
    """
    float_strings = [is_a_number(value) for value in values]
    filtered_items = list(filter(lambda item: item is not None, float_strings))
    if len(filtered_items) != 0:
        return max(set(filtered_items), key=filtered_items.count)


def separate_to_lines(rectangles):
    """Split set of rectangles into lines.

    This is determined by center of rectangle being inside of previous rectangle bounds.

    Args:
        rectangles (list): given list of rectangles

    Returns:
        list of list: list of rectangles grouped to lines
    """
    rectangles.sort(key=lambda rectangle: rectangle.center_y)
    average_height = np.mean([rectangle.height for rectangle in rectangles])
    line_break_threshold = average_height * 0.5

    # Step 3: Group coordinates into lines
    lines = []
    current_line = []
    previous_y = rectangles[0].center_y

    for rectangle in rectangles:
        if abs(rectangle.center_y - previous_y) > line_break_threshold:
            # A line break is detected
            lines.append(current_line)
            current_line = []
        
        current_line.append(rectangle)
        previous_y = rectangle.center_y  # Update previous_y to the bottom of the current word

    # Don't forget to add the last line if it's not empty
    if current_line:
        lines.append(current_line)

    return lines


def get_max_dimensions(candidates):
    """Identify dimensions of identified text
    used to determine its size

    Args:
        candidates (list): identified lines of rectangles

    Returns:
        tuple: pair of values
    """
    max_words = 0
    max_lines = 0

    for candidate in candidates.values():
        max_lines = max(max_lines, len(candidate))
        for line in candidate:
            max_words = max(max_words, len(line))

    return max_words, max_lines


def construct_lines(lines):
    return '\n'.join([' '.join([rectangle.content for rectangle in line]) for line in lines])


def align_pairwise(string_1, string_2):
    """Align two strings

    Args:
        string_1 (str): first string
        string_2 (str): second string

    Returns:
        str: aligned string
    """
    alignments = pairwise2.align.globalxs(string_1, string_2, -3, -1, gap_char=' ')
    return alignments[0][0]


def majority_vote(strings):
    """Vote on individual positions of identified words

    Args:
        strings (list): list of words (per service) corresponding to a line

    Returns:
        list: most probable list of words
    """
    # Pad strings to the same length
    max_length = max(len(s) for s in strings)
    padded_strings = [s.ljust(max_length) for s in strings]

    # Compute the majority-voted string
    result = []
    for chars in zip(*padded_strings):
        # Count occurrences of each character
        count = {}
        for char in chars:
            count[char] = count.get(char, 0) + 1
        
        # Get the character with maximum occurrence
        voted_char = max(count, key=count.get)
        result.append(voted_char)

    return ''.join(result)


def remove_non_ascii(string):
    """Remove non-ascii characters (these do not work in the alignment)

    Args:
        string (str): input line

    Returns:
        str: line containing only ascii characters
    """
    return ''.join(char for char in string if ord(char) < 128)


def identify_words(lines, is_number):
    """Identify words from lines.
    Behaves differently based on how many lines there are.

    Args:
        lines (list): given list of lines as strings
        is_number (bool): True if number(s) is/are expected

    Returns:
        str: identified word
    """
    # curate lines
    lines = list(filter(None, lines))
    lines = list(map(remove_non_ascii, lines))

    if len(lines) == 1:
        return lines[0]
    elif len(lines) == 2:
        values = [align_pairwise(lines[0], lines[1]), 
                  align_pairwise(lines[1], lines[0])]
        if is_number:
            number = identify_number(values)
            if number is not None:
                return number
        return majority_vote(values)
    elif len(lines) == 3:
        values = []
        for i in range(len(lines)):
            this = lines[i]
            other1 = lines[(i+1)%3]
            other2 = lines[(i+2)%3]

            align1 = align_pairwise(this, other1)
            align2 = align_pairwise(this, other2)

            result = align_pairwise(align1, align2)
            values.append(result)
        if is_number:
            number = identify_number(values)
            if number is not None:
                return number
        return majority_vote(values)
    

def filter_exceeding_words(lines, roi):
    """Filter regions exceeding bounds of ROI

    There are three cases:
    1. None of the regions exceeds the bounds
    2. Some of them
    3. All of them

    We keep everything as is in cases 1. and 3.,
    in case 2. we filter out the exceeding ones
    (as at least one of the services thinks the 
    exceeding part does not belong here)

    Args:
        lines (list): given list of lines
        roi (ROI): respective ROI

    Returns:
        list: filtered lines
    """
    indicators = []
    reduced_lines = []
    for line in lines:
        reduced_line = []
        exceeding_indicator = False
        for rectangle in line:
            rectangle_exceeding = roi.exceeding_rectangle(rectangle)
            exceeding_indicator = exceeding_indicator or rectangle_exceeding
            if not rectangle_exceeding:
                reduced_line.append(rectangle)
        indicators.append(exceeding_indicator)
        reduced_lines.append(reduced_line)

    if not (all(indicators) or not any(indicators)):
        return reduced_lines
    return lines


def process_lines(lines, roi, is_number):
    """Join lines to words let majority voting decide

    Args:
        lines (list): lists of rectangles organised in lines
        roi (ROI): given ROI
        is_number (bool): True if number(s) is/are expected
    """
    lines = filter_exceeding_words(lines, roi)
    lines_of_words = [[rectangle.content for rectangle in line] for line in lines]
    lines_of_words = filter(None, lines_of_words)
    return identify_words([' '.join(line) for line in lines_of_words], is_number)


def align_lines(candidate_lines):
    """Group lines to categories by y-coordinate

    Also sort them by y-coordinate to ensure correct order.

    Args:
        candidate_lines (list): identified lines from all services

    Returns:
        list: lines grouped by y-coordinate
    """
    groups = dict()
    for lines in candidate_lines:
        for line in lines:
            center = np.mean([rectangle.center_y for rectangle in line])
            bottom = max([rectangle.end_y for rectangle in line])
            top = min([rectangle.start_y for rectangle in line])

            grouped = False
            for group_center in groups.keys():
                if bottom >= group_center >= top:
                    groups[group_center].append(line)
                    grouped = True
            if not grouped:
                groups[center] = [line]
    
    return [v for _, v in groups.items()]


def general_text_area(candidates, roi, is_number):
    """Process text area

    Args:
        candidates (list of lists): identified rectangles intersecting ROI
        roi (ROI): given ROI
        is_number (bool): True if number(s) is/are expected

    Returns:
        str: extracted text
    """
    # seperate each by lines
    candidate_lines = dict()
    for key in candidates.keys():
        if candidates[key]:
            lines = separate_to_lines(candidates[key])
            for line in lines:
                line.sort()
            candidate_lines[key] = lines

    results = dict()

    max_words, max_lines = get_max_dimensions(candidate_lines)

    # if the text area is reasonably small
    if max_lines <= 3 and max_words <= 5:
        for key in candidate_lines:
            results[key] = construct_lines(candidate_lines[key])
    
        aligned_groups = align_lines(candidate_lines.values())
        words = []
        for group in aligned_groups:
            word = process_lines(group, roi, is_number)
            words.append(word.strip())
        results['inferred'] = '\n'.join(words)
    else:
        results['inferred'] = construct_lines(list(candidate_lines.values())[0])

    return results
