# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-09

### Added

- New CLI command `automatic-align` to compute alignment points and emit JSON payloads.
- New CLI command `export-logsheet` to export configured ROI values (and crops) directly to XLSX without OCR.
- New CLI command `pdf-dimensions` to emit PDF page dimensions as JSON.
- New top-level wrappers `automatic_align.py`, `export_logsheet.py`, and `pdf_dimensions.py`.

### Changed

- `process-logsheet` now supports partial OCR provider configuration (at least one of Google/Amazon/Azure is required instead of all three).
- `process-logsheet` now supports `--alignment-config` and `--backside-alignment-config` for deterministic non-interactive alignment.
- `process-logsheet` now supports `--store-csv` to write CSV output.
- `select-rois` now supports `--headless` for non-GUI ROI config generation.
- Alignment internals now accept precomputed alignment points for non-interactive workflows.

## [0.1.1] - 2026-04-08

### Changed

- fix numpy newer versions handling [#83](https://github.com/grp-bork/formHTR/issues/83)

## [0.1.0] - 2026-04-08

- Packaged project for PyPI with `pyproject.toml`, `src/` layout, and `formhtr` console entry point.
- Introduced a unified CLI with subcommands:
    - `process-logsheet`
    - `manual-align`
    - `select-rois`
    - `annotate-rois`
    - `doctor`
- Added API modules under `formhtr` to support both CLI and programmatic usage.
- Added runtime system dependency checks for `qpdf` and `zbar`, with platform-specific install hints.
- Updated README with installation guidance, system requirements, and a quickstart example.
