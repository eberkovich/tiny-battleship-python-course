from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CurriculumUnavailableError(ValueError):
    """No executable lessons are installed during the curriculum reset."""


@dataclass(frozen=True)
class AnswerChoice:
    id: str
    label: str


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    title: str
    section: str
    student_file: Path | None = None
    template: Path | None = None
    run_mode: str = "game"
    choices: tuple[AnswerChoice, ...] = ()
    correct_choice: str | None = None
    explanation: str = ""
    hints: tuple[str, ...] = ()

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
class RoadmapLesson:
    id: str
    title: str
    outcome: str


@dataclass(frozen=True)
class RoadmapStage:
    id: str
    title: str
    summary: str
    lessons: tuple[RoadmapLesson, ...]


@dataclass(frozen=True)
class ApiReference:
    introduced_in: str | None
    signature: str
    summary: str
    details: tuple[str, ...]


@dataclass(frozen=True)
class Course:
    title: str
    goal: str
    promise: str
    route: tuple[str, ...]
    roadmap: tuple[RoadmapStage, ...]
    lessons: tuple[Lesson, ...]
    api_references: dict[str, ApiReference]

    @property
    def roadmap_lessons(self) -> tuple[RoadmapLesson, ...]:
        return tuple(
            lesson for stage in self.roadmap for lesson in stage.lessons
        )

    def roadmap_lesson(self, lesson_id: str) -> RoadmapLesson:
        for lesson in self.roadmap_lessons:
            if lesson.id == lesson_id:
                return lesson
        raise KeyError(lesson_id)

    def roadmap_position(self, lesson_id: str) -> int:
        for index, lesson in enumerate(self.roadmap_lessons, start=1):
            if lesson.id == lesson_id:
                return index
        raise KeyError(lesson_id)

    def roadmap_stage(self, lesson_id: str) -> RoadmapStage:
        for stage in self.roadmap:
            if any(lesson.id == lesson_id for lesson in stage.lessons):
                return stage
        raise KeyError(lesson_id)

    def roadmap_stage_number(self, lesson_id: str) -> int:
        for index, stage in enumerate(self.roadmap, start=1):
            if any(lesson.id == lesson_id for lesson in stage.lessons):
                return index
        raise KeyError(lesson_id)

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

    def api_reference_available(self, api_name: str, task_id: str) -> bool:
        reference = self.api_references.get(api_name)
        if reference is None:
            return False
        introduction_seen = False
        for lesson in self.lessons:
            for task in lesson.tasks:
                if task.id == reference.introduced_in:
                    introduction_seen = True
                if task.id == task_id:
                    return introduction_seen and task.id != reference.introduced_in
        raise KeyError(task_id)


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing text field: {key}")
    return value


def load_course(curriculum_path: Path | None = None) -> Course:
    path = curriculum_path or PROJECT_ROOT / "CURRICULUM.yaml"
    if curriculum_path is None and not path.is_file():
        raise CurriculumUnavailableError(
            "Уроки сейчас перерабатываются. Новый курс ещё не готов."
        )
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or not raw.get("lessons"):
        raise ValueError("Curriculum version 1 requires at least one lesson")

    course_data = raw.get("course", {})
    route = course_data.get("route")
    if not isinstance(route, list) or len(route) < 2 or not all(
        isinstance(item, str) and item for item in route
    ):
        raise ValueError("Course route requires at least two text steps")

    roadmap_data = course_data.get("roadmap")
    if not isinstance(roadmap_data, list) or not roadmap_data:
        raise ValueError("Course roadmap requires at least one stage")
    roadmap: list[RoadmapStage] = []
    roadmap_stage_ids: set[str] = set()
    roadmap_lesson_ids: set[str] = set()
    for stage_data in roadmap_data:
        stage_id = _required_text(stage_data, "id")
        if stage_id in roadmap_stage_ids:
            raise ValueError(f"Roadmap stage IDs must be unique: {stage_id}")
        roadmap_stage_ids.add(stage_id)
        entries = stage_data.get("lessons")
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"Roadmap stage {stage_id} requires lessons")
        planned_lessons = []
        for entry in entries:
            planned = RoadmapLesson(
                id=_required_text(entry, "id"),
                title=_required_text(entry, "title"),
                outcome=_required_text(entry, "outcome"),
            )
            if planned.id in roadmap_lesson_ids:
                raise ValueError(
                    f"Roadmap lesson IDs must be unique: {planned.id}"
                )
            roadmap_lesson_ids.add(planned.id)
            planned_lessons.append(planned)
        roadmap.append(
            RoadmapStage(
                id=stage_id,
                title=_required_text(stage_data, "title"),
                summary=_required_text(stage_data, "summary"),
                lessons=tuple(planned_lessons),
            )
        )

    roadmap_lessons = tuple(
        lesson for stage in roadmap for lesson in stage.lessons
    )
    roadmap_by_id = {lesson.id: lesson for lesson in roadmap_lessons}

    lessons = []
    task_ids: set[str] = set()
    for lesson_data in raw["lessons"]:
        lesson_id = _required_text(lesson_data, "id")
        if lesson_id not in roadmap_by_id:
            raise ValueError(f"Implemented lesson is missing from roadmap: {lesson_id}")
        tasks = []
        for item in lesson_data["tasks"]:
            student_file = item.get("student_file")
            template = item.get("template")
            raw_choices = item.get("choices", [])
            raw_hints = item.get("hints", [])
            if not isinstance(raw_choices, list) or not all(
                isinstance(choice, dict) for choice in raw_choices
            ):
                raise ValueError("Puzzle choices must be a list of IDs and labels")
            if not isinstance(raw_hints, list) or not all(
                isinstance(hint, str) and hint.strip() for hint in raw_hints
            ):
                raise ValueError("Hints must be a list of text lines")
            choices = tuple(
                AnswerChoice(_required_text(choice, "id"), _required_text(choice, "label"))
                for choice in raw_choices
            )
            task = Task(
                id=_required_text(item, "id"),
                kind=_required_text(item, "kind"),
                title=_required_text(item, "title"),
                section=_required_text(item, "section"),
                student_file=Path(student_file) if student_file else None,
                template=PROJECT_ROOT / template if template else None,
                run_mode=str(item.get("run_mode", "game")),
                choices=choices,
                correct_choice=item.get("correct_choice"),
                explanation=(
                    _required_text(item, "explanation")
                    if item.get("kind") == "question" else ""
                ),
                hints=tuple(raw_hints),
            )
            if task.kind == "question":
                choice_ids = {choice.id for choice in choices}
                if (
                    task.is_coding or task.template is not None or len(choices) < 2
                    or len(choice_ids) != len(choices)
                    or not isinstance(task.correct_choice, str)
                    or task.correct_choice not in choice_ids
                    or not task.explanation.strip()
                ):
                    raise ValueError(f"Invalid answer-submission puzzle: {task.id}")
            elif choices or task.correct_choice or item.get("explanation"):
                raise ValueError(f"Answer choices require a question: {task.id}")
            if task.hints and not task.is_coding:
                raise ValueError(f"Hints require a coding task and text: {task.id}")
            if task.run_mode not in {"game", "console"}:
                raise ValueError(f"Unknown run mode for {task.id}: {task.run_mode}")
            if task.run_mode == "console" and not task.is_coding:
                raise ValueError(f"Console task requires a student file: {task.id}")
            if lesson_id != "lesson_01" and not task.id.startswith(
                f"{lesson_id}_"
            ):
                raise ValueError(
                    f"Task IDs after Lesson 1 must start with {lesson_id}_: "
                    f"{task.id}"
                )
            if task.id in task_ids:
                raise ValueError(f"Task IDs must be unique across the course: {task.id}")
            task_ids.add(task.id)
            tasks.append(task)
        required = tuple(lesson_data["completion_tasks"])
        lessons.append(
            Lesson(
                id=lesson_id,
                title=roadmap_by_id[lesson_id].title,
                content=PROJECT_ROOT / _required_text(lesson_data, "content"),
                completion_tasks=required,
                tasks=tuple(tasks),
            )
        )

    for lesson in lessons:
        activities = {
            task.id for task in lesson.tasks
            if (task.is_coding and task.kind != "star") or task.kind == "question"
        }
        if not lesson.completion_tasks or not set(lesson.completion_tasks) <= activities:
            raise ValueError(f"Lesson requires declared learning activities: {lesson.id}")

    implemented_ids = [lesson.id for lesson in lessons]
    planned_prefix = [
        lesson.id for lesson in roadmap_lessons[: len(implemented_ids)]
    ]
    if implemented_ids != planned_prefix:
        raise ValueError("Implemented lessons must be a prefix of the roadmap")

    api_references = {}
    for name, reference_data in raw.get("api_reference", {}).items():
        details = reference_data.get("details")
        if not isinstance(details, list) or not all(
            isinstance(line, str) and line for line in details
        ):
            raise ValueError(f"API reference {name} requires detail lines")
        api_references[name] = ApiReference(
            introduced_in=reference_data.get("introduced_in"),
            signature=_required_text(reference_data, "signature"),
            summary=_required_text(reference_data, "summary"),
            details=tuple(details),
        )
        introduction = api_references[name].introduced_in
        if introduction is not None and not isinstance(introduction, str):
            raise ValueError(f"API introduction must be a task ID: {name}")
        planned_prefixes = tuple(f"{lesson.id}_" for lesson in roadmap_lessons)
        if (
            introduction is not None and introduction not in task_ids
            and not introduction.startswith(planned_prefixes)
        ):
            raise ValueError(
                f"API reference {name} has unknown introduction task: "
                f"{introduction}"
            )
    return Course(
        title=_required_text(course_data, "title"),
        goal=_required_text(course_data, "goal"),
        promise=_required_text(course_data, "promise"),
        route=tuple(route),
        roadmap=tuple(roadmap),
        lessons=tuple(lessons),
        api_references=api_references,
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
