from __future__ import annotations

import argparse
import sys

from formhtr.roi_tools import select_rois


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "select-rois", help="Interactively define ROIs in a template PDF")
    parser.add_argument("--pdf-file", required=True, help="Template PDF")
    parser.add_argument("--output-file", required=True, help="Output config JSON")
    parser.add_argument(
        "--autodetect", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--autodetect-filter", type=float, default=3)
    parser.add_argument("--config-file", default=None,
                        help="Existing config JSON to continue editing")
    parser.add_argument("--detect-residuals",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--credentials", default=None,
                        help="Google credentials JSON (for residual detection)")
    parser.add_argument("--display-residuals",
                        action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction,
                        default=False, help="Run in headless mode without GUI interaction.")
    parser.set_defaults(_runner=run)
    return parser


def run(args: argparse.Namespace) -> int:
    if args.detect_residuals and not args.credentials:
        raise ValueError("--detect-residuals requires --credentials.")
    if args.headless and args.display_residuals:
        raise ValueError("The --headless argument cannot be used together with --display_residuals.")
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


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["select-rois", *args])

