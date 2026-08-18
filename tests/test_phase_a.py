from pathlib import Path

import pytest

from launcher.course import load_course, load_sections
from launcher.workspace import StudentWorkspace
from runner.process import run_check


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COURSE = load_course()
PHASE_A_LESSONS = COURSE.lessons[1:7]
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
        f"lesson_{number:02d}" for number in range(2, 8)
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
        assert len(required_exercises) == 3
        assert content.count("> [!NOTE]") == len(coding)
        assert set(lesson.completion_tasks) <= {task.id for task in coding}
        assert lesson.tasks[-1].kind == "summary"


@pytest.mark.parametrize(
    "lesson_id,task_id",
    [
        ("lesson_02", "lesson_02_exercise_03"),
        ("lesson_03", "lesson_03_exercise_03"),
        ("lesson_04", "lesson_04_exercise_03"),
        ("lesson_05", "lesson_05_exercise_03"),
        ("lesson_06", "lesson_06_exercise_03"),
    ],
)
def test_debugging_exercise_starters_do_not_already_pass(
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
