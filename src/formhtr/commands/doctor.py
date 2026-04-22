from __future__ import annotations

import argparse
import sys

from formhtr.deps import check_system_dependencies


def register_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("doctor", help="Check required system dependencies")
    parser.set_defaults(_runner=run)
    return parser


def run(_args: argparse.Namespace) -> int:
    missing = check_system_dependencies()
    if not missing:
        print("All required system dependencies are available: qpdf, zbar.")
        return 0

    print("Missing system dependencies:")
    for name, hint in missing:
        print(f"- {name}: {hint}")
    return 1


def main(argv: list[str] | None = None) -> int:
    from formhtr.cli import main as cli_main

    args = sys.argv[1:] if argv is None else argv
    return cli_main(["doctor", *args])

