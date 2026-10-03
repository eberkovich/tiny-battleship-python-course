from __future__ import annotations

import argparse
import sys
from pathlib import Path

from launcher.app import run_launcher
from launcher.course import CurriculumUnavailableError


def main() -> int:
    parser = argparse.ArgumentParser(description="Tiny Battleship course launcher")
    parser.add_argument("--student-dir", type=Path, required=True)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="открыть все готовые уроки и шаги без изменения прогресса",
    )
    arguments = parser.parse_args()
    try:
        run_launcher(arguments.student_dir, debug=arguments.debug)
    except CurriculumUnavailableError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
