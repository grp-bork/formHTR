from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from formhtr.logsheet import preprocess_input


def test_preprocess_input_reduces_dpi_until_size_is_under_limit(monkeypatch):
    calls = []

    def fake_convert(_pdf_path, page=0, dpi=300):
        calls.append(dpi)
        return np.zeros((20, 20, 3), dtype=np.uint8)

    monkeypatch.setattr("formhtr.logsheet.convert_pdf_to_image", fake_convert)
    monkeypatch.setattr("formhtr.logsheet.resize_image", lambda image, _size: image)
    monkeypatch.setattr("formhtr.logsheet.align_images", lambda scanned, _template, _filter: scanned)

    state = {"n": 0}

    def fake_size(_image):
        state["n"] += 1
        return 10_000_000 if state["n"] == 1 else 100

    monkeypatch.setattr("formhtr.logsheet.get_image_size", fake_size)

    config = SimpleNamespace(width=20, height=20)
    out = preprocess_input(
        scanned_logsheet_pdf="scan.pdf",
        template_pdf="template.pdf",
        config=config,
        page=0,
        skip_alignment=False,
        filter_grayscale=False,
        max_size_mb=0.0001,
        dpi=300,
    )

    assert out is not None
    assert 300 in calls
    assert 250 in calls


def test_preprocess_input_uses_alignment_config_when_provided(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "formhtr.logsheet.convert_pdf_to_image",
        lambda *_args, **_kwargs: np.zeros((10, 10, 3), dtype=np.uint8),
    )
    monkeypatch.setattr("formhtr.logsheet.resize_image", lambda image, _size: image)
    monkeypatch.setattr("formhtr.logsheet.get_image_size", lambda _image: 10)

    called = {"align_page": 0, "align_images": 0}
    monkeypatch.setattr(
        "formhtr.logsheet.align_page",
        lambda scanned, _template, template_points, target_points: (
            called.__setitem__("align_page", called["align_page"] + 1) or scanned
        ),
    )
    monkeypatch.setattr(
        "formhtr.logsheet.align_images",
        lambda scanned, _template, _filter: (
            called.__setitem__("align_images", called["align_images"] + 1) or scanned
        ),
    )

    cfg = tmp_path / "align.json"
    cfg.write_text(
        '{"template_points": [[0,0],[1,0],[1,1],[0,1]], "target_points": [[0,0],[1,0],[1,1],[0,1]]}',
        encoding="utf-8",
    )
    config = SimpleNamespace(width=10, height=10)
    out = preprocess_input(
        scanned_logsheet_pdf="scan.pdf",
        template_pdf="template.pdf",
        config=config,
        page=0,
        skip_alignment=False,
        filter_grayscale=False,
        alignment_config_path=str(cfg),
    )

    assert out is not None
    assert called["align_page"] == 1
    assert called["align_images"] == 0
