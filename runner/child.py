from __future__ import annotations

import argparse
import importlib
import json
import os
import runpy
import sys
import traceback
from pathlib import Path

from runner.results import RunResult


RESULT_PREFIX = "BATTLESHIP_RESULT="


def _technical_details(error: BaseException) -> str:
    return "".join(
        traceback.format_exception_only(type(error), error)
    ).strip()[:2000]


def _error_result(error: BaseException) -> RunResult:
    from battleship_ui.model import BattleshipUIError

    details = _technical_details(error)
    if isinstance(error, BattleshipUIError):
        return RunResult("error", error.code, str(error), details)
    if isinstance(error, SyntaxError):
        line = f" в строке {error.lineno}" if error.lineno else ""
        return RunResult(
            "error",
            "syntax_error",
            f"В коде есть синтаксическая ошибка{line}. Проверь скобки и запятые.",
            details,
        )
    if isinstance(error, NameError):
        name = getattr(error, "name", None)
        suffix = f" «{name}»" if name else ""
        return RunResult(
            "error",
            "name_error",
            f"Python не знает имя{suffix}. Проверь написание команды.",
            details,
        )
    if isinstance(error, TypeError):
        return RunResult(
            "error",
            "type_error",
            "Команда получила неподходящие аргументы. Проверь их порядок и количество.",
            details,
        )
    return RunResult(
        "error",
        "runtime_error",
        "Программа остановилась с ошибкой. Проверь последнюю изменённую команду.",
        details,
    )


def execute_check(source: Path, lesson_id: str, task_id: str) -> RunResult:
    os.environ["BATTLESHIP_UI_BACKEND"] = "fake"
    try:
        runpy.run_path(str(source), run_name="__main__")
        fake_ui = importlib.import_module("battleship_ui.fake_ui")
        acceptance = importlib.import_module(f"lessons.{lesson_id}.acceptance")
        outcome = acceptance.check(task_id, fake_ui._snapshot())
        if outcome.passed:
            return RunResult("passed", "passed", outcome.message)
        return RunResult("failed", "behavior_mismatch", outcome.message)
    except BaseException as error:
        return _error_result(error)


def execute_play(source: Path) -> RunResult:
    os.environ["BATTLESHIP_UI_BACKEND"] = "real"
    try:
        runpy.run_path(str(source), run_name="__main__")
        real_ui = importlib.import_module("battleship_ui.real_ui")
        real_ui._keep_open()
        return RunResult("passed", "played", "Игра закрыта.")
    except BaseException as error:
        return _error_result(error)


def _emit(result: RunResult) -> None:
    print(
        RESULT_PREFIX + json.dumps(result.to_dict(), ensure_ascii=False),
        flush=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("play", "check"), required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--lesson", default="lesson_01")
    parser.add_argument("--task")
    arguments = parser.parse_args(argv)

    source = arguments.file.resolve()
    if not source.is_file():
        _emit(
            RunResult(
                "error",
                "missing_file",
                "Файл с кодом не найден. Открой задание ещё раз.",
                str(source),
            )
        )
        return 2

    if arguments.mode == "check":
        if not arguments.task:
            parser.error("--task is required for check mode")
        result = execute_check(source, arguments.lesson, arguments.task)
    else:
        result = execute_play(source)
    _emit(result)
    return 0 if result.status in {"passed", "failed"} else 1


if __name__ == "__main__":
    sys.exit(main())

