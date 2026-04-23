from __future__ import annotations

import argparse
import sys

from formhtr.export_logsheet import export_logsheet_to_xlsx


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "export-logsheet", help="Export ROI crops and values to XLSX without OCR")
    parser.add_argument(
        "--pdf-logsheet", "--pdf_logsheet", dest="pdf_logsheet", required=True,
        help="Scanned logsheet PDF")
    parser.add_argument(
        "--pdf-template", "--pdf_template", dest="pdf_template", required=True,
        help="Template PDF")
    parser.add_argument(
        "--config-file", "--config_file", dest="config_file", required=True,
        help="Frontside config JSON")
    parser.add_argument(
        "--output-file", "--output_file", dest="output_file", required=True,
        help="Output XLSX file")
    parser.add_argument("--aligned", action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Scanned image already aligned with template")
    parser.add_argument(
        "--alignment-config", "--alignment_config", dest="alignment_config",
        required=False,
        help="Path to frontside alignment config JSON")
    parser.add_argument("--backside", action=argparse.BooleanOptionalAction,
                        default=False, help="Backside page present")
    parser.add_argument(
        "--backside-template", "--backside_template", dest="backside_template",
        help="Backside template PDF")
    parser.add_argument(
        "--backside-config", "--backside_config", dest="backside_config",
        required=False,
        help="Path to backside config JSON")
    parser.add_argument(
        "--backside-alignment-config", "--backside_alignment_config", dest="backside_alignment_config",
        required=False,
        help="Path to backside alignment config JSON")
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    if args.backside and not args.backside_template:
        raise ValueError("--backside requires --backside-template.")

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


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["export-logsheet", *args])

