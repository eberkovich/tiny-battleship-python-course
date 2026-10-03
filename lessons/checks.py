"""Small shared behavioral checks for script-based foundation tasks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Outcome:
    passed: bool
    message: str


def check_output(output: str, expected: tuple[str, ...], failure: str) -> Outcome:
    # Ignore surrounding whitespace, but preserve output order and line count.
    actual = tuple(line.strip() for line in output.strip().splitlines())
    if actual != expected:
        return Outcome(False, failure)
    return Outcome(True, "Получилось! Программа показывает нужный результат.")
