import os
import shutil
import subprocess
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from launcher.app import SUMMARY, LauncherApp
from launcher.controller import LauncherController
from launcher.editor import editor_command, ensure_russian_thonny_config
from runner.results import RunResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ImmediateJob:
    def __init__(self, result: RunResult):
        self.result = result
        self.process = None

    def poll_result(self) -> RunResult:
        return self.result


def test_editor_command_passes_exact_cyrillic_path_without_shell(tmp_path: Path) -> None:
    source = tmp_path / "Ученик 1" / "мой код.py"
    command = editor_command(source)

    assert command[-1] == str(source.resolve())
    assert command[1:3] == ["-m", "thonny"]


def test_thonny_is_preconfigured_in_russian_without_overwriting(
    tmp_path: Path,
) -> None:
    configuration = ensure_russian_thonny_config(tmp_path / "thonny")
    assert "language = ru_RU" in configuration.read_text(encoding="utf-8")

    configuration.write_text("[general]\nlanguage = en_US\n", encoding="utf-8")
    ensure_russian_thonny_config(tmp_path / "thonny")
    assert "en_US" in configuration.read_text(encoding="utf-8")


def test_child_facing_editor_message_hides_tool_and_filename(tmp_path: Path) -> None:
    opened = []
    controller = LauncherController(
        tmp_path / "student", editor_opener=lambda source: opened.append(source)
    )
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")

    controller.open_code()

    assert opened == [controller.source_path()]
    assert "редактор" in controller.message.lower()
    assert "thonny" not in controller.message.lower()
    assert ".py" not in controller.message.lower()


def test_single_run_checks_then_opens_real_ui_and_updates_progress(
    tmp_path: Path,
) -> None:
    calls = []

    def starter(source, **options):
        calls.append((source, options))
        code = "passed" if options["mode"] == "check" else "played"
        return ImmediateJob(RunResult("passed", code, "Готово"))

    controller = LauncherController(tmp_path / "Иван", process_starter=starter)
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")
    controller.start_run()
    controller.poll()
    assert controller.busy
    assert "exercise_01" in controller.progress.completed_tasks
    assert calls[0][1]["mode"] == "check"
    assert calls[1][1]["mode"] == "play"
    controller.poll()
    assert not controller.busy
    assert controller.message == "Готово"

    app = LauncherApp(controller)
    app.render()
    assert any(button.action == "next" for button in app.buttons)


def test_behavior_failure_still_opens_real_ui_and_preserves_progress(
    tmp_path: Path,
) -> None:
    calls = []

    def starter(source, **options):
        calls.append(options["mode"])
        if options["mode"] == "check":
            return ImmediateJob(
                RunResult("failed", "behavior_mismatch", "Попробуй ещё")
            )
        return ImmediateJob(RunResult("passed", "played", "Игра закрыта"))

    controller = LauncherController(tmp_path / "student", process_starter=starter)
    controller.enter_lesson("lesson_01")
    controller.select_task("project")
    controller.start_run()
    controller.poll()
    assert controller.busy
    controller.poll()

    assert "project" not in controller.progress.completed_tasks
    assert "project" in controller.failed_tasks
    assert calls == ["check", "play"]
    assert controller.message == "Попробуй ещё"


def test_technical_failure_is_not_run_again_with_real_ui(tmp_path: Path) -> None:
    calls = []

    def starter(source, **options):
        calls.append(options["mode"])
        return ImmediateJob(
            RunResult("error", "syntax_error", "Исправь код", "SyntaxError")
        )

    controller = LauncherController(tmp_path / "student", process_starter=starter)
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")
    controller.start_run()
    controller.poll()

    assert calls == ["check"]
    assert not controller.busy
    assert controller.message == "Исправь код"
    assert "exercise_01" in controller.failed_tasks


def test_launcher_renders_course_home_and_typed_lesson_navigation(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    app = LauncherApp(controller)
    app.render()

    assert len(app.lesson_rects) == 1
    assert not app.task_rects
    assert any(button.action == "continue" for button in app.buttons)

    controller.enter_lesson("lesson_01")
    app.render()
    assert len(app.task_rects) == len(controller.lesson.tasks)
    assert any(button.action == "next" for button in app.buttons)
    controller.select_task("exercise_01")
    app.render()
    actions = {button.action for button in app.buttons}
    assert actions >= {"home", "open", "run"}
    assert "play" not in actions
    assert "check" not in actions


def test_progress_models_every_coding_task_without_a_separate_star_counter(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    app = LauncherApp(controller)

    segments = app._progress_segments()

    assert [segment.task_id for segment in segments] == [
        "exercise_01",
        "exercise_02",
        "exercise_03",
        "project",
        "star",
    ]
    assert [segment.symbol for segment in segments] == [
        "number",
        "number",
        "number",
        "ship",
        "star",
    ]
    assert [segment.number for segment in segments] == [1, 2, 3, None, 4]
    assert segments[-1].optional

    controller.select_task("star")
    controller.failed_tasks.add("star")
    star = app._progress_segments()[-1]
    assert star.state == "failed"
    assert star.selected


def test_summary_has_its_own_kind_and_finish_color(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    controller.select_task("recap")
    app = LauncherApp(controller)

    assert controller.current_task.kind == "summary"
    assert app._task_color(controller.current_task) == SUMMARY
    assert not controller.current_task.is_coding


def test_run_command_initializes_cyrillic_student_workspace_end_to_end(
    tmp_path: Path,
) -> None:
    student = tmp_path / "Два ребёнка" / "Маша"
    environment = os.environ.copy()
    environment.update(
        {
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
            "BATTLESHIP_AUTOCLOSE_MS": "30",
        }
    )

    result = subprocess.run(
        [str(PROJECT_ROOT / "run.command"), "--student-dir", str(student)],
        cwd=PROJECT_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr
    assert (student / "battleship.py").exists()
    assert (student / "exercises/lesson_01/exercise_03.py").exists()
    assert (student / "progress.json").exists()


def test_combined_run_uses_real_subprocesses_end_to_end(
    tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("BATTLESHIP_AUTOCLOSE_MS", "30")
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")
    shutil.copyfile(
        PROJECT_ROOT / "lessons/lesson_01/reference/exercise_01.py",
        controller.source_path(),
    )

    controller.start_run()
    deadline = time.monotonic() + 5
    while controller.busy and time.monotonic() < deadline:
        controller.poll()
        time.sleep(0.01)

    assert not controller.busy
    assert "exercise_01" in controller.progress.completed_tasks
    assert controller.message_level == "success"
