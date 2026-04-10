from __future__ import annotations

import csv

import numpy as np

from formhtr.libs.processing.store_results import store_results, store_results_csv


def test_store_results_csv_writes_inferred_and_fallback_values(tmp_path):
    output = tmp_path / "results.csv"
    results = [
        ["a", {"inferred": "chosen", "google": "g1"}, np.zeros((1, 1, 3), dtype=np.uint8)],
        ["b", {"google": "g2", "amazon": "a2"}, np.zeros((1, 1, 3), dtype=np.uint8)],
    ]
    artefacts = {"google": [], "amazon": [], "azure": []}

    store_results_csv(results, artefacts, str(output))

    with output.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    assert rows[0] == ["varname", "inferred value"]
    assert rows[1] == ["a", "chosen"]
    assert rows[2] == ["b", "g2"]


def test_store_results_creates_xlsx_and_cleans_images_dir(tmp_path):
    output = tmp_path / "results.xlsx"
    img = np.zeros((8, 8, 3), dtype=np.uint8)
    results = [["flag", {"inferred": True}, img]]
    artefacts = {"google": [["extra", img]], "amazon": [], "azure": []}

    store_results(results, artefacts, str(output))

    assert output.exists()
    assert output.stat().st_size > 0
    assert not (tmp_path / "images").exists()
