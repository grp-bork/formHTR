from __future__ import annotations

from formhtr.libs.region import Rectangle, ROI
from formhtr.libs.services.utils import extract_corners


def test_extract_corners_returns_bounding_box():
    start, end = extract_corners([(5, 10), (9, 1), (2, 3), (7, 8)])
    assert start == (2, 1)
    assert end == (9, 10)


def test_rectangle_order_uses_center_x():
    left = Rectangle(0, 0, 10, 10, "L")
    right = Rectangle(20, 0, 30, 10, "R")
    assert left < right


def test_roi_exceeding_rectangle_checks_end_x_only():
    roi = ROI(0, 0, 40, 40, "x", "Handwritten")
    inside = Rectangle(10, 0, 35, 10, "ok")
    exceeding = Rectangle(10, 0, 45, 10, "no")
    assert not roi.exceeding_rectangle(inside)
    assert roi.exceeding_rectangle(exceeding)
