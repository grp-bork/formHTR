"""Sphinx configuration for formHTR."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `make html` without a prior `pip install` (source checkout).
_root = Path(__file__).resolve().parents[2]
_src = _root / "src"
if _src.is_dir() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from formhtr import __version__

project = "formHTR"
copyright = "2026, EMBL"
author = "EMBL"
version = __version__
release = __version__

extensions = [
    "myst_parser",
    "sphinxarg.ext",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

myst_enable_extensions = ["colon_fence"]

exclude_patterns: list[str] = []

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
}
html_static_path: list[str] = []

autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
napoleon_google_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}
