from __future__ import annotations

import argparse
import sys

from formhtr.deps import ensure_system_dependencies
from formhtr.logsheet import load_credentials, process_logsheet_to_xlsx


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "process-logsheet", help="Extract values from a scanned logsheet to XLSX")
    parser.add_argument("--pdf-logsheet", required=True, help="Scanned logsheet PDF")
    parser.add_argument("--pdf-template", required=True, help="Template PDF")
    parser.add_argument("--config-file", required=True, help="Config JSON")
    parser.add_argument("--output-file", required=True, help="Output XLSX file")
    parser.add_argument("--google", required=False, help="Path to Google Vision credentials JSON")
    parser.add_argument("--amazon", required=False, help="Path to Amazon credentials JSON")
    parser.add_argument("--azure", required=False, help="Path to Azure credentials JSON")
    parser.add_argument("--debug", action=argparse.BooleanOptionalAction,
                        default=False, help="Output annotated PDFs")
    parser.add_argument("--backside", action=argparse.BooleanOptionalAction,
                        default=False, help="Backside page present")
    parser.add_argument("--backside-template", help="Backside template PDF")
    parser.add_argument("--backside-config", help="Backside config JSON")
    parser.add_argument(
        "--ugly-checkboxes",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Checkboxes have irregular shape / thick edges",
    )
    parser.add_argument(
        "--aligned",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Scanned image already aligned with template (skip alignment)",
    )
    parser.add_argument(
        "--alignment-config",
        required=False,
        help="Path to JSON file containing alignment config.")
    parser.add_argument(
        "--backside-alignment-config",
        required=False,
        help="Path to JSON file containing backside alignment config.")
    parser.add_argument(
        "--filter-grayscale",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="During alignment keep only darkest grayscale pixels",
    )
    parser.add_argument(
        "--store-csv",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Store output as CSV instead of XLSX",
    )
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    ensure_system_dependencies({"zbar"})
    if args.backside and (not args.backside_template or not args.backside_config):
        raise ValueError("--backside requires --backside-template and --backside-config.")
    if args.google is None and args.amazon is None and args.azure is None:
        raise ValueError(
            "At least one OCR service credentials must be provided among --google, --amazon, and --azure.")

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


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["process-logsheet", *args])

