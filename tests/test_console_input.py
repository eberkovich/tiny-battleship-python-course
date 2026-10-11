"""Real subprocess input transport and the foundation lessons' varied checks."""

import importlib
import os
from pathlib import Path
import shutil
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from launcher.app import GLOBAL_TOOLBAR_BOTTOM, LauncherApp, _markdown_blocks
from launcher.controller import LauncherController
from launcher.course import load_course
from launcher.theme import THEMES
from runner.process import run_check, start_student_process


ROOT = Path(__file__).resolve().parents[1]
COURSE = load_course()
INPUT_TASKS = [(lesson, task) for lesson in COURSE.lessons for task in lesson.tasks if task.run_mode == "interactive"]


def wait_for_input(job):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        result = job.poll_result()
        assert result is None, result
        if job.waiting_for_input:
            return
        time.sleep(0.01)
    pytest.fail("No input request from the child")


def finish(job):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        result = job.poll_result()
        if result is not None:
            return result
        time.sleep(0.01)
    job.cancel()
    pytest.fail("Child did not finish")


@pytest.mark.parametrize("answer", ["Луна", "7", "two words", "", "🦉"])
def test_input_waits_without_blocking_and_preserves_literal_answer(tmp_path, answer):
    source = tmp_path / "read.py"
    source.write_text('print("Вопрос")\nanswer = input()\nprint("Ответ:", answer)\n')
    job = start_student_process(source, mode="interactive", timeout=0.8)
    try:
        wait_for_input(job)
        assert job.output == "Вопрос\n"
        # A child's thinking time must not become a timeout.
        job.started_at -= 60
        before = time.monotonic()
        assert job.poll_result() is None
        assert time.monotonic() - before < 0.1
        assert job.process.poll() is None
        job.send_input(answer)
        result = finish(job)
        assert result.passed
        assert result.output == f"Вопрос\nОтвет: {answer}\n"
        assert "BATTLESHIP_" not in result.output
    finally:
        job.cancel()


def test_sequential_input_and_prompt_argument(tmp_path):
    source = tmp_path / "read.py"
    source.write_text('one = input("Первый? ")\nprint("Второй?")\ntwo = input()\nprint(one, two)\n')
    job = start_student_process(source, mode="interactive", timeout=1)
    try:
        wait_for_input(job)
        assert job.output == "Первый? "
        job.send_input("А")
        wait_for_input(job)
        assert job.output == "Первый? Второй?\n"
        job.send_input("Б")
        assert finish(job).output == "Первый? Второй?\nА Б\n"
    finally:
        job.cancel()


def test_cancel_reaps_waiting_child(tmp_path):
    source = tmp_path / "read.py"
    source.write_text("input()\n")
    job = start_student_process(source, mode="interactive", timeout=1)
    wait_for_input(job)
    job.cancel()
    assert job.process.poll() is not None
    assert not job.waiting_for_input


def test_timeout_resumes_after_answer(tmp_path):
    source = tmp_path / "loop.py"
    source.write_text("input()\nwhile True:\n    pass\n")
    job = start_student_process(source, mode="interactive", timeout=0.8)
    try:
        wait_for_input(job)
        job.send_input("go")
        job.started_at -= 60
        result = job.poll_result()
        assert result.code == "timeout"
        assert job.process.poll() is not None
    finally:
        job.cancel()


def test_invalid_conversion_explains_error_without_losing_output(tmp_path):
    source = tmp_path / "number.py"
    source.write_text('print("Число?")\nanswer = input()\nnumber = int(answer)\nprint(number)\n')
    job = start_student_process(source, mode="interactive", timeout=1)
    try:
        wait_for_input(job)
        job.send_input("кот")
        result = finish(job)
        assert result.code == "value_error"
        assert "int" in result.message
        assert result.output == "Число?\n"
    finally:
        job.cancel()


@pytest.mark.parametrize("lesson,task", INPUT_TASKS, ids=[task.id for _, task in INPUT_TASKS])
def test_private_cases_reject_a_hardcoded_first_answer(tmp_path, lesson, task):
    acceptance = importlib.import_module(f"lessons.{lesson.id}.acceptance")
    answers = acceptance.input_cases(task.id)[0]
    reference = ROOT / "lessons" / lesson.id / "reference" / task.template.name
    # Execute once to obtain one correct result, then hard-code it after reads.
    import subprocess
    import sys
    observed = subprocess.run(
        [sys.executable, str(reference)], input="\n".join(answers) + "\n",
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()[len(answers):]
    source = tmp_path / "constant.py"
    source.write_text("input()\n" * len(answers) + "\n".join(f"print({line!r})" for line in observed) + "\n")
    result = run_check(source, task.id, lesson_id=lesson.id)
    assert result.code == "behavior_mismatch"


@pytest.mark.parametrize("source", ["print(18)", "input()\ninput()\nprint(18)"])
def test_private_cases_require_exact_read_count(tmp_path, source):
    path = tmp_path / "answer.py"
    path.write_text(source + "\n")
    assert run_check(path, "a09_input_birthday", lesson_id="a09_input").code == "behavior_mismatch"


@pytest.mark.parametrize("hens,sheep", [(5, 3), (0, 11), (9, 0), (43, 21)])
def test_farm_reference_conserves_population_and_legs(hens, sheep):
    import subprocess
    import sys
    animals, legs = hens + sheep, hens * 2 + sheep * 4
    result = subprocess.run(
        [sys.executable, str(ROOT / "lessons/a09_input/reference/farm.py")],
        input=f"{animals}\n{legs}\n", capture_output=True, text=True, check=True,
    )
    assert result.stdout.splitlines()[-2:] == [str(hens), str(sheep)]


def test_other_valid_number_trick_strategy_passes(tmp_path):
    source = tmp_path / "trick.py"
    source.write_text("answer = input()\nresult = int(answer)\nprint((result - 1) // 2)\n")
    assert run_check(source, "a09_input_number_trick", lesson_id="a09_input").passed


def drive_controller(controller, answers):
    remaining = iter(answers)
    deadline = time.monotonic() + 4
    while controller.busy and time.monotonic() < deadline:
        controller.poll()
        if controller.waiting_for_input:
            controller.submit_input(next(remaining))
        time.sleep(0.01)
    assert not controller.busy


def test_controller_checks_changed_inputs_but_retains_actual_output(tmp_path):
    controller = LauncherController(tmp_path / "child", debug=True)
    controller.enter_lesson("a09_input")
    controller.select_task("a09_input_birthday")
    shutil.copyfile(ROOT / "lessons/a09_input/reference/birthday.py", controller.source_path())
    controller.start_run()
    drive_controller(controller, ["2015"])
    assert controller.message_level == "success"
    assert controller.latest_output.splitlines() == ["В каком году ты родился?", "20"]
    assert not controller.workspace.load_progress().completed_tasks
    # A hard-coded program can look correct for one run, but must not pass.
    controller.source_path().write_text('print("Год?")\nyear = input()\nprint(20)\n')
    controller.start_run()
    drive_controller(controller, ["2015"])
    assert controller.message_level == "error"
    assert controller.latest_output == "Год?\n20\n"


def test_input_dialog_handles_unicode_enter_and_fits_shared_layout(tmp_path):
    controller = LauncherController(tmp_path / "child", debug=True)
    controller.enter_lesson("a08")
    controller.select_task("a08_introduce")
    shutil.copyfile(ROOT / "lessons/a08/reference/introduce.py", controller.source_path())
    app = LauncherApp(controller)
    controller.start_run()
    try:
        wait_for_input(controller.job)
        controller.poll()
        for theme in THEMES:
            controller.progress.theme = theme
            for size in [(1180, 760), (1600, 1000)]:
                app._resize_window(size)
                app.render()
                assert app.input_dialog_rect.top > GLOBAL_TOOLBAR_BOTTOM
                assert app.input_dialog_rect.contains(app.input_field_rect)
                actions = [button for button in app.buttons if button.action in {"send_input", "cancel_input"}]
                assert len(actions) == 2
                for button in actions:
                    assert app.input_dialog_rect.contains(button.rect)
                    assert not button.rect.colliderect(app.input_field_rect)
        app._handle_input_event(pygame.event.Event(pygame.TEXTINPUT, text="Соваа"))
        app._handle_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
        assert app.input_text == "Сова"
        app._handle_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        drive_controller(controller, [])
        assert controller.latest_output.splitlines()[-1] == "Сова"
        assert controller.message_level == "success"
        app.render()
        assert app.input_dialog_rect is None
    finally:
        controller.shutdown()
        pygame.quit()


def test_input_examples_do_not_render_answers_as_python():
    assert _markdown_blocks("```input\nЛуна\n```") == [("input", "Луна")]


def test_escape_cancels_input_without_marking_completion(tmp_path):
    controller = LauncherController(tmp_path / "child", debug=True)
    controller.enter_lesson("a08")
    controller.select_task("a08_introduce")
    shutil.copyfile(ROOT / "lessons/a08/reference/introduce.py", controller.source_path())
    app = LauncherApp(controller)
    original_progress = controller.workspace.progress_path.read_bytes()
    controller.start_run()
    try:
        wait_for_input(controller.job)
        controller.poll()
        app.render()
        process = controller.job.process
        app._handle_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        app.render()
        assert not controller.busy
        assert process.poll() is not None
        assert app.input_dialog_rect is None
        assert controller.workspace.progress_path.read_bytes() == original_progress
    finally:
        controller.shutdown()
        pygame.quit()


def test_bad_typed_answer_is_not_copied_to_terminal_diagnostics(tmp_path, capsys):
    controller = LauncherController(tmp_path / "child", debug=True)
    controller.enter_lesson("a09_input")
    controller.select_task("a09_input_birthday")
    shutil.copyfile(ROOT / "lessons/a09_input/reference/birthday.py", controller.source_path())
    controller.start_run()
    drive_controller(controller, ["кот"])
    assert controller.message_level == "error"
    assert "int" in controller.message
    assert capsys.readouterr().err == ""
