from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    title: str
    section: str
    student_file: Path | None = None
    template: Path | None = None

    @property
    def is_coding(self) -> bool:
        return self.student_file is not None


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    content: Path
    completion_tasks: tuple[str, ...]
    tasks: tuple[Task, ...]

    def task(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(task_id)


@dataclass(frozen=True)
class Course:
    title: str
    description: tuple[str, ...]
    lessons: tuple[Lesson, ...]

    def lesson(self, lesson_id: str) -> Lesson:
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        raise KeyError(lesson_id)

    def task(self, task_id: str) -> tuple[Lesson, Task]:
        for lesson in self.lessons:
            for task in lesson.tasks:
                if task.id == task_id:
                    return lesson, task
        raise KeyError(task_id)


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing text field: {key}")
    return value


def load_course(curriculum_path: Path | None = None) -> Course:
    path = curriculum_path or PROJECT_ROOT / "CURRICULUM.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or not raw.get("lessons"):
        raise ValueError("Curriculum version 1 requires at least one lesson")

    lessons = []
    task_ids: set[str] = set()
    for lesson_data in raw["lessons"]:
        tasks = []
        for item in lesson_data["tasks"]:
            student_file = item.get("student_file")
            template = item.get("template")
            task = Task(
                id=_required_text(item, "id"),
                kind=_required_text(item, "kind"),
                title=_required_text(item, "title"),
                section=_required_text(item, "section"),
                student_file=Path(student_file) if student_file else None,
                template=PROJECT_ROOT / template if template else None,
            )
            if task.id in task_ids:
                raise ValueError(f"Task IDs must be unique across the course: {task.id}")
            task_ids.add(task.id)
            tasks.append(task)
        lessons.append(
            Lesson(
                id=_required_text(lesson_data, "id"),
                title=_required_text(lesson_data, "title"),
                content=PROJECT_ROOT / _required_text(lesson_data, "content"),
                completion_tasks=tuple(lesson_data["completion_tasks"]),
                tasks=tuple(tasks),
            )
        )

    course_data = raw.get("course", {})
    description = course_data.get("description")
    if not isinstance(description, list) or not all(
        isinstance(line, str) and line for line in description
    ):
        raise ValueError("Course description must be a non-empty list of text")
    return Course(
        title=_required_text(course_data, "title"),
        description=tuple(description),
        lessons=tuple(lessons),
    )


def load_lesson(
    curriculum_path: Path | None = None, lesson_id: str | None = None
) -> Lesson:
    course = load_course(curriculum_path)
    return course.lesson(lesson_id) if lesson_id else course.lessons[0]


def load_sections(path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- section:") and stripped.endswith("-->"):
            current = stripped[len("<!-- section:") : -len("-->")].strip()
            if not current or current in sections:
                raise ValueError(f"Invalid or duplicate lesson section: {current}")
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}
