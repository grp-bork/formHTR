from __future__ import annotations

import json

from formhtr.libs.logsheet_config import LogsheetConfig


def test_import_from_json_inferrs_types_and_varnames(tmp_path):
    config_path = tmp_path / "config.json"
    payload = {
        "height": 1000,
        "width": 1000,
        "to_ignore": [{"coords": [1, 1, 10, 10], "content": ["HEADER"]}],
        "content": [
            {"coords": [10, 10, 40, 40], "varname": None, "type": None},
            {"coords": [100, 100, 300, 140], "varname": "name", "type": None},
        ],
    }
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    config = LogsheetConfig([], [])
    config.import_from_json(str(config_path))

    assert config.height == 1000
    assert config.width == 1000
    assert len(config.residuals) == 1
    assert config.regions[0].varname == "0"
    assert config.regions[0].content_type == "Checkbox"
    assert config.regions[1].varname == "name"
    assert config.regions[1].content_type == "Handwritten"


def test_export_to_json_remove_unannotated(tmp_path):
    config = LogsheetConfig([], [], height=200, width=300)
    config.add_roi(0, 0, 10, 10, varname="a", content_type="Checkbox")
    config.add_roi(20, 20, 30, 30, varname="b", content_type=None)

    out_path = tmp_path / "out.json"
    config.export_to_json(str(out_path), remove_unannotated=True)

    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["height"] == 200
    assert written["width"] == 300
    assert len(written["content"]) == 1
    assert written["content"][0]["varname"] == "a"
