from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from launcher.course import Course, Lesson, Task, load_course, load_sections
from launcher.editor import open_in_thonny
from launcher.workspace import Progress, StudentWorkspace
from runner.process import RunningStudentProcess, start_student_process
from runner.results import RunResult


ProcessStarter = Callable[..., RunningStudentProcess]
EditorOpener = Callable[[Path], object]


class LauncherController:
    def __init__(
        self,
        student_dir: Path,
        *,
        course: Course | None = None,
        process_starter: ProcessStarter = start_student_process,
        editor_opener: EditorOpener = open_in_thonny,
    ) -> None:
        self.course = course or load_course()
        self.workspace = StudentWorkspace(student_dir, self.course)
        self.workspace.initialize()
        self.progress = self.workspace.load_progress()
        self.lesson = self.course.lesson(self.progress.current_lesson)
        self.sections = load_sections(self.lesson.content)
        self.process_starter = process_starter
        self.editor_opener = editor_opener
        self.view = "home"
        self.job: RunningStudentProcess | None = None
        self.job_kind: str | None = None
        self.pending_check: RunResult | None = None
        self.failed_tasks: set[str] = set()
        self.message = ""
        self.message_level = "info"
        self.technical_details = ""

    @property
    def current_task(self) -> Task:
        return self.lesson.task(self.progress.current_task)

    @property
    def current_index(self) -> int:
        return self.lesson.tasks.index(self.current_task)

    @property
    def busy(self) -> bool:
        return self.job is not None

    def show_home(self) -> None:
        if not self.busy:
            self.view = "home"
            self.message = ""
            self.message_level = "info"
            self.technical_details = ""

    def enter_lesson(self, lesson_id: str) -> None:
        if self.busy or not self.lesson_unlocked(lesson_id):
            return
        lesson = self.course.lesson(lesson_id)
        task_id = (
            self.progress.current_task
            if self.progress.current_lesson == lesson_id
            and any(task.id == self.progress.current_task for task in lesson.tasks)
            else lesson.tasks[0].id
        )
        self.lesson = lesson
        self.sections = load_sections(lesson.content)
        self.progress = self.workspace.set_current_task(lesson_id, task_id)
        self.view = "lesson"
        self.message = ""
        self.message_level = "info"
        self.technical_details = ""

    def continue_course(self) -> None:
        self.enter_lesson(self.progress.current_lesson)

    def lesson_unlocked(self, lesson_id: str) -> bool:
        index = next(
            index
            for index, lesson in enumerate(self.course.lessons)
            if lesson.id == lesson_id
        )
        return index == 0 or self.workspace.lesson_complete(
            self.course.lessons[index - 1], self.progress
        )

    def lesson_status(self, lesson: Lesson) -> str:
        if self.workspace.lesson_complete(lesson, self.progress):
            return "completed"
        coding_ids = {task.id for task in lesson.tasks if task.is_coding}
        if coding_ids & (self.progress.completed_tasks | self.progress.earned_stars):
            return "in_progress"
        return "not_started" if self.lesson_unlocked(lesson.id) else "locked"

    def select_task(self, task_id: str) -> None:
        if self.busy:
            return
        self.progress = self.workspace.set_current_task(self.lesson.id, task_id)
        self.message = ""
        self.message_level = "info"
        self.technical_details = ""

    def move(self, offset: int) -> None:
        index = max(0, min(len(self.lesson.tasks) - 1, self.current_index + offset))
        self.select_task(self.lesson.tasks[index].id)

    def source_path(self) -> Path | None:
        if not self.current_task.is_coding:
            return None
        return self.workspace.source_path(self.current_task.id)

    def open_code(self) -> None:
        source = self.source_path()
        if source is None:
            self.message = "В этом шаге нет кода."
            self.message_level = "error"
            return
        try:
            self.editor_opener(source)
            self.message = "Редактор открыт. Сохрани изменения: Cmd+S"
            self.message_level = "info"
            self.technical_details = ""
        except OSError as error:
            self.message = "Не удалось открыть редактор. Запусти установку ещё раз."
            self.message_level = "error"
            self.technical_details = str(error)

    def start_run(self) -> None:
        if self.busy:
            self.message = "Предыдущий запуск ещё работает."
            self.message_level = "info"
            return
        source = self.source_path()
        if source is None:
            self.message = "В этом шаге нет кода."
            self.message_level = "error"
            return
        self.job = self.process_starter(
            source,
            mode="check",
            task_id=self.current_task.id,
            timeout=5.0,
        )
        self.job_kind = "check"
        self.pending_check = None
        self.message = "Проверяю сохранённый код…"
        self.message_level = "info"
        self.technical_details = ""

    def _start_visual_run(self) -> None:
        source = self.source_path()
        if source is None:
            return
        self.job = self.process_starter(source, mode="play", timeout=None)
        self.job_kind = "play"
        self.message = "Открываю результат…"
        self.message_level = "info"

    def poll(self) -> RunResult | None:
        if self.job is None:
            return None
        result = self.job.poll_result()
        if result is None:
            return None

        kind = self.job_kind
        self.job = None
        self.job_kind = None
        self._report_technical_details(result)

        if kind == "check":
            if result.passed:
                self.progress = self.workspace.mark_passed(self.current_task.id)
                self.failed_tasks.discard(self.current_task.id)
            else:
                self.failed_tasks.add(self.current_task.id)
            self.pending_check = result
            if result.status in {"passed", "failed"}:
                self._start_visual_run()
            else:
                self.message = result.message
                self.message_level = "error"
                self.technical_details = result.technical_details
                self.pending_check = None
            return result

        check_result = self.pending_check
        self.pending_check = None
        if result.status == "error":
            self.message = result.message
            self.message_level = "error"
            self.technical_details = result.technical_details
        elif check_result is not None:
            self.message = check_result.message
            self.message_level = "success" if check_result.passed else "error"
            self.technical_details = check_result.technical_details
        return result

    def _report_technical_details(self, result: RunResult) -> None:
        if result.technical_details:
            print(
                f"[student-code:{result.code}] {result.technical_details}",
                file=sys.stderr,
            )

    def task_passed(self, task: Task) -> bool:
        if task.kind == "star":
            return task.id in self.progress.earned_stars
        return task.id in self.progress.completed_tasks

    def lesson_complete(self, lesson: Lesson | None = None) -> bool:
        return self.workspace.lesson_complete(lesson or self.lesson, self.progress)

    def shutdown(self) -> None:
        if self.job is not None:
            process = getattr(self.job, "process", None)
            if process is not None and process.poll() is None:
                process.terminate()
        self.job = None
        self.job_kind = None
        self.pending_check = None
