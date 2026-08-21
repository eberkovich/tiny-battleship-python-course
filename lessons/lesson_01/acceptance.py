from __future__ import annotations

from dataclasses import dataclass

from battleship_ui.constants import ENEMY, PLAYER


@dataclass(frozen=True)
class AcceptanceOutcome:
    passed: bool
    message: str


def _board(snapshot: dict[str, object], board: str) -> dict[str, object]:
    return snapshot["boards"][board]


def _visible(snapshot: dict[str, object], board: str) -> bool:
    return bool(_board(snapshot, board)["visible"])


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
    if task_id == "exercise_comments":
        failure = _require_visible(snapshot, PLAYER)
        return failure or AcceptanceOutcome(
            True, "Верно! Команда снова выполняется."
        )

    if task_id == "exercise_01":
        failure = _require_visible(snapshot, PLAYER)
        return failure or AcceptanceOutcome(True, "Отлично! Твоё поле видно.")

    if task_id == "exercise_enemy":
        failure = _require_visible(snapshot, ENEMY)
        return failure or AcceptanceOutcome(
            True, "Отлично! Поле противника видно."
        )

    if task_id == "project":
        for board in (PLAYER, ENEMY):
            failure = _require_visible(snapshot, board)
            if failure:
                return failure
        return AcceptanceOutcome(True, "Игра началась: оба поля на экране!")

    return AcceptanceOutcome(False, "Для этого задания пока нет проверки.")
