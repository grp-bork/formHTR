from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .auto_align import build_alignment_payload
from .deps import check_system_dependencies, ensure_system_dependencies
from .export_logsheet import export_logsheet_to_xlsx
from .logsheet import load_credentials, process_logsheet_to_xlsx
from .manual_align import manual_align_pdf
from .pdf_utils import get_pdf_dimensions
from .roi_tools import annotate_rois, select_rois


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="formhtr", description="formHTR CLI")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    p_process = sub.add_parser(
        "process-logsheet", help="Extract values from a scanned logsheet to XLSX")
    p_process.add_argument("--pdf-logsheet", required=True,
                           help="Scanned logsheet PDF")
    p_process.add_argument(
        "--pdf-template", required=True, help="Template PDF")
    p_process.add_argument("--config-file", required=True, help="Config JSON")
    p_process.add_argument("--output-file", required=True,
                           help="Output XLSX file")
    p_process.add_argument("--google", required=False,
                           help="Path to Google Vision credentials JSON")
    p_process.add_argument("--amazon", required=False,
                           help="Path to Amazon credentials JSON")
    p_process.add_argument("--azure", required=False,
                           help="Path to Azure credentials JSON")
    p_process.add_argument("--debug", action=argparse.BooleanOptionalAction,
                           default=False, help="Output annotated PDFs")
    p_process.add_argument("--backside", action=argparse.BooleanOptionalAction,
                           default=False, help="Backside page present")
    p_process.add_argument("--backside-template", help="Backside template PDF")
    p_process.add_argument("--backside-config", help="Backside config JSON")
    p_process.add_argument(
        "--ugly-checkboxes",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Checkboxes have irregular shape / thick edges",
    )
    p_process.add_argument(
        "--aligned",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Scanned image already aligned with template (skip alignment)",
    )
    p_process.add_argument(
        "--alignment-config",
        required=False,
        help='Path to JSON file containing alignment config.')
    p_process.add_argument(
        "--backside-alignment-config",
        required=False,
        help='Path to JSON file containing backside alignment config.')
    p_process.add_argument(
        "--filter-grayscale",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="During alignment keep only darkest grayscale pixels",
    )
    p_process.add_argument(
        "--store-csv",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Store output as CSV instead of XLSX",
    )

    p_align = sub.add_parser(
        "manual-align", help="Interactively align a scanned PDF to a template")
    p_align.add_argument("--pdf-template", required=True, help="Template PDF")
    p_align.add_argument("--pdf-logsheet", required=True,
                         help="Scanned logsheet PDF")
    p_align.add_argument("--output", required=True, help="Output aligned PDF")
    p_align.add_argument("--backside-template", help="Backside template PDF")

    p_select = sub.add_parser(
        "select-rois", help="Interactively define ROIs in a template PDF")
    p_select.add_argument("--pdf-file", required=True, help="Template PDF")
    p_select.add_argument("--output-file", required=True,
                          help="Output config JSON")
    p_select.add_argument(
        "--autodetect", action=argparse.BooleanOptionalAction, default=False)
    p_select.add_argument("--autodetect-filter", type=float, default=3)
    p_select.add_argument("--config-file", default=None,
                          help="Existing config JSON to continue editing")
    p_select.add_argument("--detect-residuals",
                          action=argparse.BooleanOptionalAction, default=False)
    p_select.add_argument("--credentials", default=None,
                          help="Google credentials JSON (for residual detection)")
    p_select.add_argument("--display-residuals",
                          action=argparse.BooleanOptionalAction, default=False)
    p_select.add_argument("--headless", action=argparse.BooleanOptionalAction,
                          default=False, help='Run in headless mode without GUI interaction.')

    p_annot = sub.add_parser(
        "annotate-rois", help="Interactively label ROI types/variables")
    p_annot.add_argument("--pdf-file", required=True, help="Template PDF")
    p_annot.add_argument("--config-file", required=True,
                         help="Input config JSON")
    p_annot.add_argument("--output-file", required=True,
                         help="Output config JSON")
    p_annot.add_argument("--remove-unannotated",
                         action=argparse.BooleanOptionalAction, default=False)
    p_annot.add_argument("--display-residuals",
                         action=argparse.BooleanOptionalAction, default=False)

    sub.add_parser("doctor", help="Check required system dependencies")

    p_auto_align = sub.add_parser(
        "automatic-align", help="Compute alignment points JSON for scanned/template PDFs")
    p_auto_align.add_argument(
        "--pdf-logsheet", "--pdf_logsheet", dest="pdf_logsheet", required=True,
        help="Scanned logsheet PDF")
    p_auto_align.add_argument(
        "--pdf-template", "--pdf_template", dest="pdf_template", required=True,
        help="Template PDF")
    p_auto_align.add_argument(
        "--backside-template", "--backside_template", dest="backside_template",
        help="Backside template PDF")
    p_auto_align.add_argument("--dpi", type=int, default=300,
                              help="DPI for PDF conversion")

    p_export = sub.add_parser(
        "export-logsheet", help="Export ROI crops and values to XLSX without OCR")
    p_export.add_argument(
        "--pdf-logsheet", "--pdf_logsheet", dest="pdf_logsheet", required=True,
        help="Scanned logsheet PDF")
    p_export.add_argument(
        "--pdf-template", "--pdf_template", dest="pdf_template", required=True,
        help="Template PDF")
    p_export.add_argument(
        "--config-file", "--config_file", dest="config_file", required=True,
        help="Frontside config JSON")
    p_export.add_argument(
        "--output-file", "--output_file", dest="output_file", required=True,
        help="Output XLSX file")
    p_export.add_argument("--aligned", action=argparse.BooleanOptionalAction,
                          default=False,
                          help="Scanned image already aligned with template")
    p_export.add_argument(
        "--alignment-config", "--alignment_config", dest="alignment_config",
        required=False,
        help="Path to frontside alignment config JSON")
    p_export.add_argument("--backside", action=argparse.BooleanOptionalAction,
                          default=False, help="Backside page present")
    p_export.add_argument(
        "--backside-template", "--backside_template", dest="backside_template",
        help="Backside template PDF")
    p_export.add_argument(
        "--backside-config", "--backside_config", dest="backside_config",
        required=False,
        help="Path to backside config JSON")
    p_export.add_argument(
        "--backside-alignment-config", "--backside_alignment_config", dest="backside_alignment_config",
        required=False,
        help="Path to backside alignment config JSON")

    p_dims = sub.add_parser(
        "pdf-dimensions", help="Get PDF page dimensions after rasterization")
    p_dims.add_argument(
        "--pdf-file", "--pdf_file", dest="pdf_file", required=True,
        help="Path to PDF file")
    p_dims.add_argument("--dpi", type=int, default=300,
                        help="DPI for PDF conversion")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "process-logsheet":
        ensure_system_dependencies({"zbar"})
        if args.backside and (not args.backside_template or not args.backside_config):
            parser.error(
                "--backside requires --backside-template and --backside-config.")
        if args.google is None and args.amazon is None and args.azure is None:
            parser.error(
                'At least one OCR service credentials must be provided among --google, --amazon, and --azure.')

        credentials = load_credentials(
            google_credentials_path=args.google,
            amazon_credentials_path=args.amazon,
            azure_credentials_path=args.azure,
        )

        ratio = process_logsheet_to_xlsx(
            scanned_logsheet_pdf=args.pdf_logsheet,
            template_pdf=args.pdf_template,
            config_json=args.config_file,
            output_xlsx=args.output_file,
            credentials=credentials,
            debug=args.debug,
            backside=args.backside,
            backside_template_pdf=args.backside_template,
            backside_config_json=args.backside_config,
            ugly_checkboxes=args.ugly_checkboxes,
            already_aligned=args.aligned,
            filter_grayscale=args.filter_grayscale,
            store_csv=args.store_csv,
            alignment_config_path=args.alignment_config,
            backside_alignment_config_path=args.backside_alignment_config,
        )
        if ratio is not None:
            print(f"Success ratio: {ratio['ratio']:.3f}")
        return 0

    if args.command == "manual-align":
        ensure_system_dependencies({"qpdf"})
        manual_align_pdf(
            template_pdf=args.pdf_template,
            scanned_logsheet_pdf=args.pdf_logsheet,
            output_pdf=args.output,
            backside_template_pdf=args.backside_template,
        )
        return 0

    if args.command == "select-rois":
        if args.detect_residuals and not args.credentials:
            parser.error("--detect-residuals requires --credentials.")
        if args.headless and args.display_residuals:
            parser.error(
                'The --headless argument cannot be used together with --display_residuals.')
        select_rois(
            template_pdf=args.pdf_file,
            output_config_json=args.output_file,
            autodetect=args.autodetect,
            autodetect_filter=args.autodetect_filter,
            existing_config_json=args.config_file,
            detect_residuals=args.detect_residuals,
            google_credentials_path=args.credentials,
            display_residuals=args.display_residuals,
            headless=args.headless,
        )
        return 0

    if args.command == "annotate-rois":
        annotate_rois(
            template_pdf=args.pdf_file,
            config_json=args.config_file,
            output_config_json=args.output_file,
            remove_unannotated=args.remove_unannotated,
            display_residuals=args.display_residuals,
        )
        return 0

    if args.command == "doctor":
        missing = check_system_dependencies()
        if not missing:
            print("All required system dependencies are available: qpdf, zbar.")
            return 0

        print("Missing system dependencies:")
        for name, hint in missing:
            print(f"- {name}: {hint}")
        return 1

    if args.command == "automatic-align":
        payload = build_alignment_payload(
            scanned_logsheet_pdf=args.pdf_logsheet,
            template_pdf=args.pdf_template,
            backside_template_pdf=args.backside_template,
            dpi=args.dpi,
        )
        sys.stdout.write(json.dumps(payload))
        return 0

    if args.command == "export-logsheet":
        if args.backside and not args.backside_template:
            parser.error("--backside requires --backside-template.")

        export_logsheet_to_xlsx(
            scanned_logsheet_pdf=args.pdf_logsheet,
            template_pdf=args.pdf_template,
            config_json=args.config_file,
            output_xlsx=args.output_file,
            already_aligned=args.aligned,
            alignment_config_path=args.alignment_config,
            backside=args.backside,
            backside_template_pdf=args.backside_template,
            backside_config_json=args.backside_config,
            backside_alignment_config_path=args.backside_alignment_config,
        )
        return 0

    if args.command == "pdf-dimensions":
        payload = get_pdf_dimensions(
            pdf_file=args.pdf_file,
            dpi=args.dpi,
        )
        sys.stdout.write(json.dumps(payload))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
