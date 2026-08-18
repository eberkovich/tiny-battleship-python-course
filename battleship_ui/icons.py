from __future__ import annotations

import pygame


def draw_ship_icon(
    target: pygame.Surface,
    center: tuple[int, int],
    color: tuple[int, int, int],
    *,
    scale: float = 1.0,
) -> None:
    x, y = center
    pygame.draw.polygon(
        target,
        color,
        [
            (x - 14 * scale, y),
            (x + 14 * scale, y),
            (x + 8 * scale, y + 9 * scale),
            (x - 8 * scale, y + 9 * scale),
        ],
    )
    pygame.draw.line(
        target,
        color,
        (x, y),
        (x, y - 13 * scale),
        max(2, round(3 * scale)),
    )
    pygame.draw.polygon(
        target,
        color,
        [
            (x + 2 * scale, y - 12 * scale),
            (x + 2 * scale, y - 2 * scale),
            (x + 11 * scale, y - 2 * scale),
        ],
    )
