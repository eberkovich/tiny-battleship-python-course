import os
from pathlib import Path

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
    real_ui.show_board(PLAYER)
    real_ui.show_board(ENEMY)
    screenshot = tmp_path / "boards.png"
    real_ui._save_screenshot(str(screenshot))

    snapshot = real_ui._snapshot()
    assert snapshot["boards"][PLAYER]["cells"]["2,4"] == ["deck", DECK_IDLE]
    assert snapshot["boards"][ENEMY]["cells"]["4,2"] == ["water", "miss"]
    assert screenshot.stat().st_size > 0


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
