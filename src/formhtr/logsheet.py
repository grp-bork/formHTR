from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np

from .libs.logsheet_config import LogsheetConfig
from .libs.pdf_to_image import (convert_pdf_to_image, get_image_size,
                                resize_image)
from .libs.processing.align_images import align_images
from .libs.processing.read_content import process_content
from .libs.processing.store_results import store_results, store_results_csv
from .libs.services.call_services import call_services
from .libs.statistics import compute_success_ratio
from .libs.visualise_regions import annotate_pdfs
from .manual_align import align_page


@dataclass(frozen=True)
class ServiceCredentials:
    google_credentials_path: str | None
    amazon_credentials: dict[str, Any] | None
    azure_credentials: dict[str, Any] | None


def load_credentials(
    *,
    google_credentials_path: str | None = None,
    amazon_credentials_path: str | None = None,
    azure_credentials_path: str | None = None,
) -> ServiceCredentials:
    amazon_credentials = None
    azure_credentials = None

    if amazon_credentials_path is not None:
        with open(amazon_credentials_path, 'r') as f:
            amazon_credentials = json.load(f)

    if azure_credentials_path is not None:
        with open(azure_credentials_path, 'r') as f:
            azure_credentials = json.load(f)

    return ServiceCredentials(
        google_credentials_path=google_credentials_path,
        amazon_credentials=amazon_credentials,
        azure_credentials=azure_credentials,
    )


def preprocess_input(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    config: LogsheetConfig,
    page: int,
    skip_alignment: bool,
    filter_grayscale: bool,
    max_size_mb: float = 4,
    dpi: int = 300,
    alignment_config_path: str | None = None,
):
    template_image = np.array(convert_pdf_to_image(template_pdf, dpi=dpi))
    logsheet_image = np.array(convert_pdf_to_image(
        scanned_logsheet_pdf, page, dpi=dpi))

    logsheet_image = resize_image(
        logsheet_image, (config.width, config.height))
    template_image = resize_image(
        template_image, (config.width, config.height))

    if not skip_alignment and alignment_config_path is None:
        logsheet_image = align_images(
            logsheet_image, template_image, filter_grayscale)

    elif not skip_alignment and alignment_config_path is not None:
        with open(alignment_config_path, 'r') as f:
            align_config = json.load(f)

        template_points = align_config['template_points']
        target_points = align_config['target_points']
        logsheet_image = align_page(logsheet_image, template_image,
                                    template_points=template_points,
                                    target_points=target_points)

    if logsheet_image is None:
        return None

    if get_image_size(logsheet_image) > max_size_mb * 2**20:
        if dpi <= 50:
            return logsheet_image
        return preprocess_input(
            scanned_logsheet_pdf=scanned_logsheet_pdf,
            template_pdf=template_pdf,
            config=config,
            page=page,
            skip_alignment=skip_alignment,
            filter_grayscale=filter_grayscale,
            max_size_mb=max_size_mb,
            dpi=dpi - 50,
            alignment_config_path=alignment_config_path,
        )

    return logsheet_image


def extract_logsheet(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    config_json: str,
    credentials: ServiceCredentials,
    debug: bool = False,
    front: bool = True,
    checkbox_edges: float = 0.2,
    skip_alignment: bool = False,
    filter_grayscale: bool = False,
    alignment_config_path: str | None = None,
):
    config = LogsheetConfig([], [])
    config.import_from_json(config_json)

    page = 0 if front else 1

    logsheet_image = preprocess_input(
        scanned_logsheet_pdf=scanned_logsheet_pdf,
        template_pdf=template_pdf,
        config=config,
        page=page,
        skip_alignment=skip_alignment,
        filter_grayscale=filter_grayscale,
        alignment_config_path=alignment_config_path,
    )
    if logsheet_image is None:
        return None, None

    identified_content = call_services(
        logsheet_image,
        {
            "google": credentials.google_credentials_path,
            "amazon": credentials.amazon_credentials,
            "azure": credentials.azure_credentials,
        },
        config,
    )

    if debug:
        annotate_pdfs(identified_content, logsheet_image, front)

    return process_content(identified_content, logsheet_image, config, checkbox_edges)


def process_logsheet_to_xlsx(
    *,
    scanned_logsheet_pdf: str,
    template_pdf: str,
    config_json: str,
    output_xlsx: str,
    credentials: ServiceCredentials,
    debug: bool = False,
    backside: bool = False,
    backside_template_pdf: str | None = None,
    backside_config_json: str | None = None,
    ugly_checkboxes: bool = False,
    already_aligned: bool = False,
    filter_grayscale: bool = False,
    store_csv: bool = False,
    alignment_config_path: str | None = None,
    backside_alignment_config_path: str | None = None,
) -> float | None:
    checkbox_edges = 0.4 if ugly_checkboxes else 0.2

    contents, artefacts = extract_logsheet(
        scanned_logsheet_pdf=scanned_logsheet_pdf,
        template_pdf=template_pdf,
        config_json=config_json,
        credentials=credentials,
        debug=debug,
        checkbox_edges=checkbox_edges,
        skip_alignment=already_aligned,
        filter_grayscale=filter_grayscale,
        front=True,
        alignment_config_path=alignment_config_path,
    )

    if contents is None:
        return None

    if backside:
        if not backside_template_pdf or not backside_config_json:
            raise ValueError(
                "backside_template_pdf and backside_config_json are required when backside=True")

        try:
            contents_back, artefacts_back = extract_logsheet(
                scanned_logsheet_pdf=scanned_logsheet_pdf,
                template_pdf=backside_template_pdf,
                config_json=backside_config_json,
                credentials=credentials,
                debug=debug,
                checkbox_edges=checkbox_edges,
                skip_alignment=already_aligned,
                filter_grayscale=filter_grayscale,
                front=False,
                alignment_config_path=backside_alignment_config_path,
            )
            if contents_back is not None and artefacts_back is not None:
                contents += contents_back
                for key in artefacts.keys():
                    artefacts[key] = artefacts[key] + artefacts_back[key]
        except ValueError:
            # backside present but actually a blank page
            pass

    ratio = compute_success_ratio(contents, artefacts)
    if not store_csv:
        # store to Excel sheet
        store_results(contents, artefacts, output_xlsx)
    else:
        store_results_csv(contents, artefacts, output_xlsx)

    return ratio
