from __future__ import annotations

from pathlib import Path

import pytest

from formhtr.deps import check_system_dependencies
from formhtr.libs.processing.barcode import extract_barcode, read_barcode, select_barcode
from formhtr.libs.processing import barcode as barcode_mod
from formhtr.libs.region import Rectangle

TEST_DATA = Path(__file__).resolve().parent / "test-data"


def test_extract_barcode_tie_keeps_first_service():
    candidates = {
        "google": [Rectangle(0, 0, 10, 10, "AAA")],
        "amazon": [Rectangle(0, 0, 10, 10, "BBB")],
        "azure": [],
    }
    assert extract_barcode(candidates) == "AAA"


def test_select_barcode_prefers_code128_over_i25():
    hits = [("I25", "136313"), ("CODE128", "112491108")]
    assert select_barcode(hits, set()) == "112491108"


def test_select_barcode_prefers_code128_over_zxing_itf():
    hits = [("ITF", "136313"), ("CODE128", "112491108")]
    assert select_barcode(hits, set()) == "112491108"


def test_select_barcode_requires_ocr_match_when_ocr_present():
    hits = [("I25", "136313"), ("CODE128", "112491108")]
    assert select_barcode(hits, {"112491108"}) == "112491108"
    assert select_barcode(hits, {"999"}) is None


def test_select_barcode_keeps_lone_i25_without_ocr():
    assert select_barcode([("I25", "136313")], set()) == "136313"


def test_zxing_ocr_mismatch_falls_through_to_pyzbar(monkeypatch):
    monkeypatch.setattr(
        barcode_mod,
        "decode_with_zxing",
        lambda image: [("ITF", "136313")],
    )
    monkeypatch.setattr(
        barcode_mod,
        "decode_with_pyzbar",
        lambda image: [("CODE128", "112491108")],
    )
    monkeypatch.setattr(barcode_mod, "rotate_barcode_image", lambda image: None)

    candidates = {
        "google": [Rectangle(0, 0, 10, 10, "112491108")],
        "amazon": [],
        "azure": [],
    }
    assert read_barcode(object(), candidates) == "112491108"


def test_empty_ocr_accepts_zxing_without_pyzbar(monkeypatch):
    monkeypatch.setattr(
        barcode_mod,
        "decode_with_zxing",
        lambda image: [("CODE128", "112491108")],
    )

    def fail_pyzbar(image):
        raise AssertionError("pyzbar should not run when zxing already decoded")

    monkeypatch.setattr(barcode_mod, "decode_with_pyzbar", fail_pyzbar)
    assert read_barcode(object(), {}) == "112491108"


def test_ctd_mte_sample_prefers_code128_over_i25_false_read():
    missing = dict(check_system_dependencies())
    if "poppler" in missing:
        pytest.skip(missing["poppler"])
    if "zbar" in missing:
        pytest.skip(missing["zbar"])

    from formhtr.libs.logsheet_config import LogsheetConfig
    from formhtr.logsheet import preprocess_input

    cfg = LogsheetConfig([], [])
    cfg.import_from_json(str(TEST_DATA / "config" / "config_ctd_front.json"))
    img = preprocess_input(
        scanned_logsheet_pdf=str(TEST_DATA / "logsheet" / "logsheet_ctd.pdf"),
        template_pdf=str(TEST_DATA / "template" / "template_ctd_front.pdf"),
        config=cfg,
        page=0,
        skip_alignment=False,
        filter_grayscale=False,
    )
    assert img is not None
    roi = next(region for region in cfg.regions if region.varname == "mte_sample")
    crop = img[roi.start_y:roi.end_y, roi.start_x:roi.end_x]
    assert read_barcode(crop, {}) == "112491108"
