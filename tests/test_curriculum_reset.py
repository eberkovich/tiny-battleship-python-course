"""Production reset checks must not use the infrastructure course fixture."""

import os
from pathlib import Path
import subprocess
import sys

import pytest

from launcher.course import CurriculumUnavailableError, load_course


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_retired_curriculum_is_not_installed() -> None:
    assert not (PROJECT_ROOT / "CURRICULUM.yaml").exists()
    assert not list((PROJECT_ROOT / "lessons").glob("**/lesson.md"))
    assert not list((PROJECT_ROOT / "lessons").glob("**/acceptance.py"))
    with pytest.raises(CurriculumUnavailableError):
        load_course()


def test_reset_launch_does_not_create_a_workspace(tmp_path: Path) -> None:
    student = tmp_path / "new student"
    result = subprocess.run(
        [sys.executable, "-m", "launcher", "--student-dir", str(student)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"},
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 1
    assert "Уроки сейчас перерабатываются" in result.stderr
    assert "Traceback" not in result.stderr
    assert not student.exists()


def test_explicit_missing_curriculum_is_still_a_file_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_course(tmp_path / "missing.yaml")
