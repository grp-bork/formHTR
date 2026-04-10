from __future__ import annotations

from formhtr.libs.logsheet_config import LogsheetConfig
from formhtr.libs.processing.rtree import Ensemble, RectangleTree
from formhtr.libs.region import Rectangle, ROI


def test_rectangle_tree_intersection_and_unused_filter():
    tree = RectangleTree(
        [
            Rectangle(0, 0, 10, 10, "A"),
            Rectangle(50, 50, 60, 60, "B"),
        ]
    )
    found = tree.find_intersection([0, 0, 20, 20])
    assert len(found) == 1
    assert found[0].object == "A"

    tree.mark_rectangles(found)
    unused = tree.filter_unused()
    assert [item.content for item in unused] == ["B"]


def test_rectangle_tree_prunes_matching_residual():
    tree = RectangleTree([Rectangle(0, 0, 10, 10, "HEADER")])
    residual = Rectangle(0, 0, 10, 10, "HEADER").to_residual()
    tree.prune_residuals([residual])
    assert tree.filter_unused() == []


def test_ensemble_find_intersection_returns_per_service():
    detected = {
        "google": [Rectangle(0, 0, 10, 10, "g")],
        "amazon": [Rectangle(1, 1, 11, 11, "a")],
        "azure": [Rectangle(2, 2, 12, 12, "z")],
    }
    config = LogsheetConfig(
        regions=[ROI(0, 0, 20, 20, "field", "Handwritten")],
        residuals=[],
        height=30,
        width=30,
    )

    ensemble = Ensemble(detected, config)
    results = ensemble.find_intersection([0, 0, 20, 20])
    assert [r.content for r in results["google"]] == ["g"]
    assert [r.content for r in results["amazon"]] == ["a"]
    assert [r.content for r in results["azure"]] == ["z"]
