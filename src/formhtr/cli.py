from __future__ import annotations

import argparse
import sys

from . import __version__
from .commands import (
    annotate_rois,
    automatic_align,
    doctor,
    export_logsheet,
    manual_align,
    pdf_dimensions,
    process_logsheet,
    select_rois,
)


COMMAND_MODULES = (
    process_logsheet,
    manual_align,
    select_rois,
    annotate_rois,
    doctor,
    automatic_align,
    export_logsheet,
    pdf_dimensions,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="formhtr", description="formHTR CLI")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)
    for module in COMMAND_MODULES:
        module.register_parser(sub)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments, dispatch to the appropriate command, return exit code.

    Args:
        argv: Argument list (excluding program name). Uses ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit code: ``0`` on success, ``1`` for ``doctor`` with missing deps,
        ``2`` for unknown command (should not normally occur).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    runner = getattr(args, "_runner", None)
    if runner is None:
        parser.error(f"Unknown command: {args.command}")
        return 2
    try:
        return runner(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
