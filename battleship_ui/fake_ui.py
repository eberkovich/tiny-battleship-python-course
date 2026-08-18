from __future__ import annotations

from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER
from battleship_ui.model import GameState


_state = GameState()
_scripted_cells: list[tuple[str, int, int]] = []


def show_board(board: str) -> None:
    _state.show_board(board)


def draw_deck(board: str, x: int, y: int, state: str = DECK_IDLE) -> None:
    _state.draw_deck(board, x, y, state)


def show_miss(board: str, x: int, y: int) -> None:
    _state.show_miss(board, x, y)


def show_ship_count(board: str, count: int) -> None:
    _state.show_ship_count(board, count)


def wait_for_button(message: str, label: str) -> None:
    _state.wait_for_button(message, label)


def _configure_inputs(*, cells: list[tuple[str, int, int]]) -> None:
    global _scripted_cells
    validated = []
    for board, x, y in cells:
        _state._validate_board(board)
        _state._validate_coordinate(x, y)
        validated.append((board, x, y))
    _scripted_cells = validated


def _take_cell_input(board: str) -> tuple[int, int]:
    _state._validate_board(board)
    if not _scripted_cells:
        raise RuntimeError("Для проверки не подготовлен выбор клетки.")
    expected_board, x, y = _scripted_cells.pop(0)
    if expected_board != board:
        raise RuntimeError("Проверка подготовила выбор клетки на другом поле.")
    return x, y


def _remaining_inputs() -> tuple[tuple[str, int, int], ...]:
    return tuple(_scripted_cells)


def _reset() -> None:
    global _state, _scripted_cells
    _state = GameState()
    _scripted_cells = []


def _snapshot() -> dict[str, object]:
    return _state.snapshot()


__all__ = [
    "PLAYER",
    "ENEMY",
    "DECK_IDLE",
    "show_board",
    "draw_deck",
    "show_miss",
    "show_ship_count",
    "wait_for_button",
]
