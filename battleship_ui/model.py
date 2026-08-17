from __future__ import annotations

from dataclasses import dataclass, field

from battleship_ui.constants import (
    BOARDS,
    BOARD_SIZE,
    DECK_STATES,
)


class BattleshipUIError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class BoardState:
    visible: bool = False
    cells: dict[tuple[int, int], tuple[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.cells:
            self.cells = {
                (x, y): ("water", "idle")
                for x in range(1, BOARD_SIZE + 1)
                for y in range(1, BOARD_SIZE + 1)
            }


class GameState:
    def __init__(self) -> None:
        self.boards = {board: BoardState() for board in BOARDS}
        self.events: list[tuple[object, ...]] = []

    def show_board(self, board: str) -> None:
        self._validate_board(board)
        self.boards[board].visible = True
        self.events.append(("board_shown", board))

    def show_miss(self, board: str, x: int, y: int) -> None:
        self._validate_board(board)
        self._validate_coordinate(x, y)
        self.boards[board].cells[(x, y)] = ("water", "miss")
        self.events.append(("miss_shown", board, x, y))

    def draw_deck(self, board: str, x: int, y: int, state: str) -> None:
        self._validate_board(board)
        self._validate_coordinate(x, y)
        if state not in DECK_STATES:
            raise BattleshipUIError(
                "invalid_deck_state", "Неизвестное состояние палубы."
            )
        self.boards[board].cells[(x, y)] = ("deck", state)
        self.events.append(("deck_drawn", board, x, y, state))

    def snapshot(self) -> dict[str, object]:
        return {
            "boards": {
                board: {
                    "visible": board_state.visible,
                    "cells": {
                        f"{x},{y}": [content, state]
                        for (x, y), (content, state) in board_state.cells.items()
                    },
                }
                for board, board_state in self.boards.items()
            },
            "events": [list(event) for event in self.events],
        }

    @staticmethod
    def _validate_board(board: str) -> None:
        if board not in BOARDS:
            raise BattleshipUIError("invalid_board", "Неизвестное игровое поле.")

    @staticmethod
    def _validate_coordinate(x: int, y: int) -> None:
        if type(x) is not int or type(y) is not int:
            raise BattleshipUIError(
                "invalid_coordinate", "Координаты клетки должны быть целыми числами."
            )
        if not (1 <= x <= BOARD_SIZE and 1 <= y <= BOARD_SIZE):
            raise BattleshipUIError(
                "invalid_coordinate",
                "Координаты клетки должны быть числами от 1 до 10.",
            )
