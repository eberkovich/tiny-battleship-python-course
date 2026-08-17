from __future__ import annotations

import argparse
from pathlib import Path

from launcher.app import run_launcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny Battleship course launcher")
    parser.add_argument("--student-dir", type=Path, required=True)
    arguments = parser.parse_args()
    run_launcher(arguments.student_dir)


if __name__ == "__main__":
    main()

