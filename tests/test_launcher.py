import os
import shutil
import subprocess
import time
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from launcher.app import LauncherApp, _markdown_blocks
from launcher.controller import LauncherController
from launcher.course import Lesson, Task, load_course
from launcher.editor import editor_command, ensure_russian_thonny_config
from launcher.theme import DARK_THEME_NAME, LIGHT_THEME_NAME
from runner.results import RunResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ImmediateJob:
    def __init__(self, result: RunResult):
        self.result = result
        self.process = None

    def poll_result(self) -> RunResult:
        return self.result


def test_markdown_divider_splits_content_without_becoming_text() -> None:
    blocks = _markdown_blocks("Первый блок\n\n---\n\nВторой блок")

    assert blocks == [
        ("text", "Первый блок"),
        ("divider", ""),
        ("text", "Второй блок"),
    ]


def test_markdown_note_is_a_distinct_content_block() -> None:
    blocks = _markdown_blocks(
        "Покажи промах.\n\n"
        "> [!NOTE]\n"
        "> Открой редактор → выполни задание → сохрани изменения → "
        "нажми **«Запустить»**."
    )

    assert blocks == [
        ("text", "Покажи промах."),
        (
            "note",
            "Открой редактор → выполни задание → сохрани изменения → "
            "нажми **«Запустить»**.",
        ),
    ]


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


def test_console_run_shows_output_without_opening_game_ui(tmp_path: Path) -> None:
    course = load_course()
    lesson = course.lessons[0]
    console_task = replace(lesson.task("exercise_01"), run_mode="console")
    console_lesson = replace(
        lesson,
        tasks=tuple(
            console_task if task.id == console_task.id else task
            for task in lesson.tasks
        ),
    )
    calls = []

    def starter(source, **options):
        calls.append(options["mode"])
        return ImmediateJob(
            RunResult("passed", "passed", "Верно!", output="42")
        )

    controller = LauncherController(
        tmp_path / "student",
        course=replace(course, lessons=(console_lesson,)),
        process_starter=starter,
    )
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")
    controller.start_run()
    controller.poll()

    assert calls == ["check"]
    assert not controller.busy
    assert controller.latest_output == "42"
    assert controller.message == "Верно!"
    assert "exercise_01" in controller.progress.completed_tasks

    app = LauncherApp(controller)
    app.render()
    initial_rect = app.output_card_rect.copy()
    assert initial_rect.width == 700
    app.scroll = 120
    app.render()
    assert app.output_card_rect == initial_rect
    controller.toggle_theme()
    app.render()
    assert app.output_card_rect == initial_rect


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
    clickable_task_ids = {task_id for _, task_id in app.task_rects}
    assert clickable_task_ids == {
        task.id for task in controller.lesson.tasks if task.kind != "summary"
    }
    assert any(button.action == "next" for button in app.buttons)
    controller.select_task("exercise_01")
    app.render()
    actions = {button.action for button in app.buttons}
    assert actions >= {"home", "open", "run"}
    assert "play" not in actions
    assert "check" not in actions


def test_coding_note_stays_fixed_while_description_scrolls(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_03")
    app = LauncherApp(controller)

    app.render()
    initial_rect = app.note_card_rect.copy()
    assert initial_rect.width == 700
    assert initial_rect.height <= 60
    app.scroll = 160
    app.render()

    assert app.note_card_rect == initial_rect


def test_api_mention_opens_and_closes_signature_recap(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_03")
    app = LauncherApp(controller)
    app.render()

    link = next(link for link in app.api_links if link[1] == "show_miss")
    app._click(link[0].center)
    assert app.api_dialog == "show_miss"

    app.render()
    close = next(button for button in app.buttons if button.action == "close_api")
    app._click(close.rect.center)
    assert app.api_dialog is None


def test_api_introduction_page_uses_inline_description_not_recap_links(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    app = LauncherApp(controller)

    for task_id, introduced_api in (
        ("api", "show_board"),
        ("coordinates", "draw_deck"),
        ("coordinates", "show_miss"),
    ):
        controller.select_task(task_id)
        app.render()
        assert introduced_api not in {name for _, name in app.api_links}

    for task_id, referenced_api in (
        ("exercise_01", "show_board"),
        ("exercise_02", "draw_deck"),
        ("exercise_03", "show_miss"),
    ):
        controller.select_task(task_id)
        app.render()
        assert referenced_api in {name for _, name in app.api_links}


def test_theme_switch_is_shared_by_every_screen_and_persisted(
    tmp_path: Path,
) -> None:
    student = tmp_path / "student"
    controller = LauncherController(student)
    app = LauncherApp(controller)
    app.render()

    assert controller.progress.theme == DARK_THEME_NAME
    switch = next(button for button in app.buttons if button.action == "theme")
    app._click(switch.rect.center)
    assert controller.progress.theme == LIGHT_THEME_NAME

    controller.enter_lesson("lesson_01")
    app.render()
    assert any(button.action == "theme" for button in app.buttons)
    assert LauncherController(student).progress.theme == LIGHT_THEME_NAME


def test_opening_lesson_shows_saved_current_step(tmp_path: Path) -> None:
    student = tmp_path / "student"
    controller = LauncherController(student)
    controller.enter_lesson("lesson_01")
    assert controller.current_task.id == "intro"

    controller.select_task("coordinates")
    reopened = LauncherController(student)
    reopened.enter_lesson("lesson_01")

    assert reopened.current_task.id == "coordinates"


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
    assert app._progress_outline_color(segments[-1]) is None

    controller.select_task("star")
    controller.failed_tasks.add("star")
    star = app._progress_segments()[-1]
    assert star.state == "failed"
    assert star.selected
    assert app._progress_outline_color(star) is not None


def test_summary_has_its_own_kind_and_finish_color(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    app = LauncherApp(controller)

    controller.select_task("recap")
    assert controller.current_task.id != "recap"
    app.render()
    assert "recap" not in {task_id for _, task_id in app.task_rects}

    for task_id in controller.lesson.completion_tasks:
        controller.progress = controller.workspace.mark_passed(task_id)

    controller.select_task("recap")
    app.render()
    assert controller.current_task.kind == "summary"
    assert app._task_color(controller.current_task) == app.theme.summary
    assert not controller.current_task.is_coding
    assert "recap" in {task_id for _, task_id in app.task_rects}
    assert max(rect.bottom for rect, _ in app.task_rects) <= app.screen.get_height()


def test_next_lesson_stays_locked_until_previous_lesson_is_complete(
    tmp_path: Path,
) -> None:
    first_course = load_course()
    first = first_course.lessons[0]
    second_task = Task("lesson_02_intro", "article", "Новый урок", "api")
    second = Lesson(
        id="lesson_02",
        title="Второй урок",
        content=first.content,
        completion_tasks=(second_task.id,),
        tasks=(second_task,),
    )
    course = replace(first_course, lessons=(first, second))
    controller = LauncherController(tmp_path / "student", course=course)

    assert not controller.lesson_unlocked("lesson_02")
    controller.enter_lesson("lesson_02")
    assert controller.lesson.id == "lesson_01"

    for task_id in first.completion_tasks:
        controller.progress = controller.workspace.mark_passed(task_id)

    assert controller.lesson_unlocked("lesson_02")
    controller.enter_lesson("lesson_02")
    assert controller.lesson.id == "lesson_02"


def test_run_passes_selected_lesson_to_checker(tmp_path: Path) -> None:
    first_course = load_course()
    first = first_course.lessons[0]
    template = tmp_path / "lesson_02.py"
    template.write_text("from battleship_ui import *\n", encoding="utf-8")
    second_task = Task(
        "lesson_02_exercise_01",
        "exercise",
        "Новое упражнение",
        "api",
        student_file=Path("exercises/lesson_02/exercise_01.py"),
        template=template,
    )
    second = Lesson(
        id="lesson_02",
        title="Второй урок",
        content=first.content,
        completion_tasks=(second_task.id,),
        tasks=(second_task,),
    )
    calls = []

    def starter(source, **options):
        calls.append((source, options))
        return ImmediateJob(RunResult("passed", "passed", "Готово"))

    controller = LauncherController(
        tmp_path / "student",
        course=replace(first_course, lessons=(first, second)),
        process_starter=starter,
    )
    for task_id in first.completion_tasks:
        controller.progress = controller.workspace.mark_passed(task_id)
    controller.enter_lesson("lesson_02")
    controller.start_run()

    assert calls[0][1]["mode"] == "check"
    assert calls[0][1]["lesson_id"] == "lesson_02"
    assert calls[0][1]["task_id"] == "lesson_02_exercise_01"


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
