from __future__ import annotations

import argparse
import sys

from formhtr.roi_tools import annotate_rois


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "annotate-rois", help="Interactively label ROI types/variables")
    parser.add_argument("--pdf-file", required=True, help="Template PDF")
    parser.add_argument("--config-file", required=True, help="Input config JSON")
    parser.add_argument("--output-file", required=True, help="Output config JSON")
    parser.add_argument("--remove-unannotated",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--display-residuals",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    annotate_rois(
        template_pdf=args.pdf_file,
        config_json=args.config_file,
        output_config_json=args.output_file,
        remove_unannotated=args.remove_unannotated,
        display_residuals=args.display_residuals,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["annotate-rois", *args])

