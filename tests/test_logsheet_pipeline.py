from __future__ import annotations

from pathlib import Path

import numpy as np

from formhtr.logsheet import ServiceCredentials, extract_logsheet, process_logsheet_to_xlsx
from formhtr.libs.region import Rectangle


def _to_rectangles(items: list[dict]) -> list[Rectangle]:
    return [Rectangle(*item["coords"], item["content"]) for item in items]


def test_extract_logsheet_with_mocked_boundaries_uses_real_config(
    monkeypatch, extracted_data
):
    config_path = Path("tests/test-data/config/config_tara.json").resolve()

    monkeypatch.setattr(
        "formhtr.logsheet.preprocess_input",
        lambda **_: np.zeros((3508, 2480, 3), dtype=np.uint8),
    )
    monkeypatch.setattr("formhtr.logsheet.annotate_pdfs", lambda *args, **kwargs: None)

    mocked_identified = {
        "google": _to_rectangles(extracted_data["tara"]["google"]),
        "amazon": _to_rectangles(extracted_data["tara"]["amazon"]),
        "azure": _to_rectangles(extracted_data["tara"]["azure"]),
    }
    monkeypatch.setattr("formhtr.logsheet.call_services", lambda *_args, **_kwargs: mocked_identified)

    contents, artefacts = extract_logsheet(
        scanned_logsheet_pdf="tests/test-data/logsheet/logsheet_tara.pdf",
        template_pdf="tests/test-data/template/template_tara.pdf",
        config_json=str(config_path),
        credentials=ServiceCredentials(None, None, None),
        debug=True,
        front=True,
    )

    assert contents is not None and len(contents) == 1
    assert contents[0][0] == "comments"
    assert "inferred" in contents[0][1]
    assert set(artefacts.keys()) == {"google", "amazon", "azure"}


def test_process_logsheet_to_xlsx_calls_store_csv_when_requested(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "formhtr.logsheet.extract_logsheet",
        lambda **_: ([["v1", {"inferred": "x"}, np.zeros((2, 2, 3), dtype=np.uint8)]], {"google": [], "amazon": [], "azure": []}),
    )

    calls = {"xlsx": 0, "csv": 0}
    monkeypatch.setattr("formhtr.logsheet.store_results", lambda *args, **kwargs: calls.__setitem__("xlsx", calls["xlsx"] + 1))
    monkeypatch.setattr("formhtr.logsheet.store_results_csv", lambda *args, **kwargs: calls.__setitem__("csv", calls["csv"] + 1))

    ratio = process_logsheet_to_xlsx(
        scanned_logsheet_pdf="a.pdf",
        template_pdf="b.pdf",
        config_json="c.json",
        output_xlsx=str(tmp_path / "out.csv"),
        credentials=ServiceCredentials(None, None, None),
        store_csv=True,
    )

    assert ratio is not None
    assert calls == {"xlsx": 0, "csv": 1}


def test_process_logsheet_to_xlsx_merges_backside_content(monkeypatch, tmp_path):
    front = (
        [["front", {"inferred": "A"}, np.zeros((1, 1, 3), dtype=np.uint8)]],
        {"google": [["g", np.zeros((1, 1, 3), dtype=np.uint8)]], "amazon": [], "azure": []},
    )
    back = (
        [["back", {"inferred": "B"}, np.zeros((1, 1, 3), dtype=np.uint8)]],
        {"google": [], "amazon": [["a", np.zeros((1, 1, 3), dtype=np.uint8)]], "azure": []},
    )
    state = {"n": 0}

    def fake_extract(**_kwargs):
        state["n"] += 1
        return front if state["n"] == 1 else back

    captured = {}
    monkeypatch.setattr("formhtr.logsheet.extract_logsheet", fake_extract)
    monkeypatch.setattr("formhtr.logsheet.store_results", lambda results, artefacts, output: captured.update({"results": results, "artefacts": artefacts, "output": output}))
    monkeypatch.setattr("formhtr.logsheet.store_results_csv", lambda *args, **kwargs: None)

    ratio = process_logsheet_to_xlsx(
        scanned_logsheet_pdf="a.pdf",
        template_pdf="front_template.pdf",
        config_json="front.json",
        output_xlsx=str(tmp_path / "out.xlsx"),
        credentials=ServiceCredentials(None, None, None),
        backside=True,
        backside_template_pdf="back_template.pdf",
        backside_config_json="back.json",
    )

    assert ratio is not None
    assert len(captured["results"]) == 2
    assert len(captured["artefacts"]["google"]) == 1
    assert len(captured["artefacts"]["amazon"]) == 1
