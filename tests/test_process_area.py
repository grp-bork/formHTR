from __future__ import annotations

from formhtr.libs.processing.process_area import (
    align_lines,
    general_text_area,
    identify_number,
    identify_words,
    is_a_number,
    majority_vote,
    process_lines,
    separate_to_lines,
)
from formhtr.libs.region import Rectangle, ROI


def test_is_a_number_normalizes_and_validates():
    assert is_a_number(" 12,50 ") == "12.50"
    assert is_a_number("abc") is None


def test_identify_number_returns_most_frequent():
    assert identify_number(["1", "2", "1", "x"]) == "1"


def test_majority_vote_votes_per_character():
    assert majority_vote(["abc", "axc", "ayc"]) == "abc"


def test_identify_words_two_lines_prefers_numeric_when_requested():
    value = identify_words(["12,3", "12.3"], is_number=True)
    assert value == "12.3"


def test_separate_to_lines_groups_by_vertical_distance():
    rectangles = [
        Rectangle(0, 0, 10, 10, "A"),
        Rectangle(12, 1, 22, 11, "B"),
        Rectangle(0, 40, 10, 50, "C"),
    ]
    lines = separate_to_lines(rectangles)
    assert len(lines) == 2
    assert [r.content for r in lines[0]] == ["A", "B"]
    assert [r.content for r in lines[1]] == ["C"]


def test_process_lines_filters_words_exceeding_roi():
    roi = ROI(0, 0, 20, 20, "x", "Handwritten")
    lines = [
        [Rectangle(0, 0, 10, 10, "ok")],
        [Rectangle(0, 0, 30, 10, "too_far")],
    ]
    result = process_lines(lines, roi, is_number=False)
    assert "ok" in result
    assert "too_far" not in result


def test_align_lines_groups_close_centers_together():
    grouped = align_lines(
        [
            [[Rectangle(0, 0, 10, 10, "A")]],
            [[Rectangle(20, 1, 30, 11, "B")]],
        ]
    )
    assert len(grouped) == 1


def test_general_text_area_returns_inferred_value():
    candidates = {
        "google": [Rectangle(0, 0, 10, 10, "HELLO")],
        "amazon": [Rectangle(0, 0, 10, 10, "HELLO")],
        "azure": [],
    }
    roi = ROI(0, 0, 40, 20, "field", "Handwritten")
    out = general_text_area(candidates, roi, is_number=False)
    assert out["inferred"] == "HELLO"
