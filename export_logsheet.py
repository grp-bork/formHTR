import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from formhtr.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["export-logsheet", *sys.argv[1:]]))
