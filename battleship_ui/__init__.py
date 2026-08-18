from __future__ import annotations

import os

from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER


if os.environ.get("BATTLESHIP_UI_BACKEND", "real") == "fake":
    from battleship_ui import fake_ui as _backend
else:
    from battleship_ui import real_ui as _backend


def show_board(board: str) -> None:
    _backend.show_board(board)


def draw_deck(board: str, x: int, y: int, state: str = DECK_IDLE) -> None:
    _backend.draw_deck(board, x, y, state)


def show_miss(board: str, x: int, y: int) -> None:
    _backend.show_miss(board, x, y)


def show_ship_count(board: str, count: int) -> None:
    _backend.show_ship_count(board, count)


def wait_for_button(message: str, label: str) -> None:
    _backend.wait_for_button(message, label)


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
