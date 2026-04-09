from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from .libs.pdf_to_image import convert_pdf_to_image, resize_image
from .libs.processing.align_images import align_images
from .libs.processing.store_results import store_results
from .manual_align import align_page


@dataclass(frozen=True)
class ExportEntry:
    varname: str
    content: str
    x: int
    y: int
    width: int
    height: int
    page: int = 0


@dataclass(frozen=True)
class ExportConfig:
    width: int | None
    height: int | None
    entries: list[ExportEntry]


def _entry_from_data(item: dict, force_page: int | None = None) -> ExportEntry:
    coordinates = item.get("coordinates") or {}
    page = force_page if force_page is not None else int(item.get("page", 0))

    return ExportEntry(
        varname=item.get("varname") or "Unknown",
        content=item.get("content") or "",
        x=int(coordinates.get("x", 0)),
        y=int(coordinates.get("y", 0)),
        width=int(coordinates.get("width", 0)),
        height=int(coordinates.get("height", 0)),
        page=page,
    )


def _entry_from_content(item: dict, force_page: int | None = None) -> ExportEntry:
    coords = item.get("coords") or [0, 0, 0, 0]
    start_x, start_y, end_x, end_y = [int(v) for v in coords]
    page = 0 if force_page is None else force_page

    return ExportEntry(
        varname=item.get("varname") or "Unknown",
        content=item.get("content") or "",
        x=start_x,
        y=start_y,
        width=max(0, end_x - start_x),
        height=max(0, end_y - start_y),
        page=page,
    )


def _load_config_file(config_file: str, *, force_page: int | None = None) -> ExportConfig:
    with open(config_file, "r") as f:
        payload = json.load(f)

    entries: list[ExportEntry] = []

    if "data" in payload:
        for item in payload.get("data", []):
            entries.append(_entry_from_data(item, force_page=force_page))
    elif "content" in payload:
        for item in payload.get("content", []):
            entries.append(_entry_from_content(item, force_page=force_page))
    else:
        raise ValueError(
            "Unsupported config format. Expected either legacy 'data' or current 'content'.")

    width = payload.get("width")
    height = payload.get("height")

    return ExportConfig(
        width=int(width) if width is not None else None,
        height=int(height) if height is not None else None,
        entries=entries,
    )


def _parse_points(points: list) -> list[tuple[int, int]]:
    parsed: list[tuple[int, int]] = []
    for point in points:
        if isinstance(point, dict):
            parsed.append((int(point["x"]), int(point["y"])))
        else:
            parsed.append((int(point[0]), int(point[1])))
    return parsed


def _load_alignment_points(alignment_config_path: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    with open(alignment_config_path, "r") as f:
        align_config = json.load(f)

    template_points = align_config.get(
        "template_points") or align_config.get("templatePoints")
    target_points = align_config.get(
        "target_points") or align_config.get("targetPoints")

    if template_points is None or target_points is None:
        raise ValueError(
            "Alignment config must contain template/target points in snake_case or camelCase.")

    return _parse_points(template_points), _parse_points(target_points)


def _process_side(
    *,
    logsheet_image,
    template_image,
    aligned: bool,
    alignment_config_path: str | None,
):
    if aligned:
        return logsheet_image

    if alignment_config_path:
        template_points, target_points = _load_alignment_points(
            alignment_config_path)
        aligned_logsheet = align_page(
            logsheet_image,
            template_image,
            template_points=template_points,
            target_points=target_points,
        )
    else:
        print("Warning: Missing alignment points, falling back to automatic alignment.")
        aligned_logsheet = align_images(
            logsheet_image, template_image, filter_grayscale=False)

    if aligned_logsheet is None:
        print("Warning: Alignment failed. Using original image.")
        return logsheet_image

    return aligned_logsheet


def export_logsheet_to_xlsx(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    config_json: str,
    output_xlsx: str,
    already_aligned: bool = False,
    alignment_config_path: str | None = None,
    backside: bool = False,
    backside_template_pdf: str | None = None,
    backside_config_json: str | None = None,
    backside_alignment_config_path: str | None = None,
) -> None:
    front_config = _load_config_file(config_json)
    entries = list(front_config.entries)

    backside_config = None
    if backside and backside_config_json:
        backside_config = _load_config_file(backside_config_json, force_page=1)
        entries.extend(backside_config.entries)

    width = front_config.width
    height = front_config.height

    template_image = np.array(convert_pdf_to_image(template_pdf))
    logsheet_image = np.array(
        convert_pdf_to_image(scanned_logsheet_pdf, page=0))

    if width and height:
        target_size = (width, height)
        template_image = resize_image(template_image, target_size)
        logsheet_image = resize_image(logsheet_image, target_size)

    aligned_logsheet_front = _process_side(
        logsheet_image=logsheet_image,
        template_image=template_image,
        aligned=already_aligned,
        alignment_config_path=alignment_config_path,
    )

    aligned_logsheet_back = None
    if backside and backside_template_pdf:
        backside_template_image = np.array(
            convert_pdf_to_image(backside_template_pdf))
        logsheet_image_back = np.array(
            convert_pdf_to_image(scanned_logsheet_pdf, page=1))

        back_width = width
        back_height = height
        if backside_config and backside_config.width and backside_config.height:
            back_width = backside_config.width
            back_height = backside_config.height

        if back_width and back_height:
            target_size = (back_width, back_height)
            backside_template_image = resize_image(
                backside_template_image, target_size)
            logsheet_image_back = resize_image(
                logsheet_image_back, target_size)

        aligned_logsheet_back = _process_side(
            logsheet_image=logsheet_image_back,
            template_image=backside_template_image,
            aligned=already_aligned,
            alignment_config_path=backside_alignment_config_path,
        )

    results = []

    for entry in entries:
        if entry.page == 0:
            current_logsheet = aligned_logsheet_front
        elif entry.page == 1 and aligned_logsheet_back is not None:
            current_logsheet = aligned_logsheet_back
        else:
            continue

        img_h, img_w, _ = current_logsheet.shape

        y_start = max(0, entry.y)
        y_end = min(img_h, entry.y + entry.height)
        x_start = max(0, entry.x)
        x_end = min(img_w, entry.x + entry.width)

        if entry.width > 0 and entry.height > 0:
            cropped = current_logsheet[y_start:y_end, x_start:x_end]
        else:
            cropped = np.zeros((10, 10, 3), dtype=np.uint8)

        results.append([entry.varname, {"inferred": entry.content}, cropped])

    store_results(results, {}, output_xlsx)
