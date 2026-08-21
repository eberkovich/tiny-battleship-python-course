from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from launcher.course import Course, Lesson
from launcher.theme import DEFAULT_THEME_NAME, THEMES


PROGRESS_VERSION = 4
TEMPLATE_STATE_VERSION = 1
LEGACY_TASK_MOVES = {
    "coordinates": "lesson_01_coordinates_coordinates",
    "deck_api": "lesson_01_coordinates_deck_api",
    "exercise_02": "lesson_01_coordinates_exercise_01",
    "star": "lesson_01_coordinates_star",
}


@dataclass
class Progress:
    current_lesson: str
    current_task: str
    completed_tasks: set[str]
    earned_stars: set[str]
    theme: str

    def to_dict(self) -> dict[str, object]:
        return {
            "version": PROGRESS_VERSION,
            "current_lesson": self.current_lesson,
            "current_task": self.current_task,
            "completed_tasks": sorted(self.completed_tasks),
            "earned_stars": sorted(self.earned_stars),
            "theme": self.theme,
        }


class StudentWorkspace:
    def __init__(self, root: Path, course: Course):
        self.root = root.resolve()
        self.course = course
        self.progress_path = self.root / "progress.json"
        self.template_state_path = self.root / ".course_templates.json"

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        template_state = self._load_template_state()
        for lesson in self.course.lessons:
            for task in lesson.tasks:
                if task.student_file is None or task.template is None:
                    continue
                destination = self.root / task.student_file
                destination.parent.mkdir(parents=True, exist_ok=True)
                key = task.student_file.as_posix()
                template_digest = self._file_digest(task.template)
                if not destination.exists():
                    shutil.copyfile(task.template, destination)
                    template_state[key] = template_digest
                    continue

                destination_digest = self._file_digest(destination)
                installed_digest = template_state.get(key)
                if destination_digest == template_digest:
                    template_state[key] = template_digest
                elif installed_digest == destination_digest:
                    shutil.copyfile(task.template, destination)
                    template_state[key] = template_digest
        self._save_template_state(template_state)
        if not self.progress_path.exists():
            first_lesson = self.course.lessons[0]
            self.save_progress(
                Progress(
                    current_lesson=first_lesson.id,
                    current_task=first_lesson.tasks[0].id,
                    completed_tasks=set(),
                    earned_stars=set(),
                    theme=DEFAULT_THEME_NAME,
                )
            )

    @staticmethod
    def _file_digest(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(64 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _load_template_state(self) -> dict[str, str]:
        if not self.template_state_path.exists():
            return {}
        try:
            data = json.loads(self.template_state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if data.get("version") != TEMPLATE_STATE_VERSION:
            return {}
        templates = data.get("templates")
        if not isinstance(templates, dict):
            return {}
        return {
            key: value
            for key, value in templates.items()
            if isinstance(key, str) and isinstance(value, str)
        }

    def _save_template_state(self, templates: dict[str, str]) -> None:
        self._write_json_atomically(
            self.template_state_path,
            {
                "version": TEMPLATE_STATE_VERSION,
                "templates": dict(sorted(templates.items())),
            },
            prefix=".course-templates-",
        )

    def source_path(self, task_id: str) -> Path:
        _, task = self.course.task(task_id)
        if task.student_file is None:
            raise ValueError(f"Task {task_id} has no source file")
        return self.root / task.student_file

    def load_progress(self) -> Progress:
        data = json.loads(self.progress_path.read_text(encoding="utf-8"))
        version = data.get("version")
        if version not in {1, 2, 3, PROGRESS_VERSION}:
            raise ValueError("Unsupported progress version")
        completed_tasks = {
            LEGACY_TASK_MOVES.get(task_id, task_id)
            for task_id in data.get("completed_tasks", [])
        }
        earned_stars = {
            LEGACY_TASK_MOVES.get(task_id, task_id)
            for task_id in data.get("earned_stars", [])
        }
        current_task = LEGACY_TASK_MOVES.get(
            str(data.get("current_task")), data.get("current_task")
        )
        valid_lessons = {lesson.id for lesson in self.course.lessons}
        current_lesson = data.get("current_lesson")
        if version == 1 or current_lesson not in valid_lessons:
            current_lesson = self.course.lessons[0].id
        moved_lesson = next(
            (
                lesson
                for lesson in self.course.lessons
                if lesson.id == "lesson_01_coordinates"
            ),
            None,
        )
        if moved_lesson is not None:
            if current_task in {task.id for task in moved_lesson.tasks}:
                current_lesson = moved_lesson.id
            elif (
                version < PROGRESS_VERSION
                and current_lesson != "lesson_01"
                and not set(moved_lesson.completion_tasks) <= completed_tasks
            ):
                current_lesson = moved_lesson.id
                current_task = moved_lesson.tasks[0].id
        lesson = self.course.lesson(str(current_lesson))
        lesson_task_ids = {task.id for task in lesson.tasks}
        valid_ids = {
            task.id for course_lesson in self.course.lessons for task in course_lesson.tasks
        }
        if current_task not in lesson_task_ids:
            current_task = lesson.tasks[0].id
        return Progress(
            current_lesson=lesson.id,
            current_task=str(current_task),
            completed_tasks=completed_tasks & valid_ids,
            earned_stars=earned_stars & valid_ids,
            theme=(
                str(data.get("theme"))
                if data.get("theme") in THEMES
                else DEFAULT_THEME_NAME
            ),
        )

    def save_progress(self, progress: Progress) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._write_json_atomically(
            self.progress_path,
            progress.to_dict(),
            prefix=".progress-",
        )

    def _write_json_atomically(
        self, path: Path, data: dict[str, object], *, prefix: str
    ) -> None:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=prefix, suffix=".json", dir=self.root
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temporary_name, path)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def mark_passed(self, task_id: str) -> Progress:
        lesson, task = self.course.task(task_id)
        progress = self.load_progress()
        if task.kind == "star":
            progress.earned_stars.add(task_id)
        else:
            progress.completed_tasks.add(task_id)
        progress.current_task = task_id
        progress.current_lesson = lesson.id
        self.save_progress(progress)
        return progress

    def set_current_task(self, lesson_id: str, task_id: str) -> Progress:
        lesson = self.course.lesson(lesson_id)
        lesson.task(task_id)
        progress = self.load_progress()
        progress.current_lesson = lesson_id
        progress.current_task = task_id
        self.save_progress(progress)
        return progress

    def lesson_complete(self, lesson: Lesson, progress: Progress) -> bool:
        return set(lesson.completion_tasks) <= progress.completed_tasks

    def set_theme(self, theme: str) -> Progress:
        if theme not in THEMES:
            raise ValueError(f"Unknown theme: {theme}")
        progress = self.load_progress()
        progress.theme = theme
        self.save_progress(progress)
        return progress
