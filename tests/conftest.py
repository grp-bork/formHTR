from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from formhtr.libs.region import Rectangle, Residual, ROI


@pytest.fixture
def sample_rectangles() -> list[Rectangle]:
    return [
        Rectangle(10, 10, 30, 30, "A"),
        Rectangle(35, 10, 60, 30, "B"),
        Rectangle(10, 45, 30, 65, "C"),
    ]


@pytest.fixture
def sample_roi() -> ROI:
    return ROI(0, 0, 80, 80, varname="field", content_type="Handwritten")


@pytest.fixture
def sample_residual() -> Residual:
    return Residual(8, 8, 32, 32, expected_content=["A"])


@pytest.fixture
def rgb_image() -> np.ndarray:
    return np.full((20, 20, 3), 255, dtype=np.uint8)


@pytest.fixture(scope="session")
def extracted_data() -> dict:
    fixture_path = PROJECT_ROOT / "tests" / "test-data" / "extracted_content.py"
    spec = importlib.util.spec_from_file_location("extracted_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module.EXTRACTED
