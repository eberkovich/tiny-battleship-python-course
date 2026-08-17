import json
from pathlib import Path

from launcher.course import load_course, load_lesson, load_sections
from launcher.theme import DARK_THEME_NAME
from launcher.workspace import StudentWorkspace


def test_curriculum_and_sections_are_consistent() -> None:
    lesson = load_lesson()
    sections = load_sections(lesson.content)

    assert lesson.id == "lesson_01"
    assert [task.id for task in lesson.tasks if task.kind == "exercise"] == [
        "exercise_01",
        "exercise_02",
        "exercise_03",
    ]
    assert {task.section for task in lesson.tasks} <= sections.keys()


def test_curriculum_provides_clickable_api_recaps() -> None:
    course = load_course()

    assert set(course.api_references) == {"show_board", "draw_deck", "show_miss"}
    assert course.api_references["show_miss"].introduced_in == "api"
    assert course.api_references["show_miss"].signature == "show_miss(board, x, y)"
    assert course.api_references["show_miss"].details
    assert not course.api_reference_available("show_miss", "api")
    assert course.api_reference_available("show_miss", "exercise_03")


def test_workspace_initialization_preserves_existing_source(tmp_path: Path) -> None:
    course = load_course()
    workspace = StudentWorkspace(tmp_path / "Иван", course)
    workspace.initialize()
    project = workspace.source_path("project")
    project.write_text("# моя работа\n", encoding="utf-8")

    workspace.initialize()

    assert project.read_text(encoding="utf-8") == "# моя работа\n"
    assert workspace.source_path("exercise_03").exists()
    assert workspace.source_path("star").exists()


def test_progress_is_separate_for_exercises_project_and_star(tmp_path: Path) -> None:
    course = load_course()
    lesson = course.lessons[0]
    workspace = StudentWorkspace(tmp_path / "student", course)
    workspace.initialize()

    workspace.mark_passed("exercise_01")
    workspace.mark_passed("star")
    progress = workspace.load_progress()

    assert progress.completed_tasks == {"exercise_01"}
    assert progress.earned_stars == {"star"}
    assert not workspace.lesson_complete(lesson, progress)


def test_two_students_have_independent_source_and_progress(tmp_path: Path) -> None:
    course = load_course()
    first = StudentWorkspace(tmp_path / "Аня", course)
    second = StudentWorkspace(tmp_path / "Боря", course)
    first.initialize()
    second.initialize()

    first.source_path("project").write_text("# Анина игра\n", encoding="utf-8")
    first.mark_passed("project")

    assert second.source_path("project").read_text(encoding="utf-8") != "# Анина игра\n"
    assert "project" not in second.load_progress().completed_tasks


def test_version_one_progress_is_migrated_without_losing_passed_tasks(
    tmp_path: Path,
) -> None:
    course = load_course()
    workspace = StudentWorkspace(tmp_path / "student", course)
    workspace.root.mkdir()
    workspace.progress_path.write_text(
        json.dumps(
            {
                "version": 1,
                "current_task": "exercise_02",
                "completed_tasks": ["exercise_01"],
                "earned_stars": [],
            }
        ),
        encoding="utf-8",
    )

    progress = workspace.load_progress()

    assert progress.current_lesson == "lesson_01"
    assert progress.current_task == "exercise_02"
    assert progress.completed_tasks == {"exercise_01"}
    assert progress.theme == DARK_THEME_NAME


def test_version_two_progress_defaults_to_dark_theme(tmp_path: Path) -> None:
    course = load_course()
    workspace = StudentWorkspace(tmp_path / "student", course)
    workspace.root.mkdir()
    workspace.progress_path.write_text(
        json.dumps(
            {
                "version": 2,
                "current_lesson": "lesson_01",
                "current_task": "coordinates",
                "completed_tasks": ["exercise_01"],
                "earned_stars": [],
            }
        ),
        encoding="utf-8",
    )

    progress = workspace.load_progress()

    assert progress.current_task == "coordinates"
    assert progress.theme == DARK_THEME_NAME
