"""Minimal board check used only by infrastructure regression tests."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Outcome:
    passed: bool
    message: str


def check(task_id, snapshot, output):
    required = ("player", "enemy") if task_id == "project" else ("player",)
    for board in required:
        if not snapshot["boards"][board]["visible"]:
            name = "PLAYER" if board == "player" else "ENEMY"
            return Outcome(False, f"Покажи поле игрока: show_board({name})")
    return Outcome(True, "Верно!")
