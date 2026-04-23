from __future__ import annotations

import argparse
import sys

from formhtr.deps import ensure_system_dependencies
from formhtr.manual_align import manual_align_pdf


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "manual-align", help="Interactively align a scanned PDF to a template")
    parser.add_argument("--pdf-template", required=True, help="Template PDF")
    parser.add_argument("--pdf-logsheet", required=True, help="Scanned logsheet PDF")
    parser.add_argument("--output", required=True, help="Output aligned PDF")
    parser.add_argument("--backside-template", help="Backside template PDF")
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    ensure_system_dependencies({"qpdf"})
    manual_align_pdf(
        template_pdf=args.pdf_template,
        scanned_logsheet_pdf=args.pdf_logsheet,
        output_pdf=args.output,
        backside_template_pdf=args.backside_template,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["manual-align", *args])

