from __future__ import annotations

from dataclasses import dataclass

from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER


@dataclass(frozen=True)
class AcceptanceOutcome:
    passed: bool
    message: str


def _board(snapshot: dict[str, object], board: str) -> dict[str, object]:
    return snapshot["boards"][board]


def _visible(snapshot: dict[str, object], board: str) -> bool:
    return bool(_board(snapshot, board)["visible"])


def _cell(
    snapshot: dict[str, object], board: str, x: int, y: int
) -> tuple[str, str]:
    value = _board(snapshot, board)["cells"][f"{x},{y}"]
    return value[0], value[1]


def _require_ship(
    snapshot: dict[str, object], x: int, y: int
) -> AcceptanceOutcome | None:
    if _visible(snapshot, PLAYER) and _cell(snapshot, PLAYER, x, y) == (
        "deck",
        DECK_IDLE,
    ):
        return None
    return AcceptanceOutcome(
        False, f"Корабль должен стоять на твоём поле в клетке ({x}, {y})."
    )


def check(
    task_id: str,
    snapshot: dict[str, object],
    output: str,
) -> AcceptanceOutcome:
    expected = {
        "lesson_01_coordinates_exercise_01": ((2, 4),),
        "lesson_01_coordinates_exercise_02": ((3, 7),),
        "lesson_01_coordinates_exercise_03": ((2, 6), (8, 6)),
        "lesson_01_coordinates_project": ((2, 2),),
        "lesson_01_coordinates_star": (
            (2, 2),
            (3, 5),
            (4, 8),
            (9, 2),
            (8, 5),
            (7, 8),
        ),
    }.get(task_id)
    if expected is None:
        return AcceptanceOutcome(False, "Для этого задания пока нет проверки.")

    if task_id in {"lesson_01_coordinates_project", "lesson_01_coordinates_star"}:
        if not _visible(snapshot, PLAYER) or not _visible(snapshot, ENEMY):
            return AcceptanceOutcome(False, "Оба игровых поля должны остаться на экране.")

    for x, y in expected:
        failure = _require_ship(snapshot, x, y)
        if failure:
            return failure
    return AcceptanceOutcome(True, "Верно! Все корабли стоят в нужных клетках.")
