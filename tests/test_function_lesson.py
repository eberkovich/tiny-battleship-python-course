"""A10 task contracts through the production student subprocess checker."""

import ast
from pathlib import Path

import pytest

from launcher.controller import LauncherController
from launcher.course import load_course, load_sections
from runner.process import run_check


ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "lessons/a09"


def test_a10_explains_the_repetition_problem_before_deferring_execution_detail():
    sections = load_sections(LESSON / "lesson.md")
    intro = sections["intro"]
    assert intro.index('print("Проверка связи")') < intro.index("Если пока не совсем понятно")
    assert intro.index("Если пока не совсем понятно") < intro.index("def show_intro():")
    assert "В следующей статье" in intro
    course = load_course()
    lesson = course.lesson("a09")
    articles = [task.section for task in lesson.tasks if task.kind == "article"]
    assert articles[:2] == ["intro", "execution"]
    assert lesson.tasks[1].id == "a09_book"


def test_a10_references_use_only_established_no_argument_function_syntax():
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.Expr, ast.Call,
               ast.Name, ast.Constant, ast.Load)
    for source in (LESSON / "reference").glob("*.py"):
        tree = ast.parse(source.read_text())
        assert all(isinstance(node, allowed) for node in ast.walk(tree))
        assert all(not node.args and not node.keywords for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id == "print"))


@pytest.mark.parametrize("mutation,message", [
    ("unused", "Одна и та же функция"),
    ("extra_code", "строк с кодом"),
    ("typo", "остались опечатки"),
    ("divider", "три звёздочки"),
    ("order", "порядок"),
])
def test_book_rejects_output_only_or_incomplete_refactoring(tmp_path, mutation, message):
    source = (LESSON / "reference/book.py").read_text()
    if mutation == "unused":
        # Correct output plus an unused function does not demonstrate reuse.
        from lessons.a09.acceptance import EXPECTED
        output = "\n".join(EXPECTED["a09_book"])
        source = 'def unused():\n    print("unused")\n\n' + f"print({output!r})\n"
    elif mutation == "extra_code":
        source += "spare = 1\n"
    elif mutation == "typo":
        source = source.replace("Гермиона закатили", "Гермеона закатили")
    elif mutation == "divider":
        source = source.replace('print("***")', 'print("*")')
    else:
        source = source.replace('print("Локонс объявил конкурс на лучший портрет Локонса.")\nprint("Первое место занял Локонс.")',
                                'print("Первое место занял Локонс.")\nprint("Локонс объявил конкурс на лучший портрет Локонса.")')
    path = tmp_path / "answer.py"
    path.write_text(source)
    result = run_check(path, "a09_book", lesson_id="a09")
    assert result.status == "failed", result
    assert message in result.message


def test_book_accepts_another_function_name_quotes_and_comment_spacing(tmp_path):
    source = (LESSON / "reference/book.py").read_text()
    source = source.replace("roll_eyes", "look").replace('"', "'")
    source = "# My story\n\n" + source.replace("\n", "  # a comment\n\n")
    path = tmp_path / "answer.py"
    path.write_text(source)
    result = run_check(path, "a09_book", lesson_id="a09")
    assert result.passed, result


def test_book_gently_reports_the_users_misspelling_and_accepts_its_correction(tmp_path):
    correct = (LESSON / "reference/book.py").read_text().replace("roll_eyes", "h")
    path = tmp_path / "answer.py"
    path.write_text(correct.replace("Гермиона", "Гермеона"))
    result = run_check(path, "a09_book", lesson_id="a09")
    assert result.status == "failed"
    assert "остались опечатки" in result.message
    assert "Проверь внимательно" in result.message
    assert "Гермеона" in result.output
    assert "Гермиона" not in result.message

    path.write_text(correct)
    result = run_check(path, "a09_book", lesson_id="a09")
    assert result.passed, result
    assert "Гермеона" not in result.output


@pytest.mark.parametrize("task,source", [
    ("a09_ticket", 'print("Билет")\nprint("Место 8")\nprint("Билет")\nprint("Место 8")\n'),
    ("a09_window", 'def draw_window():\n' + "".join(f"    print({line!r})\n" for line in
       ("+---+---+", "|   |   |", "|   |   |", "+---+---+", "|   |   |", "|   |   |", "+---+---+")) + "\ndraw_window()\n"),
])
def test_function_tasks_reject_correct_output_without_the_requested_function_use(tmp_path, task, source):
    path = tmp_path / "answer.py"
    path.write_text(source)
    result = run_check(path, task, lesson_id="a09")
    assert result.status == "failed", result


def test_window_accepts_a_different_grouping_of_repeated_parts(tmp_path):
    path = tmp_path / "answer.py"
    path.write_text('''def frame():
    print("+---+---+")

def glass_row():
    print("|   |   |")
    print("|   |   |")

def draw_window():
    frame()
    glass_row()
    frame()
    glass_row()
    frame()

draw_window()
''')
    result = run_check(path, "a09_window", lesson_id="a09")
    assert result.passed, result


def test_a10_requires_the_capstone_and_each_of_its_own_activities(tmp_path):
    controller = LauncherController(tmp_path / "child")
    try:
        for lesson in controller.course.lessons:
            if lesson.id == "a09_bonus":
                break
            for task in lesson.tasks:
                if task.id in lesson.completion_tasks:
                    controller.progress.completed_tasks.add(task.id)
                    if task.kind == "question":
                        controller.progress.puzzle_answers[task.id] = task.correct_choice
        assert not controller.lesson_unlocked("a09")
        controller.progress.completed_tasks.add("a09_bonus_checkout")
        assert controller.lesson_unlocked("a09")
        controller.enter_lesson("a09")
        assert controller.current_lesson_label == "10"
        assert controller.current_task.id == "a09_intro"
        controller.select_task("a09_summary")
        assert controller.current_task.id == "a09_intro"
        for task_id in controller.lesson.completion_tasks[:-1]:
            controller.progress.completed_tasks.add(task_id)
            task = controller.lesson.task(task_id)
            if task.kind == "question":
                controller.progress.puzzle_answers[task_id] = task.correct_choice
        assert not controller.lesson_complete()
        controller.progress.completed_tasks.add("a09_window")
        assert controller.lesson_complete()
        controller.select_task("a09_summary")
        assert controller.current_task.id == "a09_summary"
        assert not controller.lesson_unlocked("a10")  # A11 has not been authored.
    finally:
        controller.shutdown()
