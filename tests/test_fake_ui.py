import inspect

import pytest

import battleship_ui
from battleship_ui import fake_ui, real_ui
from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER
from battleship_ui.model import BattleshipUIError


def setup_function() -> None:
    fake_ui._reset()


def test_real_and_fake_public_signatures_match() -> None:
    for name in ("show_board", "draw_deck", "show_miss", "show_ship_count"):
        assert inspect.signature(getattr(fake_ui, name)) == inspect.signature(
            getattr(real_ui, name)
        )
    assert (
        inspect.signature(battleship_ui.show_ship_count)
        .parameters["count"]
        .default
        is inspect.Parameter.empty
    )


def test_public_api_does_not_expose_water_states() -> None:
    assert battleship_ui.__all__ == [
        "PLAYER",
        "ENEMY",
        "DECK_IDLE",
        "show_board",
        "draw_deck",
        "show_miss",
        "show_ship_count",
    ]
    for removed in ("WATER_IDLE", "WATER_FIRED", "draw_water"):
        assert not hasattr(battleship_ui, removed)


def test_boards_start_hidden_and_drawing_before_show_is_preserved() -> None:
    fake_ui.draw_deck(PLAYER, 2, 4, DECK_IDLE)
    fake_ui.show_miss(ENEMY, 4, 2)
    before_show = fake_ui._snapshot()
    assert not before_show["boards"][PLAYER]["visible"]
    assert not before_show["boards"][ENEMY]["visible"]

    fake_ui.show_board(PLAYER)
    fake_ui.show_board(PLAYER)
    snapshot = fake_ui._snapshot()

    assert snapshot["boards"][PLAYER]["visible"]
    assert snapshot["boards"][PLAYER]["cells"]["2,4"] == ["deck", DECK_IDLE]
    assert snapshot["boards"][ENEMY]["cells"]["4,2"] == ["water", "miss"]
    assert snapshot["events"] == [
        ["deck_drawn", PLAYER, 2, 4, DECK_IDLE],
        ["miss_shown", ENEMY, 4, 2],
        ["board_shown", PLAYER],
        ["board_shown", PLAYER],
    ]


def test_ship_count_is_hidden_at_zero_until_shown_and_can_be_updated() -> None:
    initial = fake_ui._snapshot()
    assert initial["boards"][PLAYER]["ship_count"] == 0
    assert not initial["boards"][PLAYER]["ship_count_visible"]

    fake_ui.show_ship_count(PLAYER, 0)
    fake_ui.show_ship_count(PLAYER, 4)
    snapshot = fake_ui._snapshot()

    assert snapshot["boards"][PLAYER]["ship_count_visible"]
    assert snapshot["boards"][PLAYER]["ship_count"] == 4
    assert not snapshot["boards"][ENEMY]["ship_count_visible"]
    assert snapshot["events"] == [
        ["ship_count_shown", PLAYER, 0],
        ["ship_count_shown", PLAYER, 4],
    ]


def test_checker_can_prepare_deterministic_cell_inputs() -> None:
    fake_ui._configure_inputs(cells=[(PLAYER, 2, 4), (ENEMY, 7, 3)])

    assert fake_ui._take_cell_input(PLAYER) == (2, 4)
    assert fake_ui._remaining_inputs() == ((ENEMY, 7, 3),)
    assert fake_ui._take_cell_input(ENEMY) == (7, 3)
    assert fake_ui._remaining_inputs() == ()


@pytest.mark.parametrize(
    "call, code",
    [
        (lambda: fake_ui.show_board("ocean"), "invalid_board"),
        (lambda: fake_ui.show_miss(ENEMY, 0, 2), "invalid_coordinate"),
        (lambda: fake_ui.draw_deck(PLAYER, True, 2), "invalid_coordinate"),
        (lambda: fake_ui.draw_deck(PLAYER, 1, 1, "miss"), "invalid_deck_state"),
        (lambda: fake_ui.show_ship_count(PLAYER, -1), "invalid_ship_count"),
        (lambda: fake_ui.show_ship_count(PLAYER, True), "invalid_ship_count"),
    ],
)
def test_invalid_public_arguments_fail_clearly(call, code: str) -> None:
    with pytest.raises(BattleshipUIError) as error:
        call()
    assert error.value.code == code
