from __future__ import annotations

import numpy as np

from .libs.pdf_to_image import convert_pdf_to_image, resize_image
from .libs.processing.align_images import get_alignment_data


def _prepare_alignment_images(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    page: int,
    dpi: int = 300,
):
    template_image = np.array(convert_pdf_to_image(template_pdf, dpi=dpi))
    logsheet_image = np.array(convert_pdf_to_image(
        scanned_logsheet_pdf, page=page, dpi=dpi))

    height, width, _ = logsheet_image.shape

    # Keep both images in the same resolution before corner detection.
    logsheet_image = resize_image(logsheet_image, (width, height))
    template_image = resize_image(template_image, (width, height))

    return logsheet_image, template_image


def get_page_alignment_data(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    page: int = 0,
    dpi: int = 300,
) -> dict:
    logsheet_image, template_image = _prepare_alignment_images(
        scanned_logsheet_pdf=scanned_logsheet_pdf,
        template_pdf=template_pdf,
        page=page,
        dpi=dpi,
    )

    alignment_data = get_alignment_data(logsheet_image, template_image)
    height, width, _ = logsheet_image.shape

    alignment_data["imageWidth"] = int(width)
    alignment_data["imageHeight"] = int(height)
    return alignment_data


def build_alignment_payload(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    backside_template_pdf: str | None = None,
    dpi: int = 300,
) -> dict:
    frontside_alignment_data = get_page_alignment_data(
        scanned_logsheet_pdf=scanned_logsheet_pdf,
        template_pdf=template_pdf,
        page=0,
        dpi=dpi,
    )

    backside_alignment_data = None
    if backside_template_pdf:
        backside_alignment_data = get_page_alignment_data(
            scanned_logsheet_pdf=scanned_logsheet_pdf,
            template_pdf=backside_template_pdf,
            page=1,
            dpi=dpi,
        )

    return {
        "frontside": frontside_alignment_data,
        "backside": backside_alignment_data,
    }
