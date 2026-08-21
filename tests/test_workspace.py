import json
import tomllib
from dataclasses import replace
from pathlib import Path

import pytest

from launcher.course import Course, load_course, load_lesson, load_sections
from launcher.theme import DARK_THEME_NAME
from launcher.workspace import StudentWorkspace


def course_with_template(template: Path) -> Course:
    course = load_course()
    lesson = course.lessons[0]
    task = lesson.task("exercise_01")
    return replace(
        course,
        lessons=(
            replace(
                lesson,
                tasks=(replace(task, template=template),),
                completion_tasks=(task.id,),
            ),
        ),
    )


def test_curriculum_and_sections_are_consistent() -> None:
    lesson = load_lesson()
    sections = load_sections(lesson.content)

    assert lesson.id == "lesson_01"
    assert [task.id for task in lesson.tasks if task.kind == "exercise"] == [
        "exercise_comments",
        "exercise_01",
        "exercise_enemy",
    ]
    assert {task.section for task in lesson.tasks} <= sections.keys()


def test_curriculum_defines_complete_three_stage_roadmap() -> None:
    course = load_course()

    assert len(course.roadmap) == 3
    assert len(course.roadmap_lessons) == 19
    assert [stage.title for stage in course.roadmap] == [
        "Собираем флот",
        "Расставляем корабли",
        "Ход игры",
    ]
    assert [lesson.id for lesson in course.lessons] == [
        lesson.id for lesson in course.roadmap_lessons[: len(course.lessons)]
    ]


def test_curriculum_provides_clickable_api_recaps() -> None:
    course = load_course()

    assert set(course.api_references) == {
        "show_board",
        "draw_deck",
        "show_miss",
        "show_ship_count",
        "show_message",
    }
    assert course.api_references["draw_deck"].introduced_in == (
        "lesson_01_coordinates_deck_api"
    )
    assert course.api_references["show_miss"].introduced_in == (
        "lesson_14_first_shot"
    )
    assert course.api_references["show_miss"].signature == "show_miss(board, x, y)"
    assert course.api_references["show_miss"].details
    assert not course.api_reference_available("show_miss", "lesson_07_recap")
    assert course.api_references["show_ship_count"].introduced_in == (
        "lesson_02_counter"
    )
    assert course.api_references["show_message"].introduced_in == (
        "lesson_07_button_api"
    )


def test_curriculum_loads_console_run_mode(tmp_path: Path) -> None:
    curriculum = tmp_path / "curriculum.yaml"
    curriculum.write_text(
        """
version: 1
course:
  title: "Курс"
  goal: "Цель"
  promise: "Обещание"
  route: ["Начало", "Конец"]
  roadmap:
    - id: stage_01
      title: "Этап"
      summary: "Описание"
      lessons:
        - {id: lesson_01, title: "Урок", outcome: "Результат"}
lessons:
  - id: lesson_01
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
  goal: "Цель"
  promise: "Обещание"
  route: ["Начало", "Конец"]
  roadmap:
    - id: stage_01
      title: "Этап"
      summary: "Описание"
      lessons:
        - {id: lesson_01, title: "Урок", outcome: "Результат"}
lessons:
  - id: lesson_01
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
  goal: "Цель"
  promise: "Обещание"
  route: ["Начало", "Конец"]
  roadmap:
    - id: stage_01
      title: "Этап"
      summary: "Описание"
      lessons:
        - {id: lesson_01, title: "Урок", outcome: "Результат"}
lessons:
  - id: lesson_01
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
  goal: "Цель"
  promise: "Обещание"
  route: ["Начало", "Конец"]
  roadmap:
    - id: stage_01
      title: "Этап"
      summary: "Описание"
      lessons:
        - {id: lesson_01, title: "Первый урок", outcome: "Первый результат"}
        - {id: lesson_02, title: "Второй урок", outcome: "Второй результат"}
lessons:
  - id: lesson_01
    content: unused.md
    completion_tasks: []
    tasks:
      - {id: intro, kind: article, title: "Первый", section: intro}
  - id: lesson_02
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
    assert workspace.source_path("exercise_enemy").exists()
    assert workspace.source_path("lesson_01_coordinates_star").exists()


def test_workspace_refreshes_an_untouched_starter(tmp_path: Path) -> None:
    template = tmp_path / "starter.py"
    template.write_text("print('первая версия')\n", encoding="utf-8")
    workspace = StudentWorkspace(
        tmp_path / "student", course_with_template(template)
    )
    workspace.initialize()

    template.write_text("print('новая версия')\n", encoding="utf-8")
    workspace.initialize()

    assert workspace.source_path("exercise_01").read_text(encoding="utf-8") == (
        "print('новая версия')\n"
    )


def test_workspace_preserves_an_edited_starter_when_template_changes(
    tmp_path: Path,
) -> None:
    template = tmp_path / "starter.py"
    template.write_text("print('первая версия')\n", encoding="utf-8")
    workspace = StudentWorkspace(
        tmp_path / "student", course_with_template(template)
    )
    workspace.initialize()
    source = workspace.source_path("exercise_01")
    source.write_text("print('моя работа')\n", encoding="utf-8")

    template.write_text("print('новая версия')\n", encoding="utf-8")
    workspace.initialize()

    assert source.read_text(encoding="utf-8") == "print('моя работа')\n"


def test_workspace_preserves_an_untracked_legacy_file(tmp_path: Path) -> None:
    template = tmp_path / "starter.py"
    template.write_text("print('новая версия')\n", encoding="utf-8")
    workspace = StudentWorkspace(
        tmp_path / "student", course_with_template(template)
    )
    source = workspace.root / "exercises/lesson_01/exercise_01.py"
    source.parent.mkdir(parents=True)
    source.write_text("print('неизвестная старая работа')\n", encoding="utf-8")

    workspace.initialize()

    assert source.read_text(encoding="utf-8") == (
        "print('неизвестная старая работа')\n"
    )


def test_progress_is_separate_for_exercises_project_and_star(tmp_path: Path) -> None:
    course = load_course()
    lesson = course.lesson("lesson_01_coordinates")
    workspace = StudentWorkspace(tmp_path / "student", course)
    workspace.initialize()

    workspace.mark_passed("lesson_01_coordinates_exercise_01")
    workspace.mark_passed("lesson_01_coordinates_star")
    progress = workspace.load_progress()

    assert progress.completed_tasks == {"lesson_01_coordinates_exercise_01"}
    assert progress.earned_stars == {"lesson_01_coordinates_star"}
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

    assert progress.current_lesson == "lesson_01_coordinates"
    assert progress.current_task == "lesson_01_coordinates_exercise_01"
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

    assert progress.current_lesson == "lesson_01_coordinates"
    assert progress.current_task == "lesson_01_coordinates_coordinates"
    assert progress.theme == DARK_THEME_NAME


def test_existing_later_progress_stops_at_the_new_prerequisite_lesson(
    tmp_path: Path,
) -> None:
    course = load_course()
    workspace = StudentWorkspace(tmp_path / "student", course)
    workspace.root.mkdir()
    workspace.progress_path.write_text(
        json.dumps(
            {
                "version": 3,
                "current_lesson": "lesson_04",
                "current_task": "lesson_04_lists",
                "completed_tasks": ["exercise_01", "project", "exercise_02"],
                "earned_stars": ["star"],
                "theme": DARK_THEME_NAME,
            }
        ),
        encoding="utf-8",
    )

    progress = workspace.load_progress()

    assert progress.current_lesson == "lesson_01_coordinates"
    assert progress.current_task == "lesson_01_coordinates_coordinates"
    assert "project" in progress.completed_tasks
    assert "lesson_01_coordinates_exercise_01" in progress.completed_tasks
    assert progress.earned_stars == {"lesson_01_coordinates_star"}
