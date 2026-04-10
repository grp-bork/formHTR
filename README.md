# formHTR
Handprint text recognition in form documents.

[![PyPI version](https://img.shields.io/pypi/v/formhtr.svg)](https://pypi.org/project/formhtr/)
[![Tests](https://github.com/grp-bork/formHTR/actions/workflows/tests.yml/badge.svg)](https://github.com/grp-bork/formHTR/actions/workflows/tests.yml)

![Trec](https://github.com/grp-bork/formHTR/assets/15349569/c0789616-80d0-43c8-8693-d3d9f070511c)

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

### conda (dev)

```
conda env create -f conda_env.yaml
```

## Tests

The repository includes unit and mocked integration-style tests for the OCR
pipeline, CLI dispatch/validation, and output generation helpers. Tests are
executed automatically on pull requests and on pushes to `main`.

Run locally:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
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

### Create ROIs

This functionality is split (for now) into two separate scripts.

#### select ROIs

Find and define locations of regions of interest (ROIs) in the given PDF.

Generally, it is possible to draw ROIs (rectangles) manually but also to detect them automatically.
The coordinates of ROIs are stored in a JSON file.

The tool is supposed to be run from the command line, as the control commands are entered there.

*Control commands*

* Press `q` or `Esc` to exit editing and save the config file.
* Press `r` to remove the last rectangle.

Run `formhtr select-rois -h` for details.

#### annotate ROIs

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

### process logsheet

Extract values from specified ROIs.

This is the crucial step that applies various techniques to extract the information as precisely as possible.
It can process one logsheet at a time, given the template and config files.

Run `formhtr process-logsheet -h` for details.

#### Credentials

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
