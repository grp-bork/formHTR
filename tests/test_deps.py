from __future__ import annotations

from pathlib import Path

from formhtr.deps import check_system_dependencies, configure_zbar_library_search
from formhtr.libs.pdf_to_image import convert_pdf_to_image

TEMPLATE_PDF = Path(__file__).resolve().parent / "test-data" / "template" / "template_tara.pdf"


def test_macos_zbar_hint_mentions_dyld(monkeypatch):
    monkeypatch.setattr("formhtr.deps.platform.system", lambda: "Darwin")
    monkeypatch.setattr("formhtr.deps._homebrew_prefix", lambda: "/opt/homebrew")
    from formhtr.deps import _install_hint
    hint = _install_hint("zbar")
    assert "brew install zbar" in hint
    assert "DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib" in hint


def test_configure_zbar_library_search_finds_homebrew_dylib(monkeypatch, tmp_path):
    import ctypes.util

    import formhtr.deps as deps

    dylib = tmp_path / "libzbar.dylib"
    dylib.write_bytes(b"")
    monkeypatch.setattr("formhtr.deps.platform.system", lambda: "Darwin")
    monkeypatch.setattr("formhtr.deps.macos_zbar_dylib", lambda: str(dylib))
    deps._ZBAR_SEARCH_CONFIGURED = False
    monkeypatch.setattr(ctypes.util, "find_library", lambda _name: None)
    configure_zbar_library_search()
    try:
        assert ctypes.util.find_library("zbar") == str(dylib)
    finally:
        deps._ZBAR_SEARCH_CONFIGURED = False


def test_poppler_is_installed_and_can_rasterize_pdf():
    missing = dict(check_system_dependencies())
    assert "poppler" not in missing, (
        "Poppler (pdfinfo) is required to convert PDFs. "
        f"Install hint: {missing['poppler']}"
    )
    image = convert_pdf_to_image(str(TEMPLATE_PDF), dpi=72)
    assert image.size[0] > 0 and image.size[1] > 0
