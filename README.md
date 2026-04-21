# formHTR
Handwritten text recognition in form documents.

[![PyPI version](https://img.shields.io/pypi/v/formhtr.svg)](https://pypi.org/project/formhtr/)
[![Tests](https://github.com/grp-bork/formHTR/actions/workflows/tests.yml/badge.svg)](https://github.com/grp-bork/formHTR/actions/workflows/tests.yml)
[![docs](https://readthedocs.org/projects/formhtr/badge/?version=latest)](https://formhtr.readthedocs.io/en/latest/)

## Installation

### pip

```bash
pip install formhtr
```

The tool also requires the `zbar` shared library installed (used by `pyzbar`).
For PDF-related tooling, `qpdf` is also required.

System dependencies:

- macOS (Homebrew): `brew install zbar qpdf`
- Debian/Ubuntu: `sudo apt-get install libzbar0 qpdf`
- Fedora: `sudo dnf install zbar qpdf`

You can verify runtime requirements with:

```bash
formhtr doctor
```

## Usage

Run `formhtr --help` for full CLI help.

### Quickstart

```bash
# 1) Verify system dependencies
formhtr doctor

# 2) Create ROI config for a template
formhtr select-rois --pdf-file template.pdf --output-file config.json

# 3) Optionally annotate ROI types and variable names
formhtr annotate-rois --pdf-file template.pdf --config-file config.json --output-file config_annotated.json

# 4) Process a scanned logsheet into XLSX
formhtr process-logsheet \
  --pdf-logsheet scan.pdf \
  --pdf-template template.pdf \
  --config-file config_annotated.json \
  --output-file output.xlsx \
  --google google_credentials.json \
  --amazon amazon_credentials.json \
  --azure azure_credentials.json
```

### Select ROIs

Find and define locations of regions of interest (ROIs) in the given PDF.

Generally, it is possible to draw ROIs (rectangles) manually but also to detect them automatically.
The coordinates of ROIs are stored in a JSON file.

The tool is supposed to be run from the command line, as the control commands are entered there.

*Control commands*

* Press `q` or `Esc` to exit editing and save the config file.
* Press `r` to remove the last rectangle.

Run `formhtr select-rois -h` for details.

### Annotate ROIs

Specify the type of content for each rectangle.

The workflow is designed in a way that you can navigate over specified ROIs and assign them the expected type of their content.
This is done by pressing appropriate control commands.

*Control commands*

* Press `q` or `Esc` to exit editing and save the config file.
* Press `h` to add "Handwritten" type to the current ROI.
* Press `c` to add "Checkbox" type to the current ROI.
* Press `b` to add "Barcode" type to the current ROI.
* Press `r` or `d` to delete the type from the current ROI.
* Press `v` to enter the variable name.
* Press an arrow to navigate through ROIs (only left and right for now).

Run `formhtr annotate-rois -h` for details.

### Process logsheet

Extract values from specified ROIs.

This is the crucial step that applies various techniques to extract the information as precisely as possible.
It can process one logsheet at a time, given the template and config files.

Run `formhtr process-logsheet -h` for details.


### Credentials

The processing of logsheets is using external services requiring credentials to use them. Here we specify structure that is expected for credentials, always in JSON format.

__Google__

```
{
  "type": "service_account",
  "project_id": "theid",,
  "private_key_id": "thekey",
  "private_key": "-----BEGIN PRIVATE KEY-----anotherkey-----END PRIVATE KEY-----\n"
  "client_email": "emailaddress",
  "client_id": "id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "someurl",
  "universe_domain": "googleapis.com"
}
```

__Amazon__

```
{
    "ACCESS_KEY": "YOUR_KEY_ID_HERE",
    "SECRET_KEY": "YOUR_ACCESS_KEY_HERE",
    "REGION": "YOUR_REGION_NAME_HERE"
}
```

__Microsoft__

```
{
    "SUBSCRIPTION_KEY": "YOURKEYHERE",
    "ENDPOINT": "https://ENDPOINT"
}
```

### Examples

From the repository root (after `git clone`), set a short path prefix:

```bash
DATA=tests/test-data
```

#### CLI

```bash
# Check qpdf / zbar (no test files required)
formhtr doctor

# Automatic corner alignment payload for front (and optional back) pages
formhtr automatic-align \
  --pdf-logsheet "$DATA/logsheet/logsheet_tara.pdf" \
  --pdf-template "$DATA/template/template_tara.pdf"

# Two-page scan with separate front/back templates (CTD fixtures)
formhtr automatic-align \
  --pdf-logsheet "$DATA/logsheet/logsheet_ctd.pdf" \
  --pdf-template "$DATA/template/template_ctd_front.pdf" \
  --backside-template "$DATA/template/template_ctd_back.pdf"

# Export ROI crops to XLSX without OCR (use --no-aligned if the scan must be aligned first)
formhtr export-logsheet \
  --pdf-logsheet "$DATA/logsheet/logsheet_tara.pdf" \
  --pdf-template "$DATA/template/template_tara.pdf" \
  --config-file "$DATA/config/config_tara.json" \
  --output-file /tmp/formhtr_export_tara.xlsx \
  --aligned

# Full OCR pipeline (requires at least one of --google / --amazon / --azure)
formhtr process-logsheet \
  --pdf-logsheet "$DATA/logsheet/logsheet_tara.pdf" \
  --pdf-template "$DATA/template/template_tara.pdf" \
  --config-file "$DATA/config/config_tara.json" \
  --output-file /tmp/formhtr_out_tara.xlsx \
  --google credentials/google_credentials.json

# Two-sided CTD example (paths mirror tests)
formhtr process-logsheet \
  --pdf-logsheet "$DATA/logsheet/logsheet_ctd.pdf" \
  --pdf-template "$DATA/template/template_ctd_front.pdf" \
  --config-file "$DATA/config/config_ctd_front.json" \
  --output-file /tmp/formhtr_out_ctd.xlsx \
  --backside \
  --backside-template "$DATA/template/template_ctd_back.pdf" \
  --backside-config "$DATA/config/config_ctd_back.json" \
  --google credentials/google_credentials.json

# Interactive: click corner correspondences, write aligned PDF
formhtr manual-align \
  --pdf-template "$DATA/template/template_tara.pdf" \
  --pdf-logsheet "$DATA/logsheet/logsheet_tara.pdf" \
  --output /tmp/formhtr_aligned_tara.pdf

# Interactive GUI: set ROI types and variable names
formhtr annotate-rois \
  --pdf-file "$DATA/template/template_tara.pdf" \
  --config-file "$DATA/config/config_tara.json" \
  --output-file /tmp/config_annotated.json
```

#### Python API

Same paths as above; run with `PYTHONPATH=src` from the repo root, or after `pip install formhtr` with paths adjusted to your checkout.

```python
from pathlib import Path

DATA = Path("tests/test-data")

# formhtr.deps
from formhtr.deps import check_system_dependencies, ensure_system_dependencies

check_system_dependencies()
ensure_system_dependencies({"qpdf", "zbar"})

# formhtr.pdf_utils.get_pdf_dimensions
from formhtr.pdf_utils import get_pdf_dimensions

get_pdf_dimensions(pdf_file=str(DATA / "template/template_tara.pdf"))

# formhtr.auto_align
from formhtr.auto_align import build_alignment_payload, get_page_alignment_data

get_page_alignment_data(
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_tara.pdf"),
    template_pdf=str(DATA / "template/template_tara.pdf"),
    page=0,
)
build_alignment_payload(
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_ctd.pdf"),
    template_pdf=str(DATA / "template/template_ctd_front.pdf"),
    backside_template_pdf=str(DATA / "template/template_ctd_back.pdf"),
)

# formhtr.export_logsheet.export_logsheet_to_xlsx
from formhtr.export_logsheet import export_logsheet_to_xlsx

export_logsheet_to_xlsx(
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_tara.pdf"),
    template_pdf=str(DATA / "template/template_tara.pdf"),
    config_json=str(DATA / "config/config_tara.json"),
    output_xlsx="/tmp/formhtr_export_tara.xlsx",
    already_aligned=True,
)

# formhtr.logsheet — OCR needs real credentials (see Credentials below)
from formhtr.logsheet import (
    ServiceCredentials,
    extract_logsheet,
    load_credentials,
    process_logsheet_to_xlsx,
)

creds = load_credentials(google_credentials_path="credentials/google_credentials.json")
extract_logsheet(
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_tara.pdf"),
    template_pdf=str(DATA / "template/template_tara.pdf"),
    config_json=str(DATA / "config/config_tara.json"),
    credentials=creds,
    debug=False,
    front=True,
)
process_logsheet_to_xlsx(
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_tara.pdf"),
    template_pdf=str(DATA / "template/template_tara.pdf"),
    config_json=str(DATA / "config/config_tara.json"),
    output_xlsx="/tmp/formhtr_pipeline_tara.xlsx",
    credentials=creds,
)

# formhtr.roi_tools (GUIs unless select_rois(..., headless=True))
from formhtr.roi_tools import annotate_rois, select_rois

select_rois(
    template_pdf=str(DATA / "template/template_tara.pdf"),
    output_config_json="/tmp/rois.json",
    headless=True,
    existing_config_json=str(DATA / "config/config_tara.json"),
)
annotate_rois(
    template_pdf=str(DATA / "template/template_tara.pdf"),
    config_json=str(DATA / "config/config_tara.json"),
    output_config_json="/tmp/rois_annotated.json",
)

# formhtr.manual_align (opens windows unless template_points/target_points are passed)
from formhtr.manual_align import align_page, manual_align_pdf

manual_align_pdf(
    template_pdf=str(DATA / "template/template_tara.pdf"),
    scanned_logsheet_pdf=str(DATA / "logsheet/logsheet_tara.pdf"),
    output_pdf="/tmp/formhtr_aligned_tara.pdf",
)
# align_page is used on in-memory images inside the library; typical use is via manual_align_pdf.
```

## Documentation

API reference and installation notes are built with **Sphinx** under `docs/source/`. After you connect this repository to [Read the Docs](https://readthedocs.org/) (import the GitHub repo; the root `.readthedocs.yaml` drives the build), each push to the default branch triggers a documentation build. Enable “Build pull requests” in the RTD project settings if you want preview builds for PRs.

Pull requests also run a **GitHub Actions** job (`.github/workflows/docs.yml`) that installs the package and runs `sphinx-build`, so broken docs fail CI before merge.

Build locally (install [Poppler](https://poppler.freedesktop.org/) / `poppler-utils` alongside zbar and qpdf so `pdf2image` can run):

```bash
pip install ".[docs]"
sphinx-build -b html docs/source docs/_build/html
# equivalent: make -C docs html
```

## Developer Documentation

### Setup

Create your development environment using the provided [script](conda/environment-dev.yml) via conda to install all required dependencies.

### conda (dev)

```
conda env create -f conda_env.yaml
```

### Contributing

We appreciate contributions - feel free to open an issue on our repository, create your own fork, work on the problem and post a PR.
Please add your contributions to the [changelog](CHANGELOG.md) and to adhere to the [versioning](https://semver.org/spec/v2.0.0.html).
For more information see [here](CONTRIBUTING.md).

### Testing

All functionality is tested with the [pytest](https://docs.pytest.org/en/6.2.x/contents.html) framework.

The repository includes unit and mocked integration-style tests for the OCR
pipeline, CLI dispatch/validation, and output generation helpers. Tests are
executed automatically on pull requests and on pushes to `main`.

Run locally:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Optional live OCR test:

- Add at least one credential file in `credentials/`:
  `google_credentials.json`, `amazon_credentials.json`, or `azure_credentials.json`.
- The live test is skipped automatically when credentials are missing and in CI.

```bash
python -m pytest -q -m live_services
```
