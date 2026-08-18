import random
import runpy
import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE = PROJECT_ROOT / "reference" / "part_01_game.py"


def flatten_cells(cells: list[tuple[int, int]]) -> list[int]:
    return [coordinate for cell in cells for coordinate in cell]


class ScriptedBattleshipUI:
    def __init__(self, cells: list[tuple[str, int, int]]):
        self.cells = list(cells)
        self.visible_boards: list[str] = []
        self.decks: dict[tuple[str, int, int], str] = {}
        self.misses: set[tuple[str, int, int]] = set()
        self.counts: dict[str, int] = {}
        self.buttons: list[tuple[str, str]] = []

    def show_board(self, board: str) -> None:
        self.visible_boards.append(board)

    def draw_deck(self, board: str, x: int, y: int, state: str) -> None:
        self.decks[(board, x, y)] = state

    def show_miss(self, board: str, x: int, y: int) -> None:
        self.misses.add((board, x, y))

    def show_ship_count(self, board: str, count: int) -> None:
        self.counts[board] = count

    def wait_for_cell(self, board: str) -> tuple[int, int]:
        expected_board, x, y = self.cells.pop(0)
        assert board == expected_board
        return x, y

    def wait_for_button(self, message: str, label: str) -> None:
        self.buttons.append((message, label))

    def module(self) -> types.ModuleType:
        module = types.ModuleType("battleship_ui")
        exports = {
            "PLAYER": "player",
            "ENEMY": "enemy",
            "DECK_IDLE": "deck_idle",
            "DECK_SUNK": "deck_sunk",
            "show_board": self.show_board,
            "draw_deck": self.draw_deck,
            "show_miss": self.show_miss,
            "show_ship_count": self.show_ship_count,
            "wait_for_cell": self.wait_for_cell,
            "wait_for_button": self.wait_for_button,
        }
        module.__dict__.update(exports)
        module.__all__ = list(exports)
        return module


def test_complete_part_one_reference_plays_to_victory(monkeypatch) -> None:
    player_ships = [
        (1, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (9, 1),
        (1, 3),
        (3, 3),
        (5, 3),
        (7, 3),
        (9, 3),
    ]
    enemy_ships = [
        (1, 5),
        (3, 5),
        (5, 5),
        (7, 5),
        (9, 5),
        (1, 7),
        (3, 7),
        (5, 7),
        (7, 7),
        (9, 7),
    ]
    ui = ScriptedBattleshipUI(
        [("player", 1, 1), ("player", 2, 2)]
        + [("player", x, y) for x, y in player_ships[1:]]
        + [("enemy", 1, 5), ("enemy", 1, 5)]
        + [("enemy", x, y) for x, y in enemy_ships[1:]]
    )
    computer_candidates = [
        (1, 1),
        (1, 1),
        (2, 1),
        (2, 10),
        (3, 10),
        (4, 10),
        (5, 10),
        (6, 10),
        (7, 10),
        (8, 10),
        (9, 10),
    ]
    random_values = flatten_cells(enemy_ships + computer_candidates)

    monkeypatch.setitem(sys.modules, "battleship_ui", ui.module())
    monkeypatch.setattr(random, "randint", lambda _start, _end: random_values.pop(0))

    namespace = runpy.run_path(str(REFERENCE), run_name="__main__")

    assert ui.cells == []
    assert random_values == []
    assert ui.visible_boards == ["player", "enemy"]
    assert ui.counts == {"player": 9, "enemy": 0}
    assert ui.decks[("player", 1, 1)] == "deck_sunk"
    assert all(
        ui.decks[("player", x, y)] == "deck_idle" for x, y in player_ships[1:]
    )
    assert all(
        ui.decks[("enemy", x, y)] == "deck_sunk" for x, y in enemy_ships
    )
    assert {("player", x, 10) for x in range(2, 10)} <= ui.misses
    assert ("player", 2, 1) not in ui.misses
    assert ui.buttons == [
        ("Корабли не должны соприкасаться.", "Попробовать ещё"),
        ("Флот готов!", "Начать бой"),
        ("Ты уже стрелял в эту клетку.", "Выбрать другую"),
        ("Ты победил!", "Готово"),
    ]
    can_place_ship = namespace["can_place_ship"]
    ships = [(5, 5)]
    assert not can_place_ship(5, 5, ships)
    assert not can_place_ship(4, 4, ships)
    assert not can_place_ship(6, 5, ships)
    assert can_place_ship(7, 5, ships)
    can_computer_shoot = namespace["can_computer_shoot"]
    assert not can_computer_shoot(3, 3, [(3, 3)], [])
    assert not can_computer_shoot(5, 5, [], [(5, 5)])
    assert not can_computer_shoot(4, 4, [], [(5, 5)])
    assert not can_computer_shoot(6, 5, [], [(5, 5)])
    assert can_computer_shoot(7, 5, [], [(5, 5)])


def test_complete_part_one_reference_plays_to_defeat(monkeypatch) -> None:
    player_ships = [
        (1, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (9, 1),
        (1, 3),
        (3, 3),
        (5, 3),
        (7, 3),
        (9, 3),
    ]
    enemy_ships = [
        (1, 5),
        (3, 5),
        (5, 5),
        (7, 5),
        (9, 5),
        (1, 7),
        (3, 7),
        (5, 7),
        (7, 7),
        (9, 7),
    ]
    player_misses = [(x, 9) for x in range(1, 11)]
    ui = ScriptedBattleshipUI(
        [("player", x, y) for x, y in player_ships]
        + [("enemy", x, y) for x, y in player_misses]
    )
    random_values = flatten_cells(enemy_ships + player_ships)

    monkeypatch.setitem(sys.modules, "battleship_ui", ui.module())
    monkeypatch.setattr(random, "randint", lambda _start, _end: random_values.pop(0))

    runpy.run_path(str(REFERENCE), run_name="__main__")

    assert ui.cells == []
    assert random_values == []
    assert ui.counts == {"player": 0, "enemy": 10}
    assert all(
        ui.decks[("player", x, y)] == "deck_sunk" for x, y in player_ships
    )
    assert {("enemy", x, y) for x, y in player_misses} <= ui.misses
    assert ui.buttons[-1] == ("Компьютер победил. Попробуй ещё!", "Готово")
