from __future__ import annotations

import argparse
import json
import sys

from formhtr.auto_align import build_alignment_payload


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "automatic-align", help="Compute alignment points JSON for scanned/template PDFs")
    parser.add_argument(
        "--pdf-logsheet", "--pdf_logsheet", dest="pdf_logsheet", required=True,
        help="Scanned logsheet PDF")
    parser.add_argument(
        "--pdf-template", "--pdf_template", dest="pdf_template", required=True,
        help="Template PDF")
    parser.add_argument(
        "--backside-template", "--backside_template", dest="backside_template",
        help="Backside template PDF")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for PDF conversion")
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    payload = build_alignment_payload(
        scanned_logsheet_pdf=args.pdf_logsheet,
        template_pdf=args.pdf_template,
        backside_template_pdf=args.backside_template,
        dpi=args.dpi,
    )
    sys.stdout.write(json.dumps(payload))
    return 0


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["automatic-align", *args])

