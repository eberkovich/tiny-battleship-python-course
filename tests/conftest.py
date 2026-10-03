"""Keep infrastructure tests independent of the installed child curriculum."""

import os
from pathlib import Path

import pytest

import launcher.course
import runner.process


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def infrastructure_course(request, monkeypatch):
    if request.path.name not in {
        "test_launcher.py", "test_workspace.py", "test_runner.py"
    }:
        return
    monkeypatch.setattr(launcher.course, "PROJECT_ROOT", FIXTURE_ROOT)
    monkeypatch.setattr(runner.process, "PROJECT_ROOT", FIXTURE_ROOT)
    monkeypatch.setenv(
        "PYTHONPATH",
        os.pathsep.join((str(FIXTURE_ROOT), str(PROJECT_ROOT))),
    )
