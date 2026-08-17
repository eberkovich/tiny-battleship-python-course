from __future__ import annotations

import os
import time
from pathlib import Path

import pygame

from battleship_ui.constants import (
    BOARD_SIZE,
    DECK_IDLE,
    ENEMY,
    PLAYER,
)
from battleship_ui.model import GameState


WINDOW_SIZE = (1040, 600)
CELL_SIZE = 40
BOARD_ORIGINS = {
    PLAYER: (70, 120),
    ENEMY: (570, 120),
}

BACKGROUND = (17, 27, 45)
TEXT = (239, 246, 255)
GRID = (185, 218, 236)
PLAYER_WATER = (51, 155, 202)
ENEMY_CLOSED = (53, 78, 112)
DECK_IDLE_ASSET = Path(__file__).with_name("assets") / "deck_idle.png"
MISS_ASSET = Path(__file__).with_name("assets") / "miss.png"


_state = GameState()
_screen: pygame.Surface | None = None
_deck_idle_surface: pygame.Surface | None = None
_miss_surface: pygame.Surface | None = None


def show_board(board: str) -> None:
    _state.show_board(board)
    _ensure_display()
    _render()


def draw_deck(board: str, x: int, y: int, state: str = DECK_IDLE) -> None:
    _state.draw_deck(board, x, y, state)
    if _screen is not None:
        _render()


def show_miss(board: str, x: int, y: int) -> None:
    _state.show_miss(board, x, y)
    if _screen is not None:
        _render()


def _ensure_display() -> pygame.Surface:
    global _screen
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.font.get_init():
        pygame.font.init()
    if _screen is None:
        pygame.display.set_caption("Морской бой — Python")
        _screen = pygame.display.set_mode(WINDOW_SIZE)
    return _screen


def _font(size: int, *, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("Arial", size, bold=bold)


def _board_rect(board: str) -> pygame.Rect:
    origin_x, origin_y = BOARD_ORIGINS[board]
    return pygame.Rect(
        origin_x, origin_y, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE
    )


def _cell_rect(board: str, x: int, y: int) -> pygame.Rect:
    origin_x, origin_y = BOARD_ORIGINS[board]
    return pygame.Rect(
        origin_x + (x - 1) * CELL_SIZE,
        origin_y + (y - 1) * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )


def _deck_idle_image() -> pygame.Surface:
    global _deck_idle_surface
    if _deck_idle_surface is None:
        source = pygame.image.load(DECK_IDLE_ASSET)
        _deck_idle_surface = pygame.transform.smoothscale(
            source, (CELL_SIZE, CELL_SIZE)
        )
    return _deck_idle_surface


def _miss_image() -> pygame.Surface:
    global _miss_surface
    if _miss_surface is None:
        source = pygame.image.load(MISS_ASSET)
        _miss_surface = pygame.transform.smoothscale(
            source, (CELL_SIZE, CELL_SIZE)
        )
    return _miss_surface


def _render() -> None:
    screen = _ensure_display()
    screen.fill(BACKGROUND)
    title = _font(30, bold=True).render("МОРСКОЙ БОЙ", True, TEXT)
    screen.blit(title, title.get_rect(center=(WINDOW_SIZE[0] // 2, 45)))

    for board in (PLAYER, ENEMY):
        if _state.boards[board].visible:
            _draw_board(screen, board)
    pygame.display.flip()


def _draw_board(screen: pygame.Surface, board: str) -> None:
    origin_x, origin_y = BOARD_ORIGINS[board]
    title_text = "ТВОЁ ПОЛЕ" if board == PLAYER else "ПОЛЕ ПРОТИВНИКА"
    title = _font(21, bold=True).render(title_text, True, TEXT)
    screen.blit(
        title,
        title.get_rect(center=(origin_x + BOARD_SIZE * CELL_SIZE // 2, 86)),
    )

    label_font = _font(16, bold=True)
    for index in range(1, BOARD_SIZE + 1):
        x_label = label_font.render(str(index), True, TEXT)
        y_label = label_font.render(str(index), True, TEXT)
        screen.blit(
            x_label,
            x_label.get_rect(
                center=(origin_x + (index - 0.5) * CELL_SIZE, origin_y - 17)
            ),
        )
        screen.blit(
            y_label,
            y_label.get_rect(
                center=(origin_x - 22, origin_y + (index - 0.5) * CELL_SIZE)
            ),
        )

    board_state = _state.boards[board]
    for y in range(1, BOARD_SIZE + 1):
        for x in range(1, BOARD_SIZE + 1):
            content, state = board_state.cells[(x, y)]
            rect = _cell_rect(board, x, y)
            base_color = PLAYER_WATER if board == PLAYER else ENEMY_CLOSED
            pygame.draw.rect(screen, base_color, rect)
            if content == "deck" and state == DECK_IDLE and board == PLAYER:
                screen.blit(_deck_idle_image(), rect)
            elif content == "water" and state == "miss":
                screen.blit(_miss_image(), rect)
            pygame.draw.rect(screen, GRID, rect, 1)


def _keep_open() -> None:
    if _screen is None:
        return
    autoclose_ms = int(os.environ.get("BATTLESHIP_AUTOCLOSE_MS", "0"))
    started = time.monotonic()
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if autoclose_ms and (time.monotonic() - started) * 1000 >= autoclose_ms:
            running = False
        clock.tick(60)
    pygame.quit()


def _reset() -> None:
    global _state, _screen
    _state = GameState()
    if pygame.display.get_init() or pygame.font.get_init():
        pygame.quit()
    _screen = None


def _snapshot() -> dict[str, object]:
    return _state.snapshot()


def _save_screenshot(path: str) -> None:
    if _screen is None:
        _ensure_display()
        _render()
    pygame.image.save(_screen, path)


__all__ = [
    "PLAYER",
    "ENEMY",
    "DECK_IDLE",
    "show_board",
    "draw_deck",
    "show_miss",
]
