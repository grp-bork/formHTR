from Bio import pairwise2


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


def align_pairwise(s1, s2):
    alignments = pairwise2.align.globalxs(s1, s2, -3, -1, gap_char=' ')
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


def identify_words(lines):
    if len(lines) == 1:
        return lines[0]
    elif len(lines) == 2:
        # TODO we can get both directly
        align_1 = align_pairwise(lines[0], lines[1])
        align_2 = align_pairwise(lines[1], lines[0])
        # TODO voting with two like this makes no sense
        # perhaps its better to just take one of the outputs with no mixing and voting
        return majority_vote([align_1, align_2])
    elif len(lines) == 3:
        results = []
        for i in range(len(lines)):
            this = lines[i]
            other1 = lines[(i+1)%3]
            other2 = lines[(i+2)%3]

            align1 = align_pairwise(this, other1)
            align2 = align_pairwise(this, other2)

            result = align_pairwise(align1, align2)
            results.append(result)
        return majority_vote(results)


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
    return identify_words([' '.join(line) for line in sorted_lines])


def general_text_area(candidates):
    """Process text area

    Args:
        candidates (list of lists): identified rectangles intersecting ROI

    Returns:
        str: extracted text
    """
    # seperate each by lines
    candidate_lines = []
    for candidate in candidates:
        if candidate:
            lines = separate_to_lines(candidate)
            lines = sorted(lines, key=lambda x: x[0].center_y)
            for line in lines:
                line.sort()
            candidate_lines.append(lines)

    words = []
    
    for i in range(len(candidate_lines[0])):
        lines = []
        for candidate in candidate_lines:
            lines.append(candidate[i])
        # make sure they have the same number of lines !
        words.append(process_lines(lines))
    return '\n'.join(words)
