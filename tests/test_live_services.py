from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from formhtr.logsheet import ServiceCredentials, extract_logsheet, process_logsheet_to_xlsx


ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS_DIR = ROOT / "credentials"
GOOGLE_CREDENTIALS = CREDENTIALS_DIR / "google_credentials.json"
AMAZON_CREDENTIALS = CREDENTIALS_DIR / "amazon_credentials.json"
AZURE_CREDENTIALS = CREDENTIALS_DIR / "azure_credentials.json"

HAS_ANY_CREDENTIALS = any(
    path.exists() for path in (GOOGLE_CREDENTIALS, AMAZON_CREDENTIALS, AZURE_CREDENTIALS)
)
HAS_PDFINFO = shutil.which("pdfinfo") is not None


def _available_credentials() -> ServiceCredentials:
    google = str(GOOGLE_CREDENTIALS) if GOOGLE_CREDENTIALS.exists() else None
    amazon = (
        json.loads(AMAZON_CREDENTIALS.read_text(encoding="utf-8"))
        if AMAZON_CREDENTIALS.exists()
        else None
    )
    azure = (
        json.loads(AZURE_CREDENTIALS.read_text(encoding="utf-8"))
        if AZURE_CREDENTIALS.exists()
        else None
    )
    return ServiceCredentials(
        google_credentials_path=google,
        amazon_credentials=amazon,
        azure_credentials=azure,
    )


@pytest.mark.live_services
@pytest.mark.skipif(
    os.getenv("CI") == "true" or not HAS_ANY_CREDENTIALS or not HAS_PDFINFO,
    reason="Live OCR test requires at least one local credential, pdfinfo, and is skipped in CI.",
)
def test_extract_logsheet_live_services_with_local_credentials():
    credentials = _available_credentials()

    contents, artefacts = extract_logsheet(
        scanned_logsheet_pdf=str(ROOT / "tests/test-data/logsheet/logsheet_tara.pdf"),
        template_pdf=str(ROOT / "tests/test-data/template/template_tara.pdf"),
        config_json=str(ROOT / "tests/test-data/config/config_tara.json"),
        credentials=credentials,
        front=True,
        skip_alignment=True,
    )

    assert contents is not None
    assert len(contents) >= 1
    assert isinstance(artefacts, dict)
    assert set(artefacts.keys()) == {"google", "amazon", "azure"}


@pytest.mark.live_services
@pytest.mark.skipif(
    os.getenv("CI") == "true" or not HAS_ANY_CREDENTIALS or not HAS_PDFINFO,
    reason="Live OCR test requires at least one local credential, pdfinfo, and is skipped in CI.",
)
def test_process_logsheet_to_csv_live_with_ctd_front_and_back(tmp_path):
    credentials = _available_credentials()

    output = tmp_path / "ctd_live.csv"
    ratio = process_logsheet_to_xlsx(
        scanned_logsheet_pdf=str(ROOT / "tests/test-data/logsheet/logsheet_ctd.pdf"),
        template_pdf=str(ROOT / "tests/test-data/template/template_ctd_front.pdf"),
        config_json=str(ROOT / "tests/test-data/config/config_ctd_front.json"),
        output_xlsx=str(output),
        credentials=credentials,
        backside=True,
        backside_template_pdf=str(ROOT / "tests/test-data/template/template_ctd_back.pdf"),
        backside_config_json=str(ROOT / "tests/test-data/config/config_ctd_back.json"),
        already_aligned=True,
        store_csv=True,
    )

    assert ratio is not None
    assert output.exists()
    assert output.stat().st_size > 0
