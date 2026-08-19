import os
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from battleship_ui import real_ui
from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER


def setup_function() -> None:
    real_ui._reset()


def teardown_function() -> None:
    real_ui._reset()


def test_geometry_maps_one_based_coordinates_to_ten_by_ten_boards() -> None:
    player = real_ui._board_rect(PLAYER)
    enemy = real_ui._board_rect(ENEMY)

    assert player.size == (400, 400)
    assert enemy.size == (400, 400)
    assert real_ui._cell_rect(PLAYER, 1, 1).topleft == player.topleft
    assert real_ui._cell_rect(PLAYER, 10, 10).bottomright == player.bottomright
    assert not player.colliderect(enemy)


def test_hidden_state_is_rendered_after_show(tmp_path: Path) -> None:
    real_ui.draw_deck(PLAYER, 2, 4, DECK_IDLE)
    real_ui.show_miss(ENEMY, 4, 2)
    real_ui.show_ship_count(PLAYER, 4)
    real_ui.show_ship_count(ENEMY, 0)
    real_ui.show_board(PLAYER)
    real_ui.show_board(ENEMY)
    screenshot = tmp_path / "boards.png"
    real_ui._save_screenshot(str(screenshot))

    snapshot = real_ui._snapshot()
    assert snapshot["boards"][PLAYER]["cells"]["2,4"] == ["deck", DECK_IDLE]
    assert snapshot["boards"][ENEMY]["cells"]["4,2"] == ["water", "miss"]
    assert snapshot["boards"][PLAYER]["ship_count"] == 4
    assert snapshot["boards"][ENEMY]["ship_count"] == 0
    assert snapshot["boards"][PLAYER]["ship_count_visible"]
    assert snapshot["boards"][ENEMY]["ship_count_visible"]
    assert screenshot.stat().st_size > 0


def test_ship_counter_is_aligned_with_a_spacious_board_header() -> None:
    for board in (PLAYER, ENEMY):
        board_rect = real_ui._board_rect(board)
        counter = real_ui._ship_counter_rect(board)
        assert counter.right == board_rect.right
        assert counter.bottom < board_rect.top
        assert not counter.colliderect(board_rect)
        assert board_rect.top - real_ui.BOARD_HEADER_Y >= 50


def test_idle_deck_asset_is_packaged_and_scaled_to_fill_a_cell() -> None:
    assert real_ui.DECK_IDLE_ASSET.is_file()
    assert real_ui._deck_idle_image().get_size() == (
        real_ui.CELL_SIZE,
        real_ui.CELL_SIZE,
    )


def test_miss_asset_is_packaged_and_scaled_to_fill_a_cell() -> None:
    assert real_ui.MISS_ASSET.is_file()
    assert real_ui._miss_image().get_size() == (
        real_ui.CELL_SIZE,
        real_ui.CELL_SIZE,
    )


def test_button_prompt_uses_a_clickable_centered_button(tmp_path: Path) -> None:
    real_ui.show_board(PLAYER)
    real_ui._state.show_message("Флот готов!", "Начать бой")
    real_ui._render_prompt("Флот готов!", "Начать бой")
    screenshot = tmp_path / "button.png"
    real_ui._save_screenshot(str(screenshot))

    button = real_ui._prompt_button_rect()
    assert button.centerx == real_ui.WINDOW_SIZE[0] // 2
    assert button.width >= 200
    assert screenshot.stat().st_size > 0


def test_show_message_returns_after_click() -> None:
    real_ui.show_board(PLAYER)
    pygame.event.post(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": real_ui._prompt_button_rect().center},
        )
    )

    real_ui.show_message("Флот готов!", "Начать бой")

    assert real_ui._snapshot()["events"][-1] == [
        "message_shown",
        "Флот готов!",
        "Начать бой",
    ]
