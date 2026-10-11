from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from runner.child import INPUT_PREFIX, RESULT_PREFIX
from runner.results import RunResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class RunningStudentProcess:
    process: subprocess.Popen[str]
    started_at: float
    timeout: float | None

    def cancel(self) -> None:
        if self.process.poll() is None:
            self.process.kill()
        self.process.communicate()

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


class InteractiveStudentProcess(RunningStudentProcess):
    """Drain child pipes off the UI thread; only polling mutates visible state."""

    def __init__(self, process, started_at, timeout):
        super().__init__(process, started_at, timeout)
        self.waiting_for_input = False
        self.output = ""
        self._messages = queue.Queue()
        self._stdout_done = threading.Event()
        self._stderr_done = threading.Event()
        self._stderr = ""
        self._result = None
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self):
        try:
            for line in self.process.stdout:
                if line.startswith((INPUT_PREFIX, RESULT_PREFIX)):
                    self._messages.put(line)
        finally:
            self.process.stdout.close()
            self._stdout_done.set()

    def _read_stderr(self):
        try:
            while chunk := self.process.stderr.read(1024):
                self._stderr = (self._stderr + chunk)[-2000:]
        finally:
            self.process.stderr.close()
            self._stderr_done.set()

    def send_input(self, answer: str) -> None:
        if not self.waiting_for_input or "\n" in answer or "\r" in answer:
            raise ValueError("Expected one answer to a pending input request")
        self.process.stdin.write(answer + "\n")
        self.process.stdin.flush()
        self.waiting_for_input = False
        self.started_at = time.monotonic()

    def cancel(self) -> None:
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=2)
        self.process.stdin.close()
        self.waiting_for_input = False

    def poll_result(self) -> RunResult | None:
        while True:
            try:
                line = self._messages.get_nowait()
            except queue.Empty:
                break
            try:
                if line.startswith(INPUT_PREFIX):
                    self.output = json.loads(line[len(INPUT_PREFIX):])["output"]
                    self.waiting_for_input = True
                else:
                    self._result = RunResult.from_dict(json.loads(line[len(RESULT_PREFIX):]))
                    self.waiting_for_input = False
            except (KeyError, TypeError, ValueError):
                self._result = RunResult("error", "runner_error", "Не удалось прочитать результат запуска.")
        if self.process.poll() is not None:
            if not (self._stdout_done.is_set() and self._stderr_done.is_set()):
                return None
            # A reader can enqueue a final line between the drain and its done flag.
            if not self._messages.empty():
                return self.poll_result()
            self.process.stdin.close()
            self.waiting_for_input = False
            return self._result or RunResult(
                "error", "runner_error", "Не удалось прочитать результат запуска.", self._stderr,
            )
        if (
            not self.waiting_for_input and self.timeout is not None
            and time.monotonic() - self.started_at >= self.timeout
        ):
            self.cancel()
            return RunResult("error", "timeout", "Программа работает слишком долго. Проверь, не застряла ли она.", output=self.output)
        return None


def start_student_process(
    source: Path,
    *,
    mode: str,
    lesson_id: str | None = None,
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
    if mode == "check":
        if lesson_id is None or task_id is None:
            raise ValueError("Check mode requires lesson_id and task_id")
        command.extend(("--lesson", lesson_id, "--task", task_id))

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
        stdin=subprocess.PIPE if mode == "interactive" else subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    if mode == "interactive":
        return InteractiveStudentProcess(process, time.monotonic(), timeout)
    return RunningStudentProcess(process, time.monotonic(), timeout)


def run_check(
    source: Path,
    task_id: str,
    *,
    lesson_id: str,
    timeout: float = 5.0,
) -> RunResult:
    job = start_student_process(
        source,
        mode="check",
        lesson_id=lesson_id,
        task_id=task_id,
        timeout=timeout,
    )
    while True:
        result = job.poll_result()
        if result is not None:
            return result
        time.sleep(0.01)
