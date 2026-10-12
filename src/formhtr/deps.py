from __future__ import annotations

import ctypes.util
import os
import platform
import shutil
from pathlib import Path

_MACOS_ZBAR_DYLIBS = (
    "/opt/homebrew/lib/libzbar.dylib",
    "/usr/local/lib/libzbar.dylib",
)
_ZBAR_SEARCH_CONFIGURED = False


def _homebrew_prefix() -> str:
    brew = shutil.which("brew")
    if brew is not None:
        return str(Path(brew).resolve().parent.parent)
    if Path("/opt/homebrew/bin/brew").exists():
        return "/opt/homebrew"
    if Path("/usr/local/bin/brew").exists():
        return "/usr/local"
    return "/opt/homebrew"


def macos_zbar_dylib() -> str | None:
    """Return a Homebrew ``libzbar.dylib`` path if it exists."""
    prefix = _homebrew_prefix()
    candidates = (f"{prefix}/lib/libzbar.dylib",) + _MACOS_ZBAR_DYLIBS
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def configure_zbar_library_search() -> None:
    """Let ``ctypes.util.find_library('zbar')`` see Homebrew's library on macOS.

    Apple Silicon Homebrew installs to ``/opt/homebrew/lib``, which is not on
    the default dyld search path, so ``find_library`` (and ``pyzbar``) otherwise
    fail after ``brew install zbar``.
    """
    global _ZBAR_SEARCH_CONFIGURED
    if _ZBAR_SEARCH_CONFIGURED or platform.system() != "Darwin":
        return

    original = ctypes.util.find_library

    def find_library(name: str) -> str | None:
        found = original(name)
        if found:
            return found
        if name == "zbar":
            return macos_zbar_dylib()
        return None

    ctypes.util.find_library = find_library
    _ZBAR_SEARCH_CONFIGURED = True


def _install_hint(dep_name: str) -> str:
    system = platform.system().lower()
    if system == "darwin":
        hint = f"brew install {dep_name}"
        if dep_name == "zbar":
            libdir = f"{_homebrew_prefix()}/lib"
            hint += (
                f"; if zbar is already installed, the loader may still miss it: "
                f"export DYLD_FALLBACK_LIBRARY_PATH={libdir}"
            )
        return hint
    if system == "linux":
        if dep_name == "zbar":
            return "apt: sudo apt-get install libzbar0  |  dnf: sudo dnf install zbar"
        if dep_name == "poppler":
            return "apt: sudo apt-get install poppler-utils  |  dnf: sudo dnf install poppler-utils"
        return f"apt: sudo apt-get install {dep_name}  |  dnf: sudo dnf install {dep_name}"
    return f"Install {dep_name} using your system package manager."


def check_system_dependencies() -> list[tuple[str, str]]:
    """Return missing optional system dependencies.

    Returns:
        List of ``(name, install_hint)`` for each missing tool or library
        (currently ``qpdf``, ``zbar``, and ``poppler``).
    """
    missing: list[tuple[str, str]] = []

    if shutil.which("qpdf") is None:
        missing.append(("qpdf", _install_hint("qpdf")))

    configure_zbar_library_search()
    if ctypes.util.find_library("zbar") is None:
        missing.append(("zbar", _install_hint("zbar")))

    if shutil.which("pdfinfo") is None:
        missing.append(("poppler", _install_hint("poppler")))

    return missing


def ensure_system_dependencies(required: set[str]) -> None:
    """Raise ``RuntimeError`` if any required dependency is missing.

    Args:
        required: Subset of ``{"qpdf", "zbar", "poppler"}`` to enforce.

    Raises:
        RuntimeError: If a listed dependency is not available.
    """
    missing = check_system_dependencies()
    missing_required = [(name, hint) for name, hint in missing if name in required]
    if not missing_required:
        return

    lines = ["Missing required system dependencies:"]
    for name, hint in missing_required:
        lines.append(f"- {name}: {hint}")
    lines.append("Run `formhtr doctor` for a full dependency report.")
    raise RuntimeError("\n".join(lines))
