from __future__ import annotations

import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

import pygame

from launcher.controller import LauncherController
from launcher.course import Task


WINDOW_SIZE = (1180, 760)
SIDEBAR_WIDTH = 350
BACKGROUND = (15, 23, 39)
PANEL = (25, 37, 59)
CARD = (34, 49, 75)
CARD_ACTIVE = (43, 74, 111)
CODE_BACKGROUND = (17, 29, 49)
TEXT = (239, 245, 255)
MUTED = (174, 191, 211)
ACCENT = (63, 190, 181)
BUTTON = (48, 105, 152)
BUTTON_HOVER = (61, 129, 184)
SUCCESS = (67, 180, 113)
ERROR = (224, 102, 102)
GOLD = (238, 190, 72)
ARTICLE = (91, 155, 213)
QUESTION = (165, 122, 214)
PROJECT = (234, 143, 74)
SUMMARY = (164, 139, 219)
FENCE = chr(96) * 3


@dataclass(frozen=True)
class Button:
    label: str
    rect: pygame.Rect
    action: str


@dataclass(frozen=True)
class ProgressSegment:
    task_id: str
    symbol: str
    number: int | None
    optional: bool
    state: str
    selected: bool


def _clean_markdown(text: str) -> str:
    return text.replace("**", "").replace(chr(96), "")


def _wrap(font: pygame.font.Font, text: str, width: int) -> list[str]:
    if not text:
        return [""]
    result: list[str] = []
    words = text.split()
    line = words[0]
    for word in words[1:]:
        candidate = f"{line} {word}"
        if font.size(candidate)[0] <= width:
            line = candidate
        else:
            result.append(line)
            line = word
    result.append(line)
    return result


class LauncherApp:
    def __init__(self, controller: LauncherController):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("Морской бой — курс Python")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.controller = controller
        self.scroll = 0
        self.buttons: list[Button] = []
        self.task_rects: list[tuple[pygame.Rect, str]] = []
        self.lesson_rects: list[tuple[pygame.Rect, str]] = []
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.code_font = pygame.font.SysFont("Menlo", 18)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.hero_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.task_font = pygame.font.SysFont("Arial", 15, bold=True)

    def run(self) -> None:
        running = True
        started = time.monotonic()
        autoclose_ms = int(os.environ.get("BATTLESHIP_AUTOCLOSE_MS", "0"))
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll = max(0, self.scroll - event.y * 32)
            self.controller.poll()
            self.render()
            if autoclose_ms and (time.monotonic() - started) * 1000 >= autoclose_ms:
                running = False
            self.clock.tick(60)
        self.controller.shutdown()
        pygame.quit()

    def _click(self, position: tuple[int, int]) -> None:
        if self.controller.busy:
            return
        for rect, lesson_id in self.lesson_rects:
            if rect.collidepoint(position):
                self.controller.enter_lesson(lesson_id)
                self.scroll = 0
                return
        for rect, task_id in self.task_rects:
            if rect.collidepoint(position):
                self.controller.select_task(task_id)
                self.scroll = 0
                return
        for button in self.buttons:
            if not button.rect.collidepoint(position):
                continue
            if button.action == "home":
                self.controller.show_home()
            elif button.action == "continue":
                self.controller.continue_course()
            elif button.action == "open":
                self.controller.open_code()
            elif button.action == "run":
                self.controller.start_run()
            elif button.action == "previous":
                self.controller.move(-1)
                self.scroll = 0
            elif button.action == "next":
                self.controller.move(1)
                self.scroll = 0
            return

    def render(self) -> None:
        self.screen.fill(BACKGROUND)
        self.buttons = []
        self.task_rects = []
        self.lesson_rects = []
        if self.controller.view == "home":
            self._render_home()
        else:
            self._render_sidebar()
            self._render_lesson_content()
        pygame.display.flip()

    def _render_home(self) -> None:
        title = self.hero_font.render(self.controller.course.title, True, TEXT)
        self.screen.blit(title, (60, 52))
        subtitle = self.font.render(
            "Курс, в котором каждый урок меняет твою игру", True, ACCENT
        )
        self.screen.blit(subtitle, (62, 108))

        intro_rect = pygame.Rect(60, 158, 1060, 150)
        pygame.draw.rect(self.screen, CARD, intro_rect, border_radius=14)
        y = intro_rect.y + 24
        for paragraph in self.controller.course.description:
            surface = self.font.render(paragraph, True, TEXT)
            self.screen.blit(surface, (intro_rect.x + 28, y))
            y += 34

        first_task = self.controller.course.lessons[0].tasks[0]
        has_progress = bool(
            self.controller.progress.completed_tasks
            or self.controller.progress.earned_stars
            or self.controller.progress.current_task != first_task.id
        )
        action = "Продолжить" if has_progress else "Начать первый урок"
        self._add_button(action, 60, 330, 230, "continue")

        heading = self.title_font.render("Уроки", True, TEXT)
        self.screen.blit(heading, (60, 410))
        y = 462
        for number, lesson in enumerate(self.controller.course.lessons, start=1):
            rect = pygame.Rect(60, y, 760, 92)
            status = self.controller.lesson_status(lesson)
            unlocked = status != "locked"
            pygame.draw.rect(
                self.screen, CARD if unlocked else PANEL, rect, border_radius=12
            )
            number_color = ACCENT if unlocked else MUTED
            number_surface = self.title_font.render(str(number), True, number_color)
            title_color = TEXT if unlocked else MUTED
            title_surface = self.font.render(lesson.title, True, title_color)
            status_text = {
                "completed": "Пройден",
                "in_progress": "Продолжить",
                "not_started": "Не начат",
                "locked": "Откроется после предыдущего урока",
            }[status]
            status_color = SUCCESS if status == "completed" else MUTED
            self.screen.blit(number_surface, (rect.x + 24, rect.y + 25))
            self.screen.blit(title_surface, (rect.x + 74, rect.y + 20))
            self.screen.blit(
                self.small_font.render(status_text, True, status_color),
                (rect.x + 74, rect.y + 54),
            )
            if unlocked:
                self.lesson_rects.append((rect, lesson.id))
            y += 108

    def _render_sidebar(self) -> None:
        pygame.draw.rect(
            self.screen, PANEL, (0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1])
        )
        self._add_button("Все уроки", 18, 16, 125, "home", height=38)
        lesson_number = self.controller.course.lessons.index(
            self.controller.lesson
        ) + 1
        lesson_label = self.small_font.render(
            f"УРОК {lesson_number}", True, ACCENT
        )
        self.screen.blit(lesson_label, (20, 68))
        title_lines = _wrap(
            self.task_font,
            self.controller.lesson.title,
            SIDEBAR_WIDTH - 40,
        )[:2]
        for index, line in enumerate(title_lines):
            self.screen.blit(
                self.task_font.render(line, True, TEXT),
                (20, 91 + index * 20),
            )

        self._render_progress(20, 137)
        y = 184
        for task in self.controller.lesson.tasks:
            rect = pygame.Rect(14, y, SIDEBAR_WIDTH - 28, 61)
            unlocked = self.controller.task_unlocked(task)
            active = task.id == self.controller.current_task.id
            pygame.draw.rect(
                self.screen,
                CARD_ACTIVE if active else CARD if unlocked else PANEL,
                rect,
                border_radius=9,
            )
            if active:
                pygame.draw.rect(self.screen, ACCENT, rect, 2, border_radius=9)
            color = self._task_color(task) if unlocked else MUTED
            self._draw_task_icon(task, (rect.x + 27, rect.centery), color)
            task_lines = _wrap(self.task_font, task.title, rect.width - 66)[:2]
            title_y = rect.centery - len(task_lines) * 9
            for index, line in enumerate(task_lines):
                self.screen.blit(
                    self.task_font.render(line, True, TEXT if unlocked else MUTED),
                    (rect.x + 52, title_y + index * 18),
                )
            if unlocked:
                self.task_rects.append((rect, task.id))
            else:
                self._draw_lock((rect.right - 22, rect.centery), MUTED)
            y += 67

    def _render_progress(self, x: int, y: int) -> None:
        cursor_x = x
        for segment in self._progress_segments():
            if segment.optional:
                cursor_x += 8
            width = 54 if segment.optional else 42
            rect = pygame.Rect(cursor_x, y, width, 26)
            color = {
                "passed": SUCCESS,
                "failed": ERROR,
                "not_started": (70, 84, 105),
            }[segment.state]
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            outline = self._progress_outline_color(segment)
            if outline is not None:
                pygame.draw.rect(self.screen, outline, rect, 2, border_radius=6)
            self._draw_progress_marker(segment, rect)
            cursor_x += width + 6

    @staticmethod
    def _progress_outline_color(
        segment: ProgressSegment,
    ) -> tuple[int, int, int] | None:
        return TEXT if segment.selected else None

    def _progress_segments(self) -> list[ProgressSegment]:
        required_ids = set(self.controller.lesson.completion_tasks)
        exercise_number = 0
        exercise_numbers: dict[str, int] = {}
        for task in self.controller.lesson.tasks:
            if task.kind in {"exercise", "star"}:
                exercise_number += 1
                exercise_numbers[task.id] = exercise_number

        segments = []
        for task in self.controller.lesson.tasks:
            if task.id not in required_ids and task.kind != "star":
                continue
            if self.controller.task_passed(task):
                state = "passed"
            elif task.id in self.controller.failed_tasks:
                state = "failed"
            else:
                state = "not_started"
            symbol = (
                "star"
                if task.kind == "star"
                else "ship"
                if task.kind == "project"
                else "number"
            )
            segments.append(
                ProgressSegment(
                    task_id=task.id,
                    symbol=symbol,
                    number=exercise_numbers.get(task.id),
                    optional=task.kind == "star",
                    state=state,
                    selected=task.id == self.controller.current_task.id,
                )
            )
        return segments

    def _draw_progress_marker(
        self, segment: ProgressSegment, rect: pygame.Rect
    ) -> None:
        if segment.symbol == "star":
            self._draw_star((rect.x + 15, rect.centery), GOLD, radius=8)
            if segment.state == "passed":
                self._draw_check((rect.x + 37, rect.centery), TEXT)
                return
            marker = {
                "failed": "!",
                "not_started": str(segment.number),
            }[segment.state]
            marker_surface = self.small_font.render(marker, True, TEXT)
            self.screen.blit(
                marker_surface,
                marker_surface.get_rect(center=(rect.x + 37, rect.centery)),
            )
            return
        if segment.state == "passed":
            self._draw_check(rect.center, TEXT)
            return
        if segment.state == "failed":
            marker = "!"
            marker_surface = self.small_font.render(marker, True, TEXT)
            self.screen.blit(marker_surface, marker_surface.get_rect(center=rect.center))
            return
        if segment.symbol == "ship":
            self._draw_ship((rect.centerx, rect.centery), TEXT, scale=0.7)
            return
        number = self.small_font.render(str(segment.number), True, TEXT)
        self.screen.blit(number, number.get_rect(center=rect.center))

    def _render_lesson_content(self) -> None:
        left = SIDEBAR_WIDTH + 34
        width = WINDOW_SIZE[0] - left - 34
        task = self.controller.current_task
        self._draw_task_icon(task, (left + 17, 48), self._task_color(task))
        title = self.title_font.render(task.title, True, TEXT)
        self.screen.blit(title, (left + 42, 28))

        body_top = 82
        body_bottom = 586 if task.is_coding else 665
        content_rect = pygame.Rect(
            left, body_top, width, body_bottom - body_top
        )
        pygame.draw.rect(self.screen, CARD, content_rect, border_radius=10)
        self._render_markdown(
            self.controller.sections[task.section],
            content_rect.inflate(-28, -22),
        )

        if task.is_coding:
            if self.controller.message:
                color = {
                    "success": SUCCESS,
                    "error": ERROR,
                    "info": MUTED,
                }.get(self.controller.message_level, MUTED)
                message_lines = _wrap(
                    self.small_font, self.controller.message, width - 20
                )[:2]
                for index, line in enumerate(message_lines):
                    self.screen.blit(
                        self.small_font.render(line, True, color),
                        (left + 4, 603 + index * 20),
                    )
            reminder = self.small_font.render(
                "Сохрани код в редакторе: Cmd+S", True, MUTED
            )
            self.screen.blit(reminder, (left + 4, 651))

        button_y = 700
        if self.controller.current_index > 0:
            self._add_button("Назад", left, button_y, 105, "previous")
        if task.is_coding:
            self._add_button(
                "Открыть редактор", left + 125, button_y, 185, "open"
            )
            self._add_button("Запустить", left + 325, button_y, 135, "run")
        can_advance = (
            not task.is_coding
            or task.kind == "star"
            or self.controller.task_passed(task)
        )
        if (
            can_advance
            and self.controller.current_index
            < len(self.controller.lesson.tasks) - 1
        ):
            next_task = self.controller.lesson.tasks[
                self.controller.current_index + 1
            ]
            if self.controller.task_unlocked(next_task):
                self._add_button(
                    "Дальше", left + width - 120, button_y, 120, "next"
                )

    def _render_markdown(self, text: str, rect: pygame.Rect) -> None:
        self.screen.set_clip(rect)
        y = rect.y - self.scroll
        blocks: list[tuple[str, str]] = []
        in_code = False
        paragraph: list[str] = []

        def flush_paragraph() -> None:
            if paragraph:
                blocks.append(("text", " ".join(paragraph)))
                paragraph.clear()

        for raw_line in text.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith(FENCE):
                flush_paragraph()
                in_code = not in_code
                continue
            if in_code:
                blocks.append(("code", raw_line))
            elif re.match(r"^#{1,6}\s+", stripped):
                flush_paragraph()
            elif not stripped:
                flush_paragraph()
                blocks.append(("space", ""))
            elif stripped.startswith("- "):
                flush_paragraph()
                indentation = len(raw_line) - len(raw_line.lstrip())
                kind = "subbullet" if indentation else "bullet"
                blocks.append((kind, stripped[2:]))
            else:
                paragraph.append(stripped)
        flush_paragraph()

        for kind, value in blocks:
            if kind == "space":
                y += 13
            elif kind == "code":
                code_rect = pygame.Rect(rect.x, y - 4, rect.width, 31)
                pygame.draw.rect(
                    self.screen, CODE_BACKGROUND, code_rect, border_radius=5
                )
                self.screen.blit(
                    self.code_font.render(value, True, (205, 231, 246)),
                    (rect.x + 12, y + 1),
                )
                y += 35
            else:
                line = _clean_markdown(value)
                line_x = rect.x
                line_width = rect.width
                if kind == "bullet":
                    line = "• " + line
                elif kind == "subbullet":
                    line = "– " + line
                    line_x += 22
                    line_width -= 22
                for wrapped in _wrap(self.font, line, line_width):
                    self.screen.blit(
                        self.font.render(wrapped, True, TEXT), (line_x, y)
                    )
                    y += 29
            if kind in {"text", "code"}:
                y += 3
        self.screen.set_clip(None)

    def _task_color(self, task: Task) -> tuple[int, int, int]:
        return {
            "article": ARTICLE,
            "question": QUESTION,
            "exercise": ACCENT,
            "project": PROJECT,
            "star": GOLD,
            "summary": SUMMARY,
        }.get(task.kind, MUTED)

    def _draw_task_icon(
        self,
        task: Task,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = center
        if task.kind == "article":
            pygame.draw.line(
                self.screen, color, (x, y - 10), (x, y + 10), 2
            )
            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (x - 13, y - 9),
                    (x - 2, y - 6),
                    (x - 2, y + 10),
                    (x - 13, y + 7),
                ],
                2,
            )
            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (x + 13, y - 9),
                    (x + 2, y - 6),
                    (x + 2, y + 10),
                    (x + 13, y + 7),
                ],
                2,
            )
        elif task.kind == "question":
            pygame.draw.circle(self.screen, color, center, 12, 2)
            mark = self.task_font.render("?", True, color)
            self.screen.blit(mark, mark.get_rect(center=center))
        elif task.kind == "exercise":
            pygame.draw.lines(
                self.screen,
                color,
                False,
                [(x - 3, y - 9), (x - 11, y), (x - 3, y + 9)],
                2,
            )
            pygame.draw.lines(
                self.screen,
                color,
                False,
                [(x + 3, y - 9), (x + 11, y), (x + 3, y + 9)],
                2,
            )
        elif task.kind == "project":
            self._draw_ship(center, color)
        elif task.kind == "star":
            self._draw_star(center, color)
        elif task.kind == "summary":
            pygame.draw.line(
                self.screen, color, (x - 9, y - 12), (x - 9, y + 12), 2
            )
            pygame.draw.polygon(
                self.screen,
                color,
                [(x - 8, y - 11), (x + 12, y - 7), (x - 8, y - 1)],
                2,
            )
        else:
            pygame.draw.circle(self.screen, color, center, 11, 2)

    def _draw_ship(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        scale: float = 1.0,
    ) -> None:
        x, y = center
        pygame.draw.polygon(
            self.screen,
            color,
            [
                (x - 14 * scale, y),
                (x + 14 * scale, y),
                (x + 8 * scale, y + 9 * scale),
                (x - 8 * scale, y + 9 * scale),
            ],
        )
        pygame.draw.line(
            self.screen, color, (x, y), (x, y - 10 * scale), max(1, int(2 * scale))
        )

    def _draw_star(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        radius: int = 13,
    ) -> None:
        x, y = center
        points = []
        for index in range(10):
            angle = -math.pi / 2 + index * math.pi / 5
            point_radius = radius if index % 2 == 0 else radius * 0.46
            points.append(
                (
                    x + math.cos(angle) * point_radius,
                    y + math.sin(angle) * point_radius,
                )
            )
        pygame.draw.polygon(self.screen, color, points, 2)

    def _draw_lock(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = center
        pygame.draw.arc(
            self.screen,
            color,
            pygame.Rect(x - 7, y - 10, 14, 13),
            0,
            math.pi,
            2,
        )
        pygame.draw.rect(
            self.screen,
            color,
            pygame.Rect(x - 9, y - 2, 18, 14),
            2,
            border_radius=3,
        )
        pygame.draw.circle(self.screen, color, (x, y + 4), 2)
        pygame.draw.line(self.screen, color, (x, y + 5), (x, y + 8), 2)

    def _draw_check(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = center
        pygame.draw.lines(
            self.screen,
            color,
            False,
            [(x - 6, y), (x - 2, y + 4), (x + 7, y - 5)],
            2,
        )

    def _add_button(
        self,
        label: str,
        x: int,
        y: int,
        width: int,
        action: str,
        *,
        height: int = 44,
    ) -> None:
        rect = pygame.Rect(x, y, width, height)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BUTTON_HOVER if hovered else BUTTON
        if self.controller.busy:
            color = (67, 77, 93)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        surface = self.small_font.render(label, True, TEXT)
        self.screen.blit(surface, surface.get_rect(center=rect.center))
        self.buttons.append(Button(label, rect, action))


def run_launcher(student_dir: Path) -> None:
    controller = LauncherController(student_dir)
    LauncherApp(controller).run()
