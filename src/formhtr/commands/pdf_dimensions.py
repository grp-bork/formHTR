from __future__ import annotations

import argparse
import json
import sys

from formhtr.pdf_utils import get_pdf_dimensions


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "pdf-dimensions", help="Get PDF page dimensions after rasterization")
    parser.add_argument(
        "--pdf-file", "--pdf_file", dest="pdf_file", required=True,
        help="Path to PDF file")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for PDF conversion")
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    payload = get_pdf_dimensions(
        pdf_file=args.pdf_file,
        dpi=args.dpi,
    )
    sys.stdout.write(json.dumps(payload))
    return 0


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["pdf-dimensions", *args])

