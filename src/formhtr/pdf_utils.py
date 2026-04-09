from __future__ import annotations

import numpy as np

from .libs.pdf_to_image import convert_pdf_to_image


def get_pdf_dimensions(*, pdf_file: str, dpi: int = 300) -> dict[str, int]:
    image = np.array(convert_pdf_to_image(pdf_file, dpi=dpi))
    return {
        "height": int(image.shape[0]),
        "width": int(image.shape[1]),
    }
