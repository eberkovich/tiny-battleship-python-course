from __future__ import annotations

from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER
from battleship_ui.model import GameState


_state = GameState()


def show_board(board: str) -> None:
    _state.show_board(board)


def draw_deck(board: str, x: int, y: int, state: str = DECK_IDLE) -> None:
    _state.draw_deck(board, x, y, state)


def show_miss(board: str, x: int, y: int) -> None:
    _state.show_miss(board, x, y)


def show_ship_count(board: str, count: int) -> None:
    _state.show_ship_count(board, count)


def _reset() -> None:
    global _state
    _state = GameState()


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
]
