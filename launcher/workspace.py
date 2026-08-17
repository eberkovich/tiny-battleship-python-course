from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from launcher.course import Course, Lesson


PROGRESS_VERSION = 2


@dataclass
class Progress:
    current_lesson: str
    current_task: str
    completed_tasks: set[str]
    earned_stars: set[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "version": PROGRESS_VERSION,
            "current_lesson": self.current_lesson,
            "current_task": self.current_task,
            "completed_tasks": sorted(self.completed_tasks),
            "earned_stars": sorted(self.earned_stars),
        }


class StudentWorkspace:
    def __init__(self, root: Path, course: Course):
        self.root = root.resolve()
        self.course = course
        self.progress_path = self.root / "progress.json"

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for lesson in self.course.lessons:
            for task in lesson.tasks:
                if task.student_file is None or task.template is None:
                    continue
                destination = self.root / task.student_file
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copyfile(task.template, destination)
        if not self.progress_path.exists():
            first_lesson = self.course.lessons[0]
            self.save_progress(
                Progress(
                    current_lesson=first_lesson.id,
                    current_task=first_lesson.tasks[0].id,
                    completed_tasks=set(),
                    earned_stars=set(),
                )
            )

    def source_path(self, task_id: str) -> Path:
        _, task = self.course.task(task_id)
        if task.student_file is None:
            raise ValueError(f"Task {task_id} has no source file")
        return self.root / task.student_file

    def load_progress(self) -> Progress:
        data = json.loads(self.progress_path.read_text(encoding="utf-8"))
        version = data.get("version")
        if version not in {1, PROGRESS_VERSION}:
            raise ValueError("Unsupported progress version")
        valid_lessons = {lesson.id for lesson in self.course.lessons}
        current_lesson = data.get("current_lesson")
        if version == 1 or current_lesson not in valid_lessons:
            current_lesson = self.course.lessons[0].id
        lesson = self.course.lesson(str(current_lesson))
        current_task = data.get("current_task")
        lesson_task_ids = {task.id for task in lesson.tasks}
        valid_ids = {
            task.id for course_lesson in self.course.lessons for task in course_lesson.tasks
        }
        if current_task not in lesson_task_ids:
            current_task = lesson.tasks[0].id
        return Progress(
            current_lesson=lesson.id,
            current_task=str(current_task),
            completed_tasks=set(data.get("completed_tasks", [])) & valid_ids,
            earned_stars=set(data.get("earned_stars", [])) & valid_ids,
        )

    def save_progress(self, progress: Progress) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=".progress-", suffix=".json", dir=self.root
        )
        try:
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
                json.dump(progress.to_dict(), stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            os.replace(temporary_name, self.progress_path)
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
