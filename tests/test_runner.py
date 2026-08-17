from pathlib import Path

import pytest

from launcher.course import load_lesson
from runner.process import run_check


REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "lessons/lesson_01/reference"
REFERENCE_CASES = [
    (task.id, f"{task.id}.py")
    for task in load_lesson().tasks
    if task.is_coding
]


@pytest.mark.parametrize(
    "task_id, filename",
    REFERENCE_CASES,
)
def test_reference_programs_pass_in_subprocess(task_id: str, filename: str) -> None:
    assert (REFERENCE_ROOT / filename).is_file()
    result = run_check(REFERENCE_ROOT / filename, task_id)

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

    result = run_check(source, "exercise_01")

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

    result = run_check(source, "exercise_01")

    assert result.status == "error"
    assert result.code == code
    assert result.message
    assert result.technical_details


def test_timeout_stops_runaway_student_program(tmp_path: Path) -> None:
    source = tmp_path / "forever.py"
    source.write_text("while True:\n    pass\n", encoding="utf-8")

    result = run_check(source, "exercise_01", timeout=0.1)

    assert result.code == "timeout"


def test_behavior_failure_does_not_become_runtime_error(tmp_path: Path) -> None:
    source = tmp_path / "empty.py"
    source.write_text("from battleship_ui import *\n", encoding="utf-8")

    result = run_check(source, "project")

    assert result.status == "failed"
    assert "show_board(PLAYER)" in result.message


def test_wrong_board_is_a_behavior_failure(tmp_path: Path) -> None:
    source = tmp_path / "wrong_board.py"
    source.write_text(
        "from battleship_ui import *\n"
        "show_board(PLAYER)\n"
        "draw_deck(ENEMY, 2, 4, DECK_IDLE)\n",
        encoding="utf-8",
    )

    result = run_check(source, "exercise_02")

    assert result.status == "failed"
    assert "твоём поле" in result.message
