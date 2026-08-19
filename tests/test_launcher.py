import os
import shutil
import subprocess
import time
from dataclasses import replace
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from launcher.app import (
    GLOBAL_TOOLBAR_BOTTOM,
    HOME_SCROLL_VIEW_TOP,
    LauncherApp,
    _markdown_blocks,
)
from launcher.controller import LauncherController
from launcher.course import Lesson, Task, load_course
from launcher.editor import editor_command, ensure_idle_config
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
    assert command[1:4] == ["-m", "idlelib", "-e"]


def test_idle_uses_large_font_without_overwriting_existing_preference(
    tmp_path: Path,
) -> None:
    configuration = ensure_idle_config(tmp_path / "idle")
    content = configuration.read_text(encoding="utf-8")
    assert "font = Menlo" in content
    assert "font-size = 18" in content
    assert "font-bold = 0" in content

    configuration.write_text(
        "[EditorWindow]\nfont = Monaco\nfont-size = 22\nfont-bold = 1\n",
        encoding="utf-8",
    )
    ensure_idle_config(tmp_path / "idle")
    content = configuration.read_text(encoding="utf-8")
    assert "font = Monaco" in content
    assert "font-size = 22" in content
    assert "font-bold = 1" in content


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
    assert "idle" not in controller.message.lower()
    assert ".py" not in controller.message.lower()


def test_run_closes_launcher_owned_editor_before_checking(tmp_path: Path) -> None:
    events: list[str] = []

    class EditorProcess:
        def poll(self):
            return None

        def terminate(self):
            events.append("editor_closed")

        def wait(self, timeout):
            events.append("editor_waited")
            return 0

    def starter(source, **options):
        events.append("check_started")
        return ImmediateJob(RunResult("passed", "passed", "Верно!"))

    controller = LauncherController(
        tmp_path / "student",
        process_starter=starter,
        editor_opener=lambda source: EditorProcess(),
    )
    controller.enter_lesson("lesson_01")
    controller.select_task("exercise_01")
    controller.open_code()
    controller.start_run()

    assert events == ["editor_closed", "editor_waited", "check_started"]
    assert controller.editor_process is None


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


def test_game_button_appears_after_first_project_and_only_plays_current_game(
    tmp_path: Path,
) -> None:
    calls = []

    def starter(source, **options):
        calls.append((source, options))
        return ImmediateJob(
            RunResult(
                "error",
                "syntax_error",
                "В коде есть синтаксическая ошибка.",
                "SyntaxError",
            )
        )

    controller = LauncherController(
        tmp_path / "student",
        process_starter=starter,
    )
    app = LauncherApp(controller)
    app.render()
    assert not controller.game_available
    assert not any(button.action == "game" for button in app.buttons)

    controller.progress = controller.workspace.mark_passed("project")
    saved_progress = controller.progress.to_dict()
    app.render()
    game_button = next(button for button in app.buttons if button.action == "game")
    app._click(game_button.rect.center)

    assert controller.busy
    assert calls == [
        (
            controller.workspace.root / "battleship.py",
            {"mode": "play", "timeout": None},
        )
    ]
    controller.poll()
    assert not controller.busy
    assert controller.game_message == "В коде есть синтаксическая ошибка."
    assert controller.game_message_level == "error"
    assert controller.progress.to_dict() == saved_progress
    assert controller.workspace.load_progress().to_dict() == saved_progress


def test_successful_game_close_leaves_no_home_message(tmp_path: Path) -> None:
    def starter(source, **options):
        return ImmediateJob(RunResult("passed", "played", "Игра закрыта."))

    controller = LauncherController(
        tmp_path / "student",
        process_starter=starter,
        debug=True,
    )
    controller.start_game()
    controller.poll()

    assert controller.game_message == ""
    assert controller.game_message_level == "info"


def test_launcher_renders_course_home_and_typed_lesson_navigation(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    app = LauncherApp(controller)
    app.render()

    assert not app.lesson_rects
    assert not app.task_rects
    assert any(button.action == "continue" for button in app.buttons)
    toggle = next(button for button in app.buttons if button.action == "toggle_plan")
    app._click(toggle.rect.center)
    assert app.home_plan_expanded
    assert app.scroll > 0
    app.render()
    app.render()
    assert len(app.lesson_rects) == 1
    toggle = next(button for button in app.buttons if button.action == "toggle_plan")
    assert toggle.rect.top >= HOME_SCROLL_VIEW_TOP
    app._click(toggle.rect.center)
    assert not app.home_plan_expanded
    assert app.scroll == 0

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


def test_debug_mode_unlocks_every_lesson_and_step_without_saving_progress(
    tmp_path: Path,
) -> None:
    student = tmp_path / "debug-student"

    def starter(source, **options):
        return ImmediateJob(RunResult("passed", "passed", "Верно!", output="ok"))

    controller = LauncherController(
        student,
        process_starter=starter,
        debug=True,
    )
    saved_progress = controller.workspace.load_progress().to_dict()
    app = LauncherApp(controller)
    app.render()

    toggle = next(button for button in app.buttons if button.action == "toggle_plan")
    app._click(toggle.rect.center)
    app.render()
    assert len(app.lesson_rects) == len(controller.course.lessons)
    assert app.debug_badge_rect is not None
    assert all(
        controller.lesson_unlocked(lesson.id)
        for lesson in controller.course.lessons
    )

    controller.enter_lesson("lesson_07")
    controller.select_task("lesson_07_recap")
    assert controller.current_task.kind == "summary"

    controller.enter_lesson("lesson_02")
    controller.select_task("lesson_02_recap")
    app.render()
    assert any(button.action == "next_lesson" for button in app.buttons)

    controller.enter_lesson("lesson_07")
    controller.select_task("lesson_07_exercise_01")
    controller.toggle_theme()
    controller.start_run()
    controller.poll()

    assert controller.message == "Верно!"
    assert "lesson_07_exercise_01" not in controller.progress.completed_tasks
    assert controller.workspace.load_progress().to_dict() == saved_progress


def test_fixed_settings_toolbar_stays_above_page_content(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student", debug=True)
    app = LauncherApp(controller)

    app.render()
    settings_rects = [
        button.rect
        for button in app.buttons
        if button.action in {"game", "command_reference", "theme"}
    ]
    assert any(button.action == "game" for button in app.buttons)
    assert app.debug_badge_rect is not None
    settings_rects.append(app.debug_badge_rect)
    assert max(rect.bottom for rect in settings_rects) <= GLOBAL_TOOLBAR_BOTTOM
    assert all(
        not first.colliderect(second)
        for index, first in enumerate(settings_rects)
        for second in settings_rects[index + 1 :]
    )
    assert app.home_title_rect is not None
    assert app.home_title_rect.top > GLOBAL_TOOLBAR_BOTTOM

    controller.enter_lesson("lesson_01")
    app.render()
    home_button = next(button for button in app.buttons if button.action == "home")
    assert home_button.rect.top > GLOBAL_TOOLBAR_BOTTOM
    assert app.lesson_title_rect is not None
    assert app.lesson_title_rect.top > GLOBAL_TOOLBAR_BOTTOM
    assert all(rect.top > GLOBAL_TOOLBAR_BOTTOM for rect, _ in app.task_rects)


def test_roadmap_progress_uses_planned_lesson_count_and_blocks_future_lessons(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")

    assert controller.current_lesson_number == 1
    assert controller.total_lesson_count == 18
    assert controller.current_stage_number == 1
    assert controller.completed_lesson_count == 0
    assert controller.roadmap_lesson_status(
        controller.course.roadmap_lesson("lesson_08")
    ) == "future"

    for task_id in controller.lesson.completion_tasks:
        controller.progress = controller.workspace.mark_passed(task_id)

    assert controller.completed_lesson_count == 1


def test_debug_marks_unimplemented_roadmap_as_planned_not_locked(
    tmp_path: Path,
) -> None:
    normal = LauncherApp(LauncherController(tmp_path / "normal"))
    debug = LauncherApp(LauncherController(tmp_path / "debug", debug=True))
    future_stage = debug.controller.course.roadmap[1]

    assert normal._roadmap_stage_marker(future_stage) == "locked"
    assert normal._roadmap_entry_marker("future") == "locked"
    assert debug._roadmap_stage_marker(future_stage) == "planned"
    assert debug._roadmap_entry_marker("future") == "planned"


def test_launcher_cli_exposes_debug_flag() -> None:
    result = subprocess.run(
        [str(PROJECT_ROOT / ".venv/bin/python"), "-m", "launcher", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0
    assert "--debug" in result.stdout


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


def test_global_command_reference_lists_and_copies_every_api(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    app = LauncherApp(controller)
    copied: list[str] = []
    app._set_clipboard_text = copied.append
    app.render()

    reference_button = next(
        button for button in app.buttons if button.action == "command_reference"
    )
    app._click(reference_button.rect.center)
    app.render()

    assert app.command_reference_open
    assert {name for _, name in app.reference_api_links} == set(
        controller.course.api_references
    )
    assert len(app.copy_signature_links) == len(controller.course.api_references)

    show_board = controller.course.api_references["show_board"]
    copy_rect, signature = next(
        link for link in app.copy_signature_links if link[1] == show_board.signature
    )
    app._click(copy_rect.center)
    assert copied == [signature]
    assert app.copied_signature == signature
    assert not app.clipboard_error

    app.render()
    details_rect, _ = next(
        link for link in app.reference_api_links if link[1] == "show_board"
    )
    app._click(details_rect.center)
    assert app.api_dialog == "show_board"

    app.render()
    close_details = next(
        button for button in app.buttons if button.action == "close_api"
    )
    app._click(close_details.rect.center)
    assert app.api_dialog is None
    assert app.command_reference_open

    app.render()
    close_reference = next(
        button for button in app.buttons if button.action == "close_reference"
    )
    app._click(close_reference.rect.center)
    assert not app.command_reference_open

    controller.enter_lesson("lesson_01")
    app.render()
    assert any(
        button.action == "command_reference" for button in app.buttons
    )


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


def test_coding_task_icons_show_completion_and_latest_failure(
    tmp_path: Path,
) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    app = LauncherApp(controller)
    exercise = controller.lesson.task("exercise_01")
    project = controller.lesson.task("project")
    star = controller.lesson.task("star")
    article = controller.lesson.task("intro")

    assert not app._task_has_completion_badge(exercise)
    assert not app._task_has_completion_badge(article)
    controller.failed_tasks.add(exercise.id)
    assert app._task_has_failure_badge(exercise)
    assert not app._task_has_failure_badge(article)

    controller.progress = controller.workspace.mark_passed(exercise.id)
    assert app._task_has_completion_badge(exercise)
    assert not app._task_has_failure_badge(exercise)

    controller.progress = controller.workspace.mark_passed(project.id)
    assert app._task_has_completion_badge(controller.lesson.task("project"))
    assert not app._task_has_completion_badge(controller.lesson.task("star"))

    controller.progress = controller.workspace.mark_passed(star.id)
    assert app._task_has_completion_badge(controller.lesson.task("star"))

    failed = controller.lesson.task("exercise_02")
    controller.failed_tasks.add(failed.id)
    app.render()
    task_cards = {task_id: rect for rect, task_id in app.task_rects}
    assert article.id not in app.task_status_rects
    for task_id in {exercise.id, project.id, star.id, failed.id}:
        marker = app.task_status_rects[task_id]
        assert marker.size == (24, 24)
        assert marker.centerx > task_cards[task_id].centerx


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
    rendered_blocks: list[tuple[str, str]] = []
    app._render_markdown_blocks = (
        lambda blocks, rect: rendered_blocks.extend(blocks)
    )
    app.render()
    assert controller.current_task.kind == "summary"
    assert app._task_color(controller.current_task) == app.theme.summary
    assert not controller.current_task.is_coding
    assert "recap" in {task_id for _, task_id in app.task_rects}
    assert max(rect.bottom for rect, _ in app.task_rects) <= app.screen.get_height()
    next_lesson = controller.next_roadmap_lesson()
    assert next_lesson is not None
    number = controller.course.roadmap_position(next_lesson.id)
    rendered_text = [value for kind, value in rendered_blocks if kind == "text"]
    assert f"Дальше — урок {number}. {next_lesson.title}" in rendered_text
    assert next_lesson.outcome not in rendered_text


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


def test_completed_summary_opens_the_next_lesson(tmp_path: Path) -> None:
    controller = LauncherController(tmp_path / "student")
    controller.enter_lesson("lesson_01")
    for task_id in controller.lesson.completion_tasks:
        controller.progress = controller.workspace.mark_passed(task_id)
    controller.select_task("recap")
    app = LauncherApp(controller)
    app.render()

    button = next(
        button for button in app.buttons if button.action == "next_lesson"
    )
    app._click(button.rect.center)

    assert controller.lesson.id == "lesson_02"
    assert controller.current_task.id == "lesson_02_output"


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
