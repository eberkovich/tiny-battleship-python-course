import ast
import io
from pathlib import Path
import re
import tokenize

import pytest

from launcher.course import load_course, load_sections
from launcher.workspace import StudentWorkspace
from runner.process import run_check


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COURSE = load_course()
PHASE_A_LESSONS = COURSE.lessons[1:]
REFERENCE_CASES = [
    (
        lesson.id,
        task.id,
        PROJECT_ROOT
        / "lessons"
        / lesson.id
        / "reference"
        / f"{task.id.removeprefix(f'{lesson.id}_')}.py",
    )
    for lesson in PHASE_A_LESSONS
    for task in lesson.tasks
    if task.is_coding
]


@pytest.mark.parametrize("lesson_id,task_id,source", REFERENCE_CASES)
def test_phase_a_reference_programs_pass(
    lesson_id: str, task_id: str, source: Path
) -> None:
    assert source.is_file()
    result = run_check(source, task_id, lesson_id=lesson_id)
    assert result.passed, result


def test_phase_a_curriculum_sections_and_task_contracts_are_complete() -> None:
    assert [lesson.id for lesson in PHASE_A_LESSONS] == [
        "lesson_01_coordinates",
        *[f"lesson_{number:02d}" for number in range(2, 8)],
    ]
    for lesson in PHASE_A_LESSONS:
        sections = load_sections(lesson.content)
        assert {task.section for task in lesson.tasks} <= sections.keys()
        coding = [task for task in lesson.tasks if task.is_coding]
        required_exercises = [
            task
            for task in lesson.tasks
            if task.kind == "exercise" and task.id in lesson.completion_tasks
        ]
        content = lesson.content.read_text(encoding="utf-8")
        assert 3 <= len(required_exercises) <= 4
        assert content.count("> [!NOTE]") == len(coding)
        assert set(lesson.completion_tasks) <= {task.id for task in coding}
        assert lesson.tasks[-1].kind == "summary"


@pytest.mark.parametrize(
    "lesson_id,focused_sequence",
    [
        (
            "lesson_01",
            (
                "comments",
                "exercise_comments",
                "exercise_01",
            ),
        ),
        (
            "lesson_01_coordinates",
            (
                "lesson_01_coordinates_coordinates",
                "lesson_01_coordinates_deck_api",
                "lesson_01_coordinates_exercise_01",
            ),
        ),
        (
            "lesson_02",
            (
                "lesson_02_output",
                "lesson_02_exercise_01",
                "lesson_02_variables",
                "lesson_02_exercise_02",
            ),
        ),
        (
            "lesson_03",
            (
                "lesson_03_address",
                "lesson_03_exercise_01",
                "lesson_03_unpacking",
                "lesson_03_exercise_02",
            ),
        ),
        (
            "lesson_04",
            (
                "lesson_04_lists",
                "lesson_04_exercise_01",
                "lesson_04_length",
                "lesson_04_exercise_length",
                "lesson_04_access",
                "lesson_04_exercise_02",
            ),
        ),
        (
            "lesson_05",
            (
                "lesson_05_empty",
                "lesson_05_exercise_empty",
                "lesson_05_append",
                "lesson_05_exercise_01",
            ),
        ),
        (
            "lesson_06",
            (
                "lesson_06_loop",
                "lesson_06_exercise_01",
                "lesson_06_indentation",
                "lesson_06_exercise_03",
                "lesson_06_addresses",
                "lesson_06_exercise_02",
            ),
        ),
        (
            "lesson_07",
            (
                "lesson_07_strings",
                "lesson_07_exercise_01",
                "lesson_07_button_api",
                "lesson_07_exercise_02",
            ),
        ),
    ],
)
def test_new_concepts_receive_focused_practice_before_the_next_one(
    lesson_id: str, focused_sequence: tuple[str, ...]
) -> None:
    task_ids = [task.id for task in COURSE.lesson(lesson_id).tasks]
    positions = [task_ids.index(task_id) for task_id in focused_sequence]

    assert positions == sorted(positions)


def test_every_lesson_example_is_an_explicit_single_callout() -> None:
    for lesson in COURSE.lessons:
        content = lesson.content.read_text(encoding="utf-8")
        in_example = False
        example_has_label = False
        example_count = 0

        for line in content.splitlines() + [""]:
            if line == "> [!EXAMPLE]":
                assert not in_example, lesson.id
                in_example = True
                example_has_label = False
                example_count += 1
                continue
            if in_example and not line.startswith(">"):
                assert example_has_label, lesson.id
                in_example = False
            if "**Пример:" in line or "**Например:" in line:
                assert in_example and line.startswith("> "), lesson.id
                example_has_label = True

        assert example_count > 0, lesson.id


def test_lesson_04_teaches_element_access_before_tasks_use_it() -> None:
    lesson = COURSE.lesson("lesson_04")
    task_order = [task.id for task in lesson.tasks]
    access_position = task_order.index("lesson_04_access")

    for task_id in (
        "lesson_04_exercise_02",
        "lesson_04_exercise_03",
        "lesson_04_project",
    ):
        assert access_position < task_order.index(task_id)

    access = load_sections(lesson.content)["access"]
    normalized_access = " ".join(access.split())
    assert "Индексы начинаются с нуля" in normalized_access
    assert "numbers[0]" in access
    assert "cells[1]" in access

    project_reference = (
        PROJECT_ROOT / "lessons/lesson_04/reference/project.py"
    ).read_text(encoding="utf-8")
    project_tree = ast.parse(project_reference)
    assert sum(isinstance(node, ast.Subscript) for node in ast.walk(project_tree)) == 3


def _normalized_instruction(text: str) -> str:
    goal = re.split(r"> \[!(?:RECAP|NOTE)\]", text, maxsplit=1)[0]
    goal = re.sub(r"(?m)^#+\s*", "", goal)
    goal = re.sub(r"(?m)^>\s?(?:\[!EXAMPLE\]\s*)?", "", goal)
    goal = goal.replace("`", "").replace("**", "")
    return " ".join(goal.split())


def _normalized_recap(text: str) -> str:
    marker = "> [!RECAP]"
    assert marker in text
    recap = text.split(marker, maxsplit=1)[1].split("> [!NOTE]", maxsplit=1)[0]
    recap = re.sub(r"(?m)^>\s?", "", recap)
    recap = recap.replace("`", "").replace("**", "")
    return " ".join(recap.split())


def test_isolated_task_starters_repeat_the_complete_visible_goal() -> None:
    for lesson in COURSE.lessons:
        sections = load_sections(lesson.content)
        for task in lesson.tasks:
            if task.kind not in {"exercise", "star"}:
                continue
            assert task.template is not None
            source = task.template.read_text(encoding="utf-8")
            comments = "\n".join(
                token.string.removeprefix("#").lstrip()
                for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type == tokenize.COMMENT
            )
            assert _normalized_instruction(sections[task.section]) in " ".join(
                comments.split()
            ), task.id
            normalized_comments = " ".join(comments.split())
            if "> [!RECAP]" in sections[task.section]:
                assert _normalized_recap(sections[task.section]) in (
                    normalized_comments
                ), task.id
            else:
                assert "На всякий случай:" not in normalized_comments, task.id


@pytest.mark.parametrize(
    "lesson_id,task_id",
    [
        ("lesson_02", "lesson_02_exercise_03"),
        ("lesson_03", "lesson_03_exercise_03"),
        ("lesson_04", "lesson_04_exercise_03"),
        ("lesson_05", "lesson_05_exercise_03"),
        ("lesson_06", "lesson_06_exercise_03"),
        ("lesson_07", "lesson_07_exercise_03"),
    ],
)
def test_debugging_exercise_starters_do_not_already_pass(
    lesson_id: str, task_id: str
) -> None:
    lesson, task = COURSE.task(task_id)

    assert lesson.id == lesson_id
    assert task.template is not None
    assert not run_check(task.template, task_id, lesson_id=lesson_id).passed


@pytest.mark.parametrize(
    "lesson_id,task_id",
    [
        ("lesson_01_coordinates", "lesson_01_coordinates_star"),
        ("lesson_06", "lesson_06_star"),
        ("lesson_07", "lesson_07_star"),
    ],
)
def test_star_challenge_starters_do_not_already_pass(
    lesson_id: str, task_id: str
) -> None:
    lesson, task = COURSE.task(task_id)

    assert lesson.id == lesson_id
    assert task.template is not None
    assert not run_check(task.template, task_id, lesson_id=lesson_id).passed


def test_public_api_introductions_exist_before_later_references() -> None:
    ordered_tasks = [
        (lesson, task) for lesson in COURSE.lessons for task in lesson.tasks
    ]
    task_order = [task.id for _, task in ordered_tasks]
    for api_name, reference in COURSE.api_references.items():
        if reference.introduced_in not in task_order:
            assert not any(
                api_name in load_sections(lesson.content)[task.section]
                for lesson, task in ordered_tasks
            )
            continue
        introduction = task_order.index(reference.introduced_in)
        introduction_lesson, introduction_task = COURSE.task(
            reference.introduced_in
        )
        assert api_name in load_sections(introduction_lesson.content)[
            introduction_task.section
        ]
        for lesson, task in ordered_tasks[:introduction]:
            assert api_name not in load_sections(lesson.content)[task.section]
            if task.template is not None:
                assert api_name not in task.template.read_text(encoding="utf-8")


def test_each_introduced_api_advances_the_same_lessons_project() -> None:
    task_ids = {
        task.id for lesson in COURSE.lessons for task in lesson.tasks
    }
    for api_name, reference in COURSE.api_references.items():
        if reference.introduced_in not in task_ids:
            continue
        lesson, _ = COURSE.task(reference.introduced_in)
        project = next(task for task in lesson.tasks if task.kind == "project")
        sections = load_sections(lesson.content)
        assert api_name in sections[project.section], (
            f"{api_name} is introduced in {lesson.id} but is not used in its project"
        )


def test_summaries_separate_practice_from_the_cumulative_game() -> None:
    for lesson in COURSE.lessons:
        summary = next(task for task in lesson.tasks if task.kind == "summary")
        content = load_sections(lesson.content)[summary.section].lower()
        assert "в упражнениях" in content, lesson.id
        assert "в твоей игре" in content, lesson.id


def test_workspace_adds_phase_a_exercises_without_overwriting_project(
    tmp_path: Path,
) -> None:
    workspace = StudentWorkspace(tmp_path / "student", COURSE)
    workspace.initialize()
    project = workspace.source_path("lesson_07_project")
    project.write_text("# моя игра\n", encoding="utf-8")

    workspace.initialize()

    assert project.read_text(encoding="utf-8") == "# моя игра\n"
    assert workspace.source_path("lesson_06_star").is_file()
    assert workspace.source_path("lesson_07_exercise_02").is_file()
