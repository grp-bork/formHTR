from __future__ import annotations

import cv2
import numpy as np

from .libs.annotate_ROI.annotate_ROIs_widget import AnnotateROIsWidget
from .libs.annotate_ROI.cli_inputs import process_cli as process_annotate_cli
from .libs.extract_ROI.autodect import detect_rectangles, find_residuals
from .libs.extract_ROI.cli_inputs import process_cli as process_select_cli
from .libs.extract_ROI.select_ROIs_widget import SelectROIsWidget
from .libs.logsheet_config import LogsheetConfig
from .libs.pdf_to_image import convert_pdf_to_image, resize_image
from .libs.region import ROI


def select_rois(
    *,
    template_pdf: str,
    output_config_json: str,
    autodetect: bool = False,
    autodetect_filter: float = 3,
    existing_config_json: str | None = None,
    detect_residuals: bool = False,
    google_credentials_path: str | None = None,
    display_residuals: bool = False,
    headless: bool = False,
) -> None:
    """Define ROIs on a template PDF and save JSON layout.

    Args:
        template_pdf: Path to the template PDF (first page).
        output_config_json: Path to write the ROI config JSON.
        autodetect: Run rectangle detection to seed ROIs.
        autodetect_filter: Scale passed to ``detect_rectangles``.
        existing_config_json: Optional config to load and continue editing.
        detect_residuals: Use Google Vision to find printed text to ignore (needs credentials).
        google_credentials_path: Google JSON path when ``detect_residuals`` is True.
        display_residuals: Draw residual regions in the UI.
        headless: Skip GUI and only export (with autodetect/residuals as configured).

    Returns:
        ``None``; writes ``output_config_json``.
    """
    image = np.array(convert_pdf_to_image(template_pdf))

    config = LogsheetConfig([], [])
    if existing_config_json:
        config.import_from_json(existing_config_json)
        image = resize_image(image, (config.width, config.height))
    else:
        rectangles = []
        residuals = []

        if autodetect:
            rectangles = detect_rectangles(image, autodetect_filter)
            rectangles = [ROI(*rectangle) for rectangle in rectangles]

        if detect_residuals:
            if not google_credentials_path:
                raise ValueError(
                    "google_credentials_path is required when detect_residuals=True")
            residuals = find_residuals(image, google_credentials_path)

        height, width, _ = image.shape
        config = LogsheetConfig(rectangles, residuals, height, width)

    if headless:
        config.export_to_json(output_config_json)
        return

    widget = SelectROIsWidget(image, config, display_residuals)
    process_select_cli(widget)
    cv2.destroyAllWindows()
    widget.config.export_to_json(output_config_json)


def annotate_rois(
    *,
    template_pdf: str,
    config_json: str,
    output_config_json: str,
    remove_unannotated: bool = False,
    display_residuals: bool = False,
) -> None:
    """Label ROI content types and variable names, then save updated config.

    Args:
        template_pdf: Path to the template PDF.
        config_json: Existing ROI config to load.
        output_config_json: Path to write the updated config.
        remove_unannotated: If True, drop ROIs without a type on export.
        display_residuals: Draw residual regions in the UI.

    Returns:
        ``None``; writes ``output_config_json``.
    """
    image = np.array(convert_pdf_to_image(template_pdf))

    config = LogsheetConfig([], [])
    config.import_from_json(config_json)
    image = resize_image(image, (config.width, config.height))

    widget = AnnotateROIsWidget(image, config, display_residuals)
    process_annotate_cli(widget)
    cv2.destroyAllWindows()
    widget.config.export_to_json(output_config_json, remove_unannotated)
