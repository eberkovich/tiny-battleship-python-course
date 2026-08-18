from __future__ import annotations

from dataclasses import dataclass

from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER


@dataclass(frozen=True)
class AcceptanceOutcome:
    passed: bool
    message: str


def passed(message: str) -> AcceptanceOutcome:
    return AcceptanceOutcome(True, message)


def failed(message: str) -> AcceptanceOutcome:
    return AcceptanceOutcome(False, message)


def expect_output(output: str, expected: str) -> AcceptanceOutcome:
    if output == expected:
        return passed("Верно! Результат программы совпал с заданием.")
    shown = output or "пусто"
    return failed(f"Ожидался результат «{expected}», сейчас получилось: {shown}")


def board(snapshot: dict[str, object], board_name: str) -> dict[str, object]:
    return snapshot["boards"][board_name]


def cell(
    snapshot: dict[str, object], board_name: str, x: int, y: int
) -> tuple[str, str]:
    value = board(snapshot, board_name)["cells"][f"{x},{y}"]
    return value[0], value[1]


def expect_decks(
    snapshot: dict[str, object],
    board_name: str,
    cells: tuple[tuple[int, int], ...],
) -> AcceptanceOutcome | None:
    if not board(snapshot, board_name)["visible"]:
        name = "своё поле" if board_name == PLAYER else "поле противника"
        return failed(f"Сначала покажи {name}.")
    for x, y in cells:
        if cell(snapshot, board_name, x, y) != ("deck", DECK_IDLE):
            return failed(f"Не найден корабль в клетке ({x}, {y}).")
    return None


def expect_project_fleet(
    snapshot: dict[str, object],
    cells: tuple[tuple[int, int], ...],
    count: int,
) -> AcceptanceOutcome:
    for board_name in (PLAYER, ENEMY):
        if not board(snapshot, board_name)["visible"]:
            return failed("Оба игровых поля должны быть на экране.")
    deck_failure = expect_decks(snapshot, PLAYER, cells)
    if deck_failure:
        return deck_failure
    player = board(snapshot, PLAYER)
    if not player["ship_count_visible"] or player["ship_count"] != count:
        return failed(f"Покажи возле своего поля счётчик {count}.")
    return passed("Отлично! Флот и его счётчик работают.")


def expect_misses(
    snapshot: dict[str, object],
    board_name: str,
    cells: tuple[tuple[int, int], ...],
) -> AcceptanceOutcome:
    if not board(snapshot, board_name)["visible"]:
        return failed("Покажи нужное игровое поле.")
    for x, y in cells:
        if cell(snapshot, board_name, x, y) != ("water", "miss"):
            return failed(f"Не найден промах в клетке ({x}, {y}).")
    return passed("Звёздочка твоя! Все промахи показаны циклом.")


def button_events(snapshot: dict[str, object]) -> list[tuple[str, str]]:
    return [
        (str(event[1]), str(event[2]))
        for event in snapshot["events"]
        if event[0] == "button_waited"
    ]


__all__ = [
    "AcceptanceOutcome",
    "ENEMY",
    "PLAYER",
    "button_events",
    "expect_decks",
    "expect_misses",
    "expect_output",
    "expect_project_fleet",
    "failed",
    "passed",
]
