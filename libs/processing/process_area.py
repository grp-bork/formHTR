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


def separate_to_lines(rectangles):
    """Split set of rectangles into lines.

    This is determined by center of rectangle being inside of previous rectangle bounds.

    Args:
        rectangles (list): given list of rectangles

    Returns:
        list of list: list of rectangles grouped to lines
    """
    groups = [[rectangles[0]]]
    for rectangle in rectangles[1:]:
        aligned = False
        for i in range(len(groups)):
            if rectangle.is_y_aligned(groups[i][-1]) and not aligned:
                groups[i].append(rectangle)
                aligned = True
        if not aligned:
            groups.append([rectangle])
    return groups


def majority_vote_word_sets(sets_of_words):
    """Vote on individual positions of identified words in line

    TODO: it might be also smart to give higher priority if we are expecting a number
    or if we have a set of expected words/values

    Args:
        sets_of_words (list): list of lists (per service) of words corresponding to a line

    Returns:
        list: most probable list of words
    """
    # Determine the maximum set length
    max_length = max(len(s) for s in sets_of_words)

    # Compute the majority-voted set
    result = []
    for i in range(max_length):
        word_count = {}
        
        # Count occurrences of each word at position i
        for word_set in sets_of_words:
            if i < len(word_set):
                word = word_set[i]
                word_count[word] = word_count.get(word, 0) + 1

        # If any words were found for this position, get the one with maximum occurrence
        if word_count:
            voted_word = max(word_count, key=word_count.get)
            result.append(voted_word)

    return result


def process_lines(lines):
    """Join lines to words let majority voting decide

    TODO: A smarted algo should be used here at some point,
    working perhaps with individual words and their positions.

    TODO: if majority says there is one item and one service says its two,
    perhaps the majority is right

    Args:
        lines (list): lists of rectangles organised in lines
    """
    lines_of_words = [[rectangle.content for rectangle in line] for line in lines]
    sorted_lines = sorted(lines_of_words, key=len, reverse=True)
    return ''.join(majority_vote_word_sets(sorted_lines))


def general_text_area(candidates):
    """Process text area

    Args:
        candidates (list of lists): identified rectangles intersecting ROI

    Returns:
        str: extracted text
    """
    # seperate each by lines
    candidates = list(map(separate_to_lines, candidates))
    # sort from left to right 
    for candidate in candidates:
        for line in candidate:
            line.sort()

    lines = []
    
    for i in range(len(candidates[0])):
        # make sure they have the same number of lines !
        lines.append(process_lines([candidates[0][i], candidates[1][i], candidates[2][i]]))
    return '\n'.join(lines)
