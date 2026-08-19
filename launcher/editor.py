from __future__ import annotations

import configparser
import subprocess
import sys
from pathlib import Path


IDLE_FONT_FAMILY = "Menlo"
IDLE_FONT_SIZE = 18


def idle_user_dir() -> Path:
    return Path.home() / ".idlerc"


def ensure_idle_config(user_dir: Path | None = None) -> Path:
    directory = user_dir or idle_user_dir()
    configuration = directory / "config-main.cfg"
    parser = configparser.ConfigParser()
    if configuration.exists():
        parser.read(configuration, encoding="utf-8")

    font_options = ("font", "font-size", "font-bold")
    has_font_preference = parser.has_section("EditorWindow") and any(
        parser.has_option("EditorWindow", option) for option in font_options
    )
    if has_font_preference:
        return configuration

    directory.mkdir(parents=True, exist_ok=True)
    if not parser.has_section("EditorWindow"):
        parser.add_section("EditorWindow")
    parser.set("EditorWindow", "font", IDLE_FONT_FAMILY)
    parser.set("EditorWindow", "font-size", str(IDLE_FONT_SIZE))
    parser.set("EditorWindow", "font-bold", "0")
    with configuration.open("w", encoding="utf-8") as stream:
        parser.write(stream)
    return configuration


def editor_command(source: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "idlelib",
        "-e",
        str(source.resolve()),
    ]


def open_in_idle(source: Path) -> subprocess.Popen[bytes]:
    ensure_idle_config()
    return subprocess.Popen(
        editor_command(source),
        cwd=source.resolve().parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def close_editor(process: object | None) -> None:
    if process is None:
        return
    poll = getattr(process, "poll", None)
    terminate = getattr(process, "terminate", None)
    wait = getattr(process, "wait", None)
    if not callable(poll) or not callable(terminate) or poll() is not None:
        return
    try:
        terminate()
        if callable(wait):
            wait(timeout=2)
    except subprocess.TimeoutExpired:
        kill = getattr(process, "kill", None)
        if callable(kill):
            kill()
        if callable(wait):
            wait(timeout=2)
    except OSError:
        pass
