import os
import time
from pathlib import Path

import pytest

from runner.process import run_check, start_student_process


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = PROJECT_ROOT / "tests/fixtures"
REFERENCE_CASES = [
    ("exercise_01", "player.py"),
    ("project", "boards.py"),
]


@pytest.mark.parametrize(
    "task_id, filename",
    REFERENCE_CASES,
)
def test_reference_programs_pass_in_subprocess(task_id: str, filename: str) -> None:
    assert (REFERENCE_ROOT / filename).is_file()
    result = run_check(
        REFERENCE_ROOT / filename,
        task_id,
        lesson_id="lesson_01",
    )

    assert result.passed, result


def test_student_program_is_not_imported_into_launcher_process(tmp_path: Path) -> None:
    source = tmp_path / "mutate.py"
    marker = tmp_path / "marker.txt"
    source.write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('child')\n"
        "from battleship_ui import *\n"
        "show_board(PLAYER)\n",
        encoding="utf-8",
    )

    result = run_check(source, "exercise_01", lesson_id="lesson_01")

    assert result.passed
    assert marker.read_text(encoding="utf-8") == "child"


@pytest.mark.parametrize(
    "program, code",
    [
        ("show_board(PLAYER\n", "syntax_error"),
        ("from battleship_ui import *\nshow_bord(PLAYER)\n", "name_error"),
        ("from battleship_ui import *\ndraw_deck(PLAYER, 99, 1)\n", "invalid_coordinate"),
    ],
)
def test_errors_are_translated_to_structured_results(
    tmp_path: Path, program: str, code: str
) -> None:
    source = tmp_path / "ошибка.py"
    source.write_text(program, encoding="utf-8")

    result = run_check(source, "exercise_01", lesson_id="lesson_01")

    assert result.status == "error"
    assert result.code == code
    assert result.message
    assert result.technical_details


def test_timeout_stops_runaway_student_program(tmp_path: Path) -> None:
    source = tmp_path / "forever.py"
    source.write_text("while True:\n    pass\n", encoding="utf-8")

    result = run_check(
        source,
        "exercise_01",
        lesson_id="lesson_01",
        timeout=0.1,
    )

    assert result.code == "timeout"


def test_behavior_failure_does_not_become_runtime_error(tmp_path: Path) -> None:
    source = tmp_path / "empty.py"
    source.write_text("from battleship_ui import *\n", encoding="utf-8")

    result = run_check(source, "project", lesson_id="lesson_01")

    assert result.status == "failed"
    assert "show_board(PLAYER)" in result.message


def test_wrong_board_is_a_behavior_failure(tmp_path: Path) -> None:
    source = tmp_path / "wrong_board.py"
    source.write_text(
        "from battleship_ui import *\n"
        "show_board(ENEMY)\n",
        encoding="utf-8",
    )

    result = run_check(
        source,
        "exercise_01",
        lesson_id="lesson_01",
    )

    assert result.status == "failed"
    assert "show_board(PLAYER)" in result.message


def test_checker_routes_to_requested_lesson_acceptance(tmp_path: Path) -> None:
    package_root = tmp_path / "checker_package"
    lesson_package = package_root / "lessons" / "lesson_02"
    lesson_package.mkdir(parents=True)
    (package_root / "lessons" / "__init__.py").write_text("", encoding="utf-8")
    (lesson_package / "__init__.py").write_text("", encoding="utf-8")
    (lesson_package / "acceptance.py").write_text(
        "class Outcome:\n"
        "    passed = True\n"
        "    message = 'Проверен второй урок.'\n\n"
        "def prepare(task_id, fake_ui):\n"
        "    fake_ui.show_board('enemy')\n\n"
        "def check(task_id, snapshot, output):\n"
        "    assert task_id == 'lesson_02_exercise_01'\n"
        "    assert snapshot['boards']['enemy']['visible']\n"
        "    assert output == '42\\n'\n"
        "    return Outcome()\n",
        encoding="utf-8",
    )
    source = tmp_path / "exercise.py"
    source.write_text(
        "from battleship_ui import *\nshow_board(PLAYER)\nprint(42)\n",
        encoding="utf-8",
    )
    python_path = os.pathsep.join((str(package_root), str(PROJECT_ROOT)))

    job = start_student_process(
        source,
        mode="check",
        lesson_id="lesson_02",
        task_id="lesson_02_exercise_01",
        timeout=5.0,
        extra_environment={"PYTHONPATH": python_path},
    )
    deadline = time.monotonic() + 5.0
    result = None
    while result is None and time.monotonic() < deadline:
        result = job.poll_result()
        time.sleep(0.01)

    assert result is not None
    assert result.passed
    assert result.message == "Проверен второй урок."
    assert result.output == "42\n"


def test_partial_output_is_preserved_after_runtime_error(tmp_path: Path) -> None:
    source = tmp_path / "partial.py"
    source.write_text("print('начало')\nraise RuntimeError('boom')\n", encoding="utf-8")

    result = run_check(source, "exercise_01", lesson_id="lesson_01")

    assert result.status == "error"
    assert result.output == "начало\n"


def test_captured_output_preserves_spaces_and_blank_rows(tmp_path: Path) -> None:
    source = tmp_path / "literal_output.py"
    source.write_text(
        "print('  начало  ')\nprint('')\nprint('конец  ')\nprint('')\n",
        encoding="utf-8",
    )
    result = run_check(source, "exercise_01", lesson_id="lesson_01")
    assert result.output == "  начало  \n\nконец  \n\n"


def test_student_output_is_bounded(tmp_path: Path) -> None:
    source = tmp_path / "large_output.py"
    source.write_text(
        "from battleship_ui import *\n"
        "show_board(PLAYER)\n"
        "print('x' * 10000)\n",
        encoding="utf-8",
    )

    result = run_check(source, "exercise_01", lesson_id="lesson_01")

    assert result.passed
    assert len(result.output) < 4100
    assert result.output.endswith("… вывод сокращён …")


def test_play_does_not_capture_pygame_banner_as_student_output() -> None:
    job = start_student_process(
        REFERENCE_ROOT / "boards.py",
        mode="play",
        timeout=5.0,
        extra_environment={
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
            "BATTLESHIP_AUTOCLOSE_MS": "30",
        },
    )
    deadline = time.monotonic() + 5.0
    result = None
    while result is None and time.monotonic() < deadline:
        result = job.poll_result()
        time.sleep(0.01)

    assert result is not None
    assert result.passed
    assert result.output == ""
