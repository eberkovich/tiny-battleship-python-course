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


def _require_visible(
    snapshot: dict[str, object], board: str
) -> AcceptanceOutcome | None:
    if _visible(snapshot, board):
        return None
    name = "поле игрока" if board == PLAYER else "поле противника"
    constant = "PLAYER" if board == PLAYER else "ENEMY"
    return AcceptanceOutcome(
        False, f"Покажи {name}: show_board({constant})"
    )


def check(
    task_id: str,
    snapshot: dict[str, object],
    output: str,
) -> AcceptanceOutcome:
    if task_id == "exercise_01":
        failure = _require_visible(snapshot, PLAYER)
        return failure or AcceptanceOutcome(True, "Отлично! Твоё поле видно.")

    if task_id == "exercise_02":
        failure = _require_visible(snapshot, PLAYER)
        if failure:
            return failure
        if _cell(snapshot, PLAYER, 2, 4) != ("deck", DECK_IDLE):
            return AcceptanceOutcome(
                False,
                "Однопалубный корабль должен быть на твоём поле в клетке (2, 4).",
            )
        return AcceptanceOutcome(
            True, "Верно! Однопалубный корабль стоит в клетке (2, 4)."
        )

    if task_id == "exercise_03":
        failure = _require_visible(snapshot, ENEMY)
        if failure:
            return failure
        if _cell(snapshot, ENEMY, 4, 2) != ("water", "miss"):
            return AcceptanceOutcome(
                False, "Промах должен быть на поле противника в клетке (4, 2)."
            )
        return AcceptanceOutcome(True, "Точно! Промах отмечен в клетке (4, 2).")

    if task_id == "project":
        for board in (PLAYER, ENEMY):
            failure = _require_visible(snapshot, board)
            if failure:
                return failure
        return AcceptanceOutcome(True, "Игра началась: оба поля на экране!")

    if task_id == "star":
        for board in (PLAYER, ENEMY):
            failure = _require_visible(snapshot, board)
            if failure:
                return failure
        ships = ((2, 2), (3, 5), (4, 8), (9, 2), (8, 5), (7, 8))
        for x, y in ships:
            if _cell(snapshot, PLAYER, x, y) != ("deck", DECK_IDLE):
                return AcceptanceOutcome(
                    False,
                    f"Не найден корабль в клетке ({x}, {y}). Проверь отражение.",
                )
        return AcceptanceOutcome(True, "Звёздочка твоя! Флот стал зеркальным.")

    return AcceptanceOutcome(False, "Для этого задания пока нет проверки.")
