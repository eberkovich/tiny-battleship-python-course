from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from runner.child import RESULT_PREFIX
from runner.results import RunResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class RunningStudentProcess:
    process: subprocess.Popen[str]
    started_at: float
    timeout: float | None

    def poll_result(self) -> RunResult | None:
        if self.process.poll() is None:
            if self.timeout is None or time.monotonic() - self.started_at < self.timeout:
                return None
            self.process.kill()
            self.process.communicate()
            return RunResult(
                "error",
                "timeout",
                "Программа работает слишком долго. Проверь, не застряла ли она.",
            )
        stdout, stderr = self.process.communicate()
        for line in reversed(stdout.splitlines()):
            if line.startswith(RESULT_PREFIX):
                try:
                    return RunResult.from_dict(json.loads(line[len(RESULT_PREFIX) :]))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                    break
        return RunResult(
            "error",
            "runner_error",
            "Не удалось прочитать результат запуска.",
            stderr[-2000:],
        )


def start_student_process(
    source: Path,
    *,
    mode: str,
    task_id: str | None = None,
    timeout: float | None = None,
    extra_environment: dict[str, str] | None = None,
) -> RunningStudentProcess:
    command = [
        sys.executable,
        "-m",
        "runner.child",
        "--mode",
        mode,
        "--file",
        str(source.resolve()),
    ]
    if task_id is not None:
        command.extend(("--task", task_id))

    environment = os.environ.copy()
    existing_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(PROJECT_ROOT)
        if not existing_path
        else os.pathsep.join((str(PROJECT_ROOT), existing_path))
    )
    if extra_environment:
        environment.update(extra_environment)

    process = subprocess.Popen(
        command,
        cwd=source.resolve().parent,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return RunningStudentProcess(process, time.monotonic(), timeout)


def run_check(source: Path, task_id: str, timeout: float = 5.0) -> RunResult:
    job = start_student_process(
        source, mode="check", task_id=task_id, timeout=timeout
    )
    while True:
        result = job.poll_result()
        if result is not None:
            return result
        time.sleep(0.01)

