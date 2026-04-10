from __future__ import annotations

from formhtr.libs.processing.store_results import order_results
from formhtr.libs.statistics import compute_success_ratio


def test_order_results_follows_expected_priority():
    values = {"azure": "az", "inferred": "inf", "google": "gg"}
    assert order_results(values) == ["inf", "gg", "az"]


def test_compute_success_ratio_handles_zero_artefacts():
    ratio = compute_success_ratio(
        contents=[["a", {}, None], ["b", {}, None]],
        artefacts={"google": [], "amazon": [], "azure": []},
    )
    assert ratio["identified"] == 2
    assert ratio["artefacts"] == 0
    assert ratio["ratio"] == 2.0
