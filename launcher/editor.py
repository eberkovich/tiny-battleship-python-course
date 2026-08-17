from __future__ import annotations

import configparser
import subprocess
import sys
from pathlib import Path


def thonny_user_dir() -> Path:
    return Path(sys.prefix) / ".thonny"


def ensure_russian_thonny_config(user_dir: Path | None = None) -> Path:
    directory = user_dir or thonny_user_dir()
    configuration = directory / "configuration.ini"
    if configuration.exists():
        return configuration

    directory.mkdir(parents=True, exist_ok=True)
    parser = configparser.ConfigParser()
    parser["general"] = {"language": "ru_RU"}
    with configuration.open("w", encoding="utf-8") as stream:
        parser.write(stream)
    return configuration


def editor_command(source: Path) -> list[str]:
    return [sys.executable, "-m", "thonny", str(source.resolve())]


def open_in_thonny(source: Path) -> subprocess.Popen[bytes]:
    ensure_russian_thonny_config()
    return subprocess.Popen(
        editor_command(source),
        cwd=source.resolve().parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

