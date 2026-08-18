import json
import tomllib
from pathlib import Path

import pytest

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
    assert course.api_references["draw_deck"].introduced_in == "coordinates"
    assert course.api_references["show_miss"].introduced_in == "coordinates"
    assert course.api_references["show_miss"].signature == "show_miss(board, x, y)"
    assert course.api_references["show_miss"].details
    assert not course.api_reference_available("show_miss", "coordinates")
    assert course.api_reference_available("show_miss", "exercise_03")


def test_curriculum_loads_console_run_mode(tmp_path: Path) -> None:
    curriculum = tmp_path / "curriculum.yaml"
    curriculum.write_text(
        """
version: 1
course:
  title: "Курс"
  description: ["Описание"]
lessons:
  - id: lesson_01
    title: "Урок"
    content: unused.md
    completion_tasks: [exercise]
    tasks:
      - id: exercise
        kind: exercise
        title: "Упражнение"
        section: exercise
        student_file: exercise.py
        run_mode: console
""".strip(),
        encoding="utf-8",
    )

    course = load_course(curriculum)

    assert course.lessons[0].tasks[0].run_mode == "console"


def test_curriculum_rejects_unknown_run_mode(tmp_path: Path) -> None:
    curriculum = tmp_path / "curriculum.yaml"
    curriculum.write_text(
        """
version: 1
course:
  title: "Курс"
  description: ["Описание"]
lessons:
  - id: lesson_01
    title: "Урок"
    content: unused.md
    completion_tasks: [exercise]
    tasks:
      - id: exercise
        kind: exercise
        title: "Упражнение"
        section: exercise
        student_file: exercise.py
        run_mode: paper
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown run mode"):
        load_course(curriculum)


def test_packaging_discovers_future_lesson_modules() -> None:
    configuration = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )

    includes = configuration["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "lessons*" in includes


def test_curriculum_rejects_duplicate_task_ids(tmp_path: Path) -> None:
    curriculum = tmp_path / "curriculum.yaml"
    curriculum.write_text(
        """
version: 1
course:
  title: "Курс"
  description: ["Описание"]
lessons:
  - id: lesson_01
    title: "Урок"
    content: unused.md
    completion_tasks: []
    tasks:
      - {id: intro, kind: article, title: "Первый", section: intro}
      - {id: intro, kind: article, title: "Второй", section: second}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unique across the course"):
        load_course(curriculum)


def test_new_lesson_task_ids_must_include_lesson_prefix(tmp_path: Path) -> None:
    curriculum = tmp_path / "curriculum.yaml"
    curriculum.write_text(
        """
version: 1
course:
  title: "Курс"
  description: ["Описание"]
lessons:
  - id: lesson_01
    title: "Первый урок"
    content: unused.md
    completion_tasks: []
    tasks:
      - {id: intro, kind: article, title: "Первый", section: intro}
  - id: lesson_02
    title: "Второй урок"
    content: unused.md
    completion_tasks: []
    tasks:
      - {id: project, kind: project, title: "Проект", section: project}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must start with lesson_02_"):
        load_course(curriculum)


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
