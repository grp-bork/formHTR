"""Helpers for development-only CLI wrapper scripts.

These wrappers are intended for local repository use. Installed usage should
go through the ``formhtr`` console script entrypoint.
"""

from __future__ import annotations

import pathlib
import sys


def run(command: str, argv: list[str] | None = None) -> int:
    """Dispatch a fixed subcommand to ``formhtr.cli.main``.

    Args:
        command: Subcommand name (for example ``"manual-align"``).
        argv: Arguments after the subcommand. Defaults to ``sys.argv[1:]``.
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))

    from formhtr.cli import main

    args = sys.argv[1:] if argv is None else argv
    return main([command, *args])
