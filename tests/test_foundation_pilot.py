"""Production pilot checks, independent of the infrastructure curriculum fixture."""

from dataclasses import replace
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest
import yaml

from launcher.app import GLOBAL_TOOLBAR_BOTTOM, LauncherApp
from launcher.controller import LauncherController
from launcher.course import CurriculumUnavailableError, load_course, load_sections
from runner.process import run_check


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COURSE = load_course()
CODING_TASKS = [
    (lesson, task) for lesson in COURSE.lessons for task in lesson.tasks if task.is_coding
]
QUESTIONS = [
    (lesson, task) for lesson in COURSE.lessons for task in lesson.tasks if task.kind == "question"
]


def test_pilot_scope_and_material_are_consistent() -> None:
    assert [lesson.id for lesson in COURSE.lessons] == ["a01", "a02", "a03"]
    assert len(COURSE.roadmap_lessons) == 32
    assert [len(lesson.completion_tasks) for lesson in COURSE.lessons] == [3, 5, 4]
    all_ids = set()
    for lesson in COURSE.lessons:
        sections = load_sections(lesson.content)
        for task in lesson.tasks:
            assert task.id.startswith(lesson.id + "_")
            assert task.id not in all_ids
            all_ids.add(task.id)
            assert task.section in sections
            assert task.title in sections[task.section]
            assert task.kind not in {"project", "star"}
            if task.is_coding:
                assert task.run_mode == "console"
                assert task.template.is_file()
                assert "battleship_ui" not in task.template.read_text()
        assert set(lesson.completion_tasks) == {
            task.id for task in lesson.tasks if task.is_coding or task.kind == "question"
        }


@pytest.mark.parametrize("lesson,task", CODING_TASKS, ids=[t.id for _, t in CODING_TASKS])
def test_reference_uses_student_checker(lesson, task) -> None:
    reference = PROJECT_ROOT / "lessons" / lesson.id / "reference" / task.template.name
    result = run_check(reference, task.id, lesson_id=lesson.id)
    assert result.passed, result


def specification_comments(text: str) -> list[str]:
    """Normalize only supported markup; protect the complete starter-copy contract."""
    blocks = text.split("> [!NOTE]", 1)[0].replace("**", "").replace("`", "")
    lines = []
    for line in blocks.splitlines():
        if "[!EXAMPLE]" in line:
            continue
        if line.startswith("## "):
            line = line[3:]
        if line.startswith(">"):
            line = line[1:].removeprefix(" ")
        if line not in {"python", "text"}:
            lines.append(line)
    return [line for line in lines if line.strip()]


@pytest.mark.parametrize("lesson,task", CODING_TASKS, ids=[t.id for _, t in CODING_TASKS])
def test_starters_contain_complete_task_without_workflow(lesson, task) -> None:
    content = load_sections(lesson.content)[task.section]
    comments = [
        line.removeprefix("#").removeprefix(" ")
        for line in task.template.read_text().splitlines() if line.startswith("#")
    ]
    assert " ".join(comments).split() == " ".join(specification_comments(content)).split()
    assert "Открой редактор" not in task.template.read_text()


@pytest.mark.parametrize("lesson,task", QUESTIONS, ids=[t.id for _, t in QUESTIONS])
@pytest.mark.parametrize("correct", [True, False], ids=["correct", "incorrect"])
def test_submitted_puzzle_feedback_completion_and_reopening(tmp_path, lesson, task, correct) -> None:
    controller = LauncherController(tmp_path / "child", debug=False)
    # Unlock earlier lessons for this independent interaction test.
    for previous in COURSE.lessons[:COURSE.lessons.index(lesson)]:
        for activity in previous.tasks:
            if activity.kind == "question":
                controller.progress.puzzle_answers[activity.id] = activity.correct_choice
                controller.progress.completed_tasks.add(activity.id)
            elif activity.is_coding:
                controller.progress.completed_tasks.add(activity.id)
    controller.workspace.save_progress(controller.progress)
    controller.enter_lesson(lesson.id)
    controller.select_task(task.id)
    choice = task.correct_choice if correct else next(c.id for c in task.choices if c.id != task.correct_choice)
    before = controller.workspace.progress_path.read_bytes()
    controller.choose_answer(choice)
    assert controller.workspace.progress_path.read_bytes() == before
    assert not controller.task_passed(task)
    assert not controller.puzzle_feedback
    controller.submit_answer()
    assert controller.task_passed(task)
    assert task.explanation in controller.puzzle_feedback
    assert next(c.label for c in task.choices if c.id == task.correct_choice) in controller.puzzle_feedback
    feedback = controller.puzzle_feedback
    reopened = LauncherController(controller.workspace.root)
    reopened.enter_lesson(lesson.id)
    reopened.select_task(task.id)
    assert reopened.selected_answer == choice
    assert reopened.puzzle_feedback == feedback


def test_unanswered_puzzles_block_summary_and_next_lesson(tmp_path) -> None:
    controller = LauncherController(tmp_path / "child")
    controller.enter_lesson("a01")
    assert not controller.lesson_complete()
    controller.select_task("a01_summary")
    assert controller.current_task.id == "a01_intro"
    controller.submit_answer()  # No question/choice: no completion.
    for task_id in controller.lesson.completion_tasks[:-1]:
        controller.select_task(task_id)
        controller.choose_answer(controller.current_task.choices[0].id)
        controller.submit_answer()
    assert controller.lesson_status(controller.lesson) == "in_progress"
    assert not controller.lesson_unlocked("a02")
    assert not controller.task_unlocked(controller.lesson.task("a01_summary"))
    controller.select_task(controller.lesson.completion_tasks[-1])
    controller.choose_answer("yes")  # A wrong answer still completes this puzzle.
    controller.submit_answer()
    assert controller.lesson_complete()
    assert controller.lesson_unlocked("a02")
    controller.select_task("a01_summary")
    assert controller.current_task.id == "a01_summary"


def test_debug_answers_hints_and_navigation_do_not_persist(tmp_path) -> None:
    controller = LauncherController(tmp_path / "review", debug=True)
    before = controller.workspace.progress_path.read_bytes()
    controller.enter_lesson("a02")
    controller.select_task("a02_q_print")
    controller.choose_answer("quoted")
    controller.submit_answer()
    assert controller.puzzle_feedback
    controller.select_task("a02_houses")
    controller.reveal_hint()
    assert controller.revealed_hints["a02_houses"] == 1
    assert controller.workspace.progress_path.read_bytes() == before


def test_fresh_workspaces_are_independent_and_have_no_game_file(tmp_path) -> None:
    first = LauncherController(tmp_path / "first")
    second = LauncherController(tmp_path / "second")
    for controller in (first, second):
        assert not (controller.workspace.root / "battleship.py").exists()
        assert not controller.game_available
        assert len(list(controller.workspace.root.rglob("*.py"))) == 7
    first.enter_lesson("a01")
    first.select_task("a01_q_number")
    first.choose_answer("seven")
    first.submit_answer()
    assert not second.workspace.load_progress().completed_tasks


def test_legacy_completion_cannot_complete_replacement_tasks(tmp_path) -> None:
    root = tmp_path / "old child"
    root.mkdir()
    source = root / "battleship.py"
    source.write_text("# Preserve this game\n")
    (root / "progress.json").write_text(json.dumps({
        "version": 4, "current_lesson": "lesson_01", "current_task": "recap",
        "completed_tasks": ["exercise_01", "project", "lesson_02_project"],
    }))
    controller = LauncherController(root)
    assert not controller.lesson_complete()
    assert controller.current_task.id == "a01_intro"
    assert not controller.progress.completed_tasks
    assert source.read_text() == "# Preserve this game\n"


def test_invalid_saved_choice_does_not_complete_puzzle(tmp_path) -> None:
    controller = LauncherController(tmp_path / "child")
    controller.progress.completed_tasks.add("a01_q_number")
    controller.progress.puzzle_answers["a01_q_number"] = "deleted_choice"
    controller.workspace.save_progress(controller.progress)
    reopened = LauncherController(controller.workspace.root)
    assert "a01_q_number" not in reopened.progress.completed_tasks
    assert not reopened.progress.puzzle_answers
    empty = replace(reopened.lesson, completion_tasks=())
    assert not reopened.workspace.lesson_complete(empty, reopened.progress)


def test_answer_keys_have_independent_evidence() -> None:
    comments = subprocess.run([sys.executable, "-c", "# Покажи число 7"], capture_output=True, text=True, check=True)
    assert comments.stdout == ""
    calls = subprocess.run([sys.executable, "-c", 'print("print")\nprint(2)\n\n# print(7)\nprint(5)'], capture_output=True, text=True, check=True)
    assert calls.stdout.splitlines() == ["print", "2", "5"]
    houses = [(3, 2, 1), (2, 4, 1), (3, 1, 2), (3, 3, 1), (3, 2, 2), (4, 3, 1)]
    assert sum(cats == 3 and dogs > birds for cats, dogs, birds in houses) == 2
    assert 12 - 3 - 3 + 5 == 11
    solutions = [order for order in itertools.permutations((1, 2, 3, 4))
                 if order.index(1) < order.index(2)
                 and order.index(3) == order.index(2) + 1
                 and order.index(4) not in (0, 3)]
    assert solutions == [(1, 4, 2, 3)]


@pytest.mark.parametrize("source,lesson,task,code", [
    ("print(8", "a02", "a02_repair", "syntax_error"),
    ("print(1)", "a02", "a02_houses", "behavior_mismatch"),
    ("print(11)\nprint(11)", "a02", "a02_stickers", "behavior_mismatch"),
    ("print(1)\nprint(2)\nprint(3)", "a03", "a03_countdown", "behavior_mismatch"),
    ("print(1423)", "a03", "a03_race", "behavior_mismatch"),
])
def test_focused_failures_keep_programming_and_reasoning_distinct(tmp_path, source, lesson, task, code) -> None:
    path = tmp_path / "answer.py"
    path.write_text(source)
    result = run_check(path, task, lesson_id=lesson)
    assert not result.passed
    assert result.code == code
    if code == "syntax_error":
        assert "строке" in result.message
        assert "синтакс" not in result.message


def test_console_run_end_to_end_shows_output_and_does_not_open_game(tmp_path) -> None:
    controller = LauncherController(tmp_path / "review", debug=True)
    controller.enter_lesson("a03")
    controller.select_task("a03_race")
    shutil.copyfile(PROJECT_ROOT / "lessons/a03/reference/race.py", controller.source_path())
    controller.start_run()
    deadline = time.monotonic() + 5
    while controller.busy and time.monotonic() < deadline:
        controller.poll()
        time.sleep(0.01)
    assert not controller.busy
    assert controller.latest_output.splitlines() == ["1", "4", "2", "3"]
    assert controller.message_level == "success"
    assert controller.pending_check is None
    assert not controller.workspace.load_progress().completed_tasks


def test_full_pilot_progress_requires_every_activity_and_survives_reopening(tmp_path) -> None:
    controller = LauncherController(tmp_path / "child")
    for index, lesson in enumerate(COURSE.lessons):
        controller.enter_lesson(lesson.id)
        assert not controller.lesson_complete()
        for task_id in lesson.completion_tasks:
            controller.select_task(task_id)
            task = controller.current_task
            if task.kind == "question":
                controller.choose_answer(task.correct_choice)
                controller.submit_answer()
            else:
                reference = PROJECT_ROOT / "lessons" / lesson.id / "reference" / task.template.name
                shutil.copyfile(reference, controller.source_path())
                controller.start_run()
                deadline = time.monotonic() + 5
                while controller.busy and time.monotonic() < deadline:
                    controller.poll()
                    time.sleep(0.01)
                assert not controller.busy
                assert controller.message_level == "success", controller.message
            assert controller.task_passed(task)
        assert controller.lesson_complete()
        assert controller.completed_lesson_count == index + 1
        controller.select_task(lesson.tasks[-1].id)
    reopened = LauncherController(controller.workspace.root)
    assert reopened.current_task.id == "a03_summary"
    assert reopened.completed_lesson_count == 3
    assert not (reopened.workspace.root / "battleship.py").exists()


def test_puzzle_ui_collects_answer_reveals_feedback_and_marks_card(tmp_path) -> None:
    controller = LauncherController(tmp_path / "child")
    controller.enter_lesson("a01")
    controller.select_task("a01_q_number")
    app = LauncherApp(controller)
    app.render()
    assert not any(button.action in {"open", "run", "submit_answer", "next"} for button in app.buttons)
    assert len(app.answer_rects) == 3
    app._click(app.answer_rects[0][0].center)
    app.render()
    submit = next(button for button in app.buttons if button.action == "submit_answer")
    app._click(submit.rect.center)
    app.render()
    assert controller.task_passed(controller.current_task)
    assert app.puzzle_feedback_rect.height > 0
    assert app.puzzle_feedback_rect.top > GLOBAL_TOOLBAR_BOTTOM
    assert controller.current_task.id in app.task_status_rects
    assert any(button.action == "next" for button in app.buttons)
    assert not any(button.action == "submit_answer" for button in app.buttons)
    pygame.quit()


def test_hint_ui_reveals_in_order_without_progress_or_layout_changes(tmp_path) -> None:
    controller = LauncherController(tmp_path / "review", debug=True)
    controller.enter_lesson("a02")
    controller.select_task("a02_houses")
    app = LauncherApp(controller)
    app.scroll = 1_000_000
    app.render()
    before = controller.workspace.progress_path.read_bytes()
    note = app.note_card_rect.copy()
    button = next(button for button in app.buttons if button.action == "hint")
    assert not controller.revealed_hints
    app._click(button.rect.center)
    app.render()
    assert controller.revealed_hints["a02_houses"] == 1
    assert app.note_card_rect == note
    button = next(button for button in app.buttons if button.action == "hint")
    app._click(button.rect.center)
    app.render()
    assert controller.revealed_hints["a02_houses"] == 2
    assert not any(button.action == "hint" for button in app.buttons)
    assert not controller.task_passed(controller.current_task)
    assert controller.workspace.progress_path.read_bytes() == before
    pygame.quit()


@pytest.mark.parametrize("size", [(1180, 760), (1600, 1000)])
def test_pilot_layout_regions_do_not_overlap_at_supported_sizes(tmp_path, size) -> None:
    controller = LauncherController(tmp_path / "review", debug=True)
    app = LauncherApp(controller)
    app._resize_window(size)
    for lesson in COURSE.lessons:
        controller.enter_lesson(lesson.id)
        for task in lesson.tasks:
            controller.select_task(task.id)
            controller.latest_output = "1\n4\n2\n3" if task.is_coding else ""
            controller.message = "Проверь результат программы." if task.is_coding else ""
            for scroll in (0, 1_000_000):
                app.scroll = scroll
                app.render()
                bounds = app.screen.get_rect()
                assert bounds.contains(app.lesson_title_rect)
                assert app.lesson_title_rect.top > GLOBAL_TOOLBAR_BOTTOM
                for button in app.buttons:
                    assert bounds.contains(button.rect)
                for first, second in itertools.combinations(app.buttons, 2):
                    assert not first.rect.colliderect(second.rect), (task.id, first, second)
                for rect, _ in app.answer_rects:
                    assert rect.top >= 132
                    assert rect.bottom <= size[1] - 74
                if task.is_coding:
                    assert app.output_card_rect.bottom < app.note_card_rect.top
                    for button in app.buttons:
                        if button.action in {"open", "run", "next", "previous"}:
                            assert app.note_card_rect.bottom < button.rect.top
    app.command_reference_open = True
    app.render()
    close = next(button for button in app.buttons if button.action == "close_reference")
    assert len(app.reference_api_links) == 6
    assert all(rect.bottom < close.rect.top for rect, _ in app.reference_api_links)
    pygame.quit()


@pytest.mark.parametrize("change", ["no_choices", "duplicate_choice", "bad_answer", "no_explanation", "empty_required", "required_article"])
def test_metadata_rejects_incomplete_puzzle_contracts(tmp_path, change) -> None:
    raw = yaml.safe_load((PROJECT_ROOT / "CURRICULUM.yaml").read_text())
    lesson = raw["lessons"][0]
    question = next(task for task in lesson["tasks"] if task["kind"] == "question")
    if change == "no_choices":
        question["choices"] = []
    elif change == "duplicate_choice":
        question["choices"][1]["id"] = question["choices"][0]["id"]
    elif change == "bad_answer":
        question["correct_choice"] = "missing"
    elif change == "no_explanation":
        question["explanation"] = ""
    elif change == "empty_required":
        lesson["completion_tasks"] = []
    else:
        lesson["completion_tasks"] = [lesson["tasks"][0]["id"]]
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True))
    with pytest.raises(ValueError):
        load_course(path)


def test_missing_production_curriculum_still_has_reset_fallback(tmp_path, monkeypatch) -> None:
    import launcher.course
    monkeypatch.setattr(launcher.course, "PROJECT_ROOT", tmp_path)
    with pytest.raises(CurriculumUnavailableError):
        load_course()
    with pytest.raises(FileNotFoundError):
        load_course(tmp_path / "explicit-missing.yaml")
