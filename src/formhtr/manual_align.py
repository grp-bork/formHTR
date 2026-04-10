from __future__ import annotations

import io

import cv2
import img2pdf
import numpy as np
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

from .libs.pdf_to_image import convert_pdf_to_image, resize_image
from .libs.processing.align_images import compute_closest_point, transform


def _select_points(image, window_name: str):
    """Let the user click four corner points in an OpenCV window.

    Args:
        image: BGR image to display.
        window_name: OpenCV window title.

    Returns:
        List of up to four ``(x, y)`` points (may be fewer if the user quits early).
    """
    original_image = image.copy()
    points: list[tuple[int, int]] = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) < 4:
                points.append((x, y))
                cv2.circle(image, (x, y), 15, (0, 0, 255), -1)
                cv2.imshow(window_name, image)

    keep_running = True
    while keep_running:
        cv2.imshow(window_name, image)
        cv2.setMouseCallback(window_name, click_event)
        key = cv2.waitKey(0)

        if key == ord("r") and points:
            points.pop()
            image = original_image.copy()
            for (x, y) in points:
                cv2.circle(image, (x, y), 15, (0, 0, 255), -1)
            cv2.imshow(window_name, image)
        elif key in [27, ord("q")]:
            cv2.destroyAllWindows()
            keep_running = False

    cv2.destroyAllWindows()
    return points


def _to_pdf_bytes(image) -> bytes:
    """Encode a single-page raster image as PDF bytes.

    Args:
        image: ``numpy`` image array (RGB or BGR as accepted by PIL).

    Returns:
        PDF file content as bytes.
    """
    image_pil = Image.fromarray(image)
    image_bytes = io.BytesIO()
    image_pil.save(image_bytes, format="JPEG")
    return img2pdf.convert(image_bytes.getvalue())


def align_page(target, template, *, backside: bool = False,
               template_points: list[tuple[int, int]] | None = None,
               target_points: list[tuple[int, int]] | None = None):
    """Warp ``target`` onto ``template`` using four-point homography.

    Args:
        target: Scanned page image (``numpy`` BGR).
        template: Template image of the same logical size.
        backside: Affects GUI window labels only.
        template_points: Four template corners, or ``None`` to pick in a GUI.
        target_points: Four scan corners, or ``None`` to pick in a GUI.

    Returns:
        Warped ``target`` with template dimensions.
    """
    height, width, _ = target.shape

    target = resize_image(target, (width, height))
    template = resize_image(template, (width, height))

    template_points = template_points if template_points is not None else _select_points(
        template.copy(), "TEMPLATE(backside)" if backside else "TEMPLATE")
    template_points = [
        compute_closest_point((0, 0), template_points),
        compute_closest_point((width, 0), template_points),
        compute_closest_point((width, height), template_points),
        compute_closest_point((0, height), template_points),
    ]

    target_points = target_points if target_points is not None else _select_points(
        target.copy(), "SCAN(backside)" if backside else "SCAN")
    target_points = [
        compute_closest_point((0, 0), target_points),
        compute_closest_point((width, 0), target_points),
        compute_closest_point((width, height), target_points),
        compute_closest_point((0, height), target_points),
    ]

    return transform(target, template, target_points, template_points)


def manual_align_pdf(
    *,
    template_pdf: str,
    scanned_logsheet_pdf: str,
    output_pdf: str,
    backside_template_pdf: str | None = None,
    template_points: list[tuple[int, int]] | None = None,
    target_points: list[tuple[int, int]] | None = None,
) -> None:
    """Write a PDF whose pages are the aligned scan (front and optionally back).

    Args:
        template_pdf: Front template PDF path.
        scanned_logsheet_pdf: Scanned PDF (at least one page; two if backside is used).
        output_pdf: Output PDF path to create or overwrite.
        backside_template_pdf: Optional back template; if omitted, page 2 of the scan is copied.
        template_points: Optional shared four template corners (else GUI per ``align_page``).
        target_points: Optional shared four scan corners (else GUI per ``align_page``).

    Returns:
        ``None``; writes ``output_pdf`` on disk.
    """
    output_pdf_writer = PdfWriter()

    template = np.array(convert_pdf_to_image(template_pdf))
    target = np.array(convert_pdf_to_image(scanned_logsheet_pdf))

    aligned_frontside = align_page(target, template, backside=False,
                                   template_points=template_points,
                                   target_points=target_points)
    frontside_pdf_bytes = _to_pdf_bytes(aligned_frontside)
    frontside_pdf_reader = PdfReader(io.BytesIO(frontside_pdf_bytes))
    output_pdf_writer.add_page(frontside_pdf_reader.pages[0])

    if backside_template_pdf:
        template = np.array(convert_pdf_to_image(backside_template_pdf))
        target = np.array(convert_pdf_to_image(scanned_logsheet_pdf, page=1))

        aligned_backside = align_page(target, template, backside=True,
                                      template_points=template_points,
                                      target_points=target_points)
        backside_pdf_bytes = _to_pdf_bytes(aligned_backside)
        backside_pdf_reader = PdfReader(io.BytesIO(backside_pdf_bytes))
        output_pdf_writer.add_page(backside_pdf_reader.pages[0])
    else:
        original_pdf = PdfReader(scanned_logsheet_pdf)
        output_pdf_writer.add_page(original_pdf.pages[1])

    with open(output_pdf, "wb") as f:
        output_pdf_writer.write(f)
