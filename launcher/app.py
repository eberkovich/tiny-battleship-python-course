from __future__ import annotations

import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

import pygame

from battleship_ui.icons import draw_ship_icon
from launcher.controller import LauncherController
from launcher.course import Task
from launcher.theme import DARK_THEME_NAME, THEMES, ThemePalette


WINDOW_SIZE = (1180, 760)
SIDEBAR_WIDTH = 350
FENCE = chr(96) * 3
SUBMARINE_DIVIDER_ASSET = Path(__file__).with_name("assets") / "submarine_divider.png"
CONTENT_COLUMN_WIDTH = 700
CONTENT_PADDING_X = 32
CONTENT_PADDING_Y = 26
NOTE_COLUMN_WIDTH = CONTENT_COLUMN_WIDTH
NOTE_PADDING_X = CONTENT_PADDING_X
NOTE_PADDING_Y = 10
NOTE_LINE_HEIGHT = 21
NOTE_LINE_GAP = 2
DIVIDER_HEIGHT = 40
TASK_ICON_SIZE = 36
TASK_ICON_RENDER_SCALE = 4
DIALOG_OVERLAY_ALPHA = 135


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


def _markdown_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False
    in_note = False
    paragraph: list[str] = []
    note: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(("text", " ".join(paragraph)))
            paragraph.clear()

    def flush_note() -> None:
        if note:
            blocks.append(("note", "\n".join(note)))
            note.clear()

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if in_note:
            if stripped.startswith(">"):
                note_line = stripped[1:].strip()
                if note_line:
                    note.append(note_line)
                continue
            flush_note()
            in_note = False
        if stripped.startswith(FENCE):
            flush_paragraph()
            in_code = not in_code
            continue
        if in_code:
            blocks.append(("code", raw_line))
        elif stripped == "> [!NOTE]":
            flush_paragraph()
            if blocks and blocks[-1][0] == "space":
                blocks.pop()
            in_note = True
        elif stripped == "---":
            flush_paragraph()
            if blocks and blocks[-1][0] == "space":
                blocks.pop()
            blocks.append(("divider", ""))
        elif re.match(r"^#{1,6}\s+", stripped):
            flush_paragraph()
        elif not stripped:
            flush_paragraph()
            if blocks and blocks[-1][0] not in {"space", "divider"}:
                blocks.append(("space", ""))
        elif stripped.startswith("- "):
            flush_paragraph()
            indentation = len(raw_line) - len(raw_line.lstrip())
            kind = "subbullet" if indentation else "bullet"
            blocks.append((kind, stripped[2:]))
        else:
            paragraph.append(stripped)
    flush_paragraph()
    flush_note()
    while blocks and blocks[-1][0] == "space":
        blocks.pop()
    return blocks


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
        self.api_links: list[tuple[pygame.Rect, str]] = []
        self.api_dialog: str | None = None
        self.note_card_rect: pygame.Rect | None = None
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.code_font = pygame.font.SysFont("Menlo", 18)
        self.note_font = pygame.font.SysFont("Arial", 15, italic=True)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.hero_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.task_font = pygame.font.SysFont("Arial", 15, bold=True)
        self.task_icon_font = pygame.font.SysFont(
            "Arial", 15 * TASK_ICON_RENDER_SCALE, bold=True
        )
        divider_source = pygame.image.load(SUBMARINE_DIVIDER_ASSET).convert_alpha()
        middle_width = round(
            divider_source.get_width() * DIVIDER_HEIGHT / divider_source.get_height()
        )
        escort_height = round(DIVIDER_HEIGHT * 0.72)
        escort_width = round(
            divider_source.get_width() * escort_height / divider_source.get_height()
        )
        middle = pygame.transform.smoothscale(
            divider_source, (middle_width, DIVIDER_HEIGHT)
        )
        escort = pygame.transform.smoothscale(
            divider_source, (escort_width, escort_height)
        )
        gap = 3
        divider_width = middle_width + escort_width * 2 + gap * 2
        self.submarine_divider = pygame.Surface(
            (divider_width, DIVIDER_HEIGHT), pygame.SRCALPHA
        )
        escort_y = (DIVIDER_HEIGHT - escort_height) // 2
        self.submarine_divider.blit(escort, (0, escort_y))
        self.submarine_divider.blit(middle, (escort_width + gap, 0))
        self.submarine_divider.blit(
            escort, (escort_width + gap + middle_width + gap, escort_y)
        )

    @property
    def theme(self) -> ThemePalette:
        return THEMES[self.controller.progress.theme]

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
                elif event.type == pygame.MOUSEWHEEL and self.api_dialog is None:
                    self.scroll = max(0, self.scroll - event.y * 32)
            self.controller.poll()
            self.render()
            if autoclose_ms and (time.monotonic() - started) * 1000 >= autoclose_ms:
                running = False
            self.clock.tick(60)
        self.controller.shutdown()
        pygame.quit()

    def _click(self, position: tuple[int, int]) -> None:
        if self.api_dialog is not None:
            for button in self.buttons:
                if (
                    button.action == "close_api"
                    and button.rect.collidepoint(position)
                ):
                    self.api_dialog = None
                    return
            return
        if self.controller.busy:
            return
        for rect, api_name in self.api_links:
            if rect.collidepoint(position):
                self.api_dialog = api_name
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
            elif button.action == "theme":
                self.controller.toggle_theme()
            return

    def render(self) -> None:
        self.screen.fill(self.theme.background)
        self.buttons = []
        self.task_rects = []
        self.lesson_rects = []
        self.api_links = []
        self.note_card_rect = None
        if self.controller.view == "home":
            self._render_home()
        else:
            self._render_sidebar()
            self._render_lesson_content()
        self._render_theme_switch()
        if self.api_dialog is not None:
            self._render_api_dialog()
        pygame.display.flip()

    def _render_theme_switch(self) -> None:
        rect = pygame.Rect(WINDOW_SIZE[0] - 146, 16, 128, 38)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = (
            self.theme.button_disabled
            if self.controller.busy
            else self.theme.button_hover
            if hovered
            else self.theme.button
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=9)
        icon_center = (rect.x + 20, rect.centery)
        if self.controller.progress.theme == DARK_THEME_NAME:
            pygame.draw.circle(
                self.screen, self.theme.button_text, icon_center, 8
            )
            pygame.draw.circle(
                self.screen, color, (icon_center[0] + 4, icon_center[1] - 3), 8
            )
            label = "Тёмная"
        else:
            pygame.draw.circle(
                self.screen, self.theme.button_text, icon_center, 6, 2
            )
            for offset_x, offset_y in (
                (-10, 0),
                (10, 0),
                (0, -10),
                (0, 10),
                (-7, -7),
                (7, -7),
                (-7, 7),
                (7, 7),
            ):
                pygame.draw.line(
                    self.screen,
                    self.theme.button_text,
                    (
                        round(icon_center[0] + offset_x * 0.7),
                        round(icon_center[1] + offset_y * 0.7),
                    ),
                    (icon_center[0] + offset_x, icon_center[1] + offset_y),
                    2,
                )
            label = "Светлая"
        surface = self.small_font.render(label, True, self.theme.button_text)
        self.screen.blit(
            surface,
            surface.get_rect(midleft=(rect.x + 38, rect.centery)),
        )
        self.buttons.append(Button(label, rect, "theme"))

    def _render_home(self) -> None:
        title = self.hero_font.render(
            self.controller.course.title, True, self.theme.text
        )
        self.screen.blit(title, (60, 52))
        subtitle = self.font.render(
            "Курс, в котором каждый урок меняет твою игру",
            True,
            self.theme.accent,
        )
        self.screen.blit(subtitle, (62, 108))

        intro_rect = pygame.Rect(60, 158, 1060, 150)
        pygame.draw.rect(self.screen, self.theme.card, intro_rect, border_radius=14)
        y = intro_rect.y + 24
        for paragraph in self.controller.course.description:
            surface = self.font.render(paragraph, True, self.theme.text)
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

        heading = self.title_font.render("Уроки", True, self.theme.text)
        self.screen.blit(heading, (60, 410))
        y = 462
        for number, lesson in enumerate(self.controller.course.lessons, start=1):
            rect = pygame.Rect(60, y, 760, 92)
            status = self.controller.lesson_status(lesson)
            unlocked = status != "locked"
            pygame.draw.rect(
                self.screen,
                self.theme.card if unlocked else self.theme.panel,
                rect,
                border_radius=12,
            )
            number_color = self.theme.accent if unlocked else self.theme.muted
            number_surface = self.title_font.render(str(number), True, number_color)
            title_color = self.theme.text if unlocked else self.theme.muted
            title_surface = self.font.render(lesson.title, True, title_color)
            status_text = {
                "completed": "Пройден",
                "in_progress": "Продолжить",
                "not_started": "Не начат",
                "locked": "Откроется после предыдущего урока",
            }[status]
            status_color = (
                self.theme.success if status == "completed" else self.theme.muted
            )
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
            self.screen,
            self.theme.panel,
            (0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1]),
        )
        self._add_button("Все уроки", 18, 16, 125, "home", height=38)
        lesson_number = self.controller.course.lessons.index(
            self.controller.lesson
        ) + 1
        lesson_label = self.small_font.render(
            f"УРОК {lesson_number}", True, self.theme.accent
        )
        self.screen.blit(lesson_label, (20, 68))
        title_lines = _wrap(
            self.task_font,
            self.controller.lesson.title,
            SIDEBAR_WIDTH - 40,
        )[:2]
        for index, line in enumerate(title_lines):
            self.screen.blit(
                self.task_font.render(line, True, self.theme.text),
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
                self.theme.card_active
                if active
                else self.theme.card
                if unlocked
                else self.theme.panel,
                rect,
                border_radius=9,
            )
            if active:
                pygame.draw.rect(
                    self.screen, self.theme.accent, rect, 2, border_radius=9
                )
            color = self._task_color(task) if unlocked else self.theme.muted
            self._draw_task_icon(task, (rect.x + 27, rect.centery), color)
            task_lines = _wrap(self.task_font, task.title, rect.width - 66)[:2]
            title_y = rect.centery - len(task_lines) * 9
            for index, line in enumerate(task_lines):
                self.screen.blit(
                    self.task_font.render(
                        line,
                        True,
                        self.theme.text if unlocked else self.theme.muted,
                    ),
                    (rect.x + 52, title_y + index * 18),
                )
            if unlocked:
                self.task_rects.append((rect, task.id))
            else:
                self._draw_lock(
                    (rect.right - 22, rect.centery), self.theme.muted
                )
            y += 67

    def _render_progress(self, x: int, y: int) -> None:
        cursor_x = x
        for segment in self._progress_segments():
            if segment.optional:
                cursor_x += 8
            width = 54 if segment.optional else 42
            rect = pygame.Rect(cursor_x, y, width, 26)
            color = {
                "passed": self.theme.success,
                "failed": self.theme.error,
                "not_started": self.theme.progress_idle,
            }[segment.state]
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            outline = self._progress_outline_color(segment)
            if outline is not None:
                pygame.draw.rect(self.screen, outline, rect, 2, border_radius=6)
            self._draw_progress_marker(segment, rect)
            cursor_x += width + 6

    def _progress_outline_color(
        self,
        segment: ProgressSegment,
    ) -> tuple[int, int, int] | None:
        return self.theme.text if segment.selected else None

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
            self._draw_star(
                (rect.x + 15, rect.centery), self.theme.gold, radius=8
            )
            if segment.state == "passed":
                self._draw_check(
                    (rect.x + 37, rect.centery), self.theme.button_text
                )
                return
            marker = {
                "failed": "!",
                "not_started": str(segment.number),
            }[segment.state]
            marker_surface = self.small_font.render(
                marker, True, self.theme.button_text
            )
            self.screen.blit(
                marker_surface,
                marker_surface.get_rect(center=(rect.x + 37, rect.centery)),
            )
            return
        if segment.state == "passed":
            self._draw_check(rect.center, self.theme.button_text)
            return
        if segment.state == "failed":
            marker = "!"
            marker_surface = self.small_font.render(
                marker, True, self.theme.button_text
            )
            self.screen.blit(marker_surface, marker_surface.get_rect(center=rect.center))
            return
        if segment.symbol == "ship":
            self._draw_ship(
                (rect.centerx, rect.centery), self.theme.button_text, scale=0.7
            )
            return
        number = self.small_font.render(
            str(segment.number), True, self.theme.button_text
        )
        self.screen.blit(number, number.get_rect(center=rect.center))

    def _render_lesson_content(self) -> None:
        left = SIDEBAR_WIDTH + 34
        width = WINDOW_SIZE[0] - left - 34
        button_y = 700
        task = self.controller.current_task
        self._draw_task_icon(task, (left + 17, 48), self._task_color(task))
        title = self.title_font.render(task.title, True, self.theme.text)
        self.screen.blit(title, (left + 42, 28))

        body_top = 82
        section_blocks = _markdown_blocks(self.controller.sections[task.section])
        note_values = [value for kind, value in section_blocks if kind == "note"]
        message_lines: list[str] = []
        message_color = self.theme.muted
        if task.is_coding and self.controller.message:
            message_color = {
                "success": self.theme.success,
                "error": self.theme.error,
                "info": self.theme.muted,
            }.get(self.controller.message_level, self.theme.muted)
            message_width = min(CONTENT_COLUMN_WIDTH, width) - CONTENT_PADDING_X * 2
            message_lines = _wrap(
                self.small_font, self.controller.message, message_width
            )[:2]
        if task.is_coding and note_values:
            note_value = note_values[0]
            note_height = self._note_card_height(note_value, width)
            note_top = button_y - 14 - note_height
            content_bottom = note_top - 14
            if message_lines:
                content_bottom -= len(message_lines) * 20 + 10
            content_rect = pygame.Rect(
                left, body_top, width, content_bottom - body_top
            )
            self._render_markdown_blocks(
                [block for block in section_blocks if block[0] != "note"],
                content_rect,
            )
            self._render_fixed_note(note_value, left, note_top, width)
            if message_lines:
                card_x = left + (width - min(CONTENT_COLUMN_WIDTH, width)) // 2
                message_y = note_top - 10 - len(message_lines) * 20
                for index, line in enumerate(message_lines):
                    self.screen.blit(
                        self.small_font.render(line, True, message_color),
                        (card_x + CONTENT_PADDING_X, message_y + index * 20),
                    )
        else:
            content_rect = pygame.Rect(
                left, body_top, width, 665 - body_top
            )
            self._render_markdown_blocks(section_blocks, content_rect)

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
        self._render_markdown_blocks(_markdown_blocks(text), rect)

    def _render_markdown_blocks(
        self,
        blocks: list[tuple[str, str]],
        rect: pygame.Rect,
    ) -> None:
        self.screen.set_clip(rect)
        card_width = min(CONTENT_COLUMN_WIDTH, rect.width)
        card_x = rect.centerx - card_width // 2
        inner_width = card_width - CONTENT_PADDING_X * 2
        items: list[tuple[str, list[tuple[str, str]]]] = []
        group: list[tuple[str, str]] = []

        def flush_group() -> None:
            if group:
                items.append(("content", group.copy()))
                group.clear()

        for block in blocks:
            if block[0] == "divider":
                flush_group()
                items.append(("divider", []))
            elif block[0] == "note":
                flush_group()
                items.append(("note", [block]))
            else:
                group.append(block)
        flush_group()

        y = rect.y - self.scroll
        previous_was_card = False
        for item_kind, group in items:
            if item_kind == "divider":
                y += 14
                divider_rect = self.submarine_divider.get_rect(
                    centerx=rect.centerx, top=y
                )
                self.screen.blit(self.submarine_divider, divider_rect)
                y = divider_rect.bottom + 14
                previous_was_card = False
                continue
            if previous_was_card:
                y += 14
            item_inner_width = (
                card_width - NOTE_PADDING_X * 2
                if item_kind == "note"
                else inner_width
            )
            item_padding_y = (
                NOTE_PADDING_Y if item_kind == "note" else CONTENT_PADDING_Y
            )
            content_height = self._markdown_group_height(group, item_inner_width)
            card = pygame.Rect(
                card_x,
                y,
                card_width,
                content_height + item_padding_y * 2,
            )
            pygame.draw.rect(
                self.screen,
                self.theme.note_background
                if item_kind == "note"
                else self.theme.content_card,
                card,
                border_radius=14,
            )
            self._draw_markdown_group(
                group,
                card.x
                + (NOTE_PADDING_X if item_kind == "note" else CONTENT_PADDING_X),
                card.y + item_padding_y,
                item_inner_width,
            )
            y = card.bottom
            previous_was_card = True
        self.screen.set_clip(None)

    def _note_card_height(self, value: str, available_width: int) -> int:
        card_width = min(NOTE_COLUMN_WIDTH, available_width)
        inner_width = card_width - NOTE_PADDING_X * 2
        return (
            self._markdown_group_height([("note", value)], inner_width)
            + NOTE_PADDING_Y * 2
        )

    def _render_fixed_note(
        self,
        value: str,
        left: int,
        top: int,
        available_width: int,
    ) -> None:
        card_width = min(NOTE_COLUMN_WIDTH, available_width)
        card_x = left + (available_width - card_width) // 2
        card_height = self._note_card_height(value, available_width)
        card = pygame.Rect(card_x, top, card_width, card_height)
        pygame.draw.rect(
            self.screen, self.theme.note_background, card, border_radius=9
        )
        self._draw_markdown_group(
            [("note", value)],
            card.x + NOTE_PADDING_X,
            card.y + NOTE_PADDING_Y,
            card.width - NOTE_PADDING_X * 2,
        )
        self.note_card_rect = card

    def _markdown_group_height(
        self, blocks: list[tuple[str, str]], width: int
    ) -> int:
        height = 0
        for kind, value in blocks:
            if kind == "space":
                height += 18
            elif kind == "code":
                height += 43
            elif kind == "note":
                source_lines = value.splitlines()
                for index, source_line in enumerate(source_lines):
                    height += len(
                        _wrap(self.note_font, _clean_markdown(source_line), width)
                    ) * NOTE_LINE_HEIGHT
                    if index < len(source_lines) - 1:
                        height += NOTE_LINE_GAP
            else:
                line = _clean_markdown(value)
                line_width = width - 22 if kind == "subbullet" else width
                if kind == "bullet":
                    line = "• " + line
                elif kind == "subbullet":
                    line = "• " + line
                height += len(_wrap(self.font, line, line_width)) * 30 + 5
        return height

    def _draw_markdown_group(
        self,
        blocks: list[tuple[str, str]],
        x: int,
        y: int,
        width: int,
    ) -> None:
        for kind, value in blocks:
            if kind == "space":
                y += 18
            elif kind == "code":
                code_rect = pygame.Rect(x, y, width, 35)
                pygame.draw.rect(
                    self.screen,
                    self.theme.code_background,
                    code_rect,
                    border_radius=5,
                )
                self._draw_text_with_api_links(
                    self.code_font,
                    value,
                    self.theme.code_text,
                    x + 12,
                    y + 4,
                )
                y += 43
            elif kind == "note":
                source_lines = value.splitlines()
                for index, source_line in enumerate(source_lines):
                    for wrapped in _wrap(
                        self.note_font, _clean_markdown(source_line), width
                    ):
                        self.screen.blit(
                            self.note_font.render(wrapped, True, self.theme.muted),
                            (x, y),
                        )
                        y += NOTE_LINE_HEIGHT
                    if index < len(source_lines) - 1:
                        y += NOTE_LINE_GAP
            else:
                line = _clean_markdown(value)
                line_x = x
                line_width = width
                if kind == "bullet":
                    line = "• " + line
                elif kind == "subbullet":
                    line = "• " + line
                    line_x += 22
                    line_width -= 22
                for wrapped in _wrap(self.font, line, line_width):
                    self._draw_text_with_api_links(
                        self.font,
                        wrapped,
                        self.theme.text,
                        line_x,
                        y,
                    )
                    y += 30
                y += 5

    def _draw_text_with_api_links(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        x: int,
        y: int,
    ) -> None:
        self.screen.blit(font.render(text, True, color), (x, y))
        for api_name in self.controller.course.api_references:
            if not self.controller.course.api_reference_available(
                api_name, self.controller.current_task.id
            ):
                continue
            pattern = rf"\b{re.escape(api_name)}\b"
            for match in re.finditer(pattern, text):
                link_x = x + font.size(text[: match.start()])[0]
                link_width = font.size(api_name)[0]
                self.screen.blit(
                    font.render(api_name, True, self.theme.accent),
                    (link_x, y),
                )
                underline_y = y + font.get_height() - 2
                pygame.draw.line(
                    self.screen,
                    self.theme.accent,
                    (link_x, underline_y),
                    (link_x + link_width, underline_y),
                    1,
                )
                link_rect = pygame.Rect(
                    link_x,
                    y,
                    link_width,
                    font.get_height(),
                ).clip(self.screen.get_clip())
                if link_rect.width and link_rect.height:
                    self.api_links.append((link_rect, api_name))

    def _render_api_dialog(self) -> None:
        reference = self.controller.course.api_references.get(self.api_dialog or "")
        if reference is None:
            self.api_dialog = None
            return

        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, DIALOG_OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(0, 0, 700, 390)
        dialog.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        pygame.draw.rect(
            self.screen, self.theme.content_card, dialog, border_radius=16
        )
        pygame.draw.rect(
            self.screen, self.theme.accent, dialog, 2, border_radius=16
        )

        title = self.title_font.render(
            f"Команда {self.api_dialog}", True, self.theme.text
        )
        self.screen.blit(title, (dialog.x + 32, dialog.y + 28))

        code_rect = pygame.Rect(dialog.x + 32, dialog.y + 82, dialog.width - 64, 42)
        pygame.draw.rect(
            self.screen, self.theme.code_background, code_rect, border_radius=7
        )
        signature = self.code_font.render(
            reference.signature, True, self.theme.code_text
        )
        self.screen.blit(signature, (code_rect.x + 14, code_rect.y + 7))

        y = dialog.y + 147
        for line in _wrap(self.font, reference.summary, dialog.width - 64):
            self.screen.blit(
                self.font.render(line, True, self.theme.text),
                (dialog.x + 32, y),
            )
            y += 29
        y += 10
        for detail in reference.details:
            for line in _wrap(self.small_font, "• " + detail, dialog.width - 76):
                self.screen.blit(
                    self.small_font.render(line, True, self.theme.text),
                    (dialog.x + 42, y),
                )
                y += 23
            y += 4

        self._add_button(
            "Закрыть",
            dialog.right - 142,
            dialog.bottom - 58,
            110,
            "close_api",
            height=38,
        )

    def _task_color(self, task: Task) -> tuple[int, int, int]:
        return {
            "article": self.theme.article,
            "question": self.theme.question,
            "exercise": self.theme.accent,
            "project": self.theme.project,
            "star": self.theme.gold,
            "summary": self.theme.summary,
        }.get(task.kind, self.theme.muted)

    def _draw_task_icon(
        self,
        task: Task,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        render_size = TASK_ICON_SIZE * TASK_ICON_RENDER_SCALE
        icon_surface = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
        icon_center = (render_size // 2, render_size // 2)
        self._draw_task_icon_shape(
            icon_surface,
            task,
            icon_center,
            color,
            TASK_ICON_RENDER_SCALE,
        )
        icon = pygame.transform.smoothscale(
            icon_surface, (TASK_ICON_SIZE, TASK_ICON_SIZE)
        )
        self.screen.blit(icon, icon.get_rect(center=center))

    def _draw_task_icon_shape(
        self,
        target: pygame.Surface,
        task: Task,
        center: tuple[int, int],
        color: tuple[int, int, int],
        scale: int,
    ) -> None:
        x, y = center

        def point(offset_x: int, offset_y: int) -> tuple[int, int]:
            return (x + offset_x * scale, y + offset_y * scale)

        def stroke(width: int) -> int:
            return width * scale

        if task.kind == "article":
            pygame.draw.polygon(
                target,
                color,
                [
                    point(-15, -10),
                    point(-2, -7),
                    point(-2, 11),
                    point(-15, 8),
                ],
            )
            pygame.draw.polygon(
                target,
                color,
                [
                    point(15, -10),
                    point(2, -7),
                    point(2, 11),
                    point(15, 8),
                ],
            )
            pygame.draw.line(
                target,
                self.theme.button_text,
                point(0, -7),
                point(0, 11),
                stroke(3),
            )
            pygame.draw.line(
                target,
                self.theme.button_text,
                point(-11, -5),
                point(-5, -3),
                stroke(2),
            )
            pygame.draw.line(
                target,
                self.theme.button_text,
                point(11, -5),
                point(5, -3),
                stroke(2),
            )
        elif task.kind == "question":
            pygame.draw.circle(target, color, point(0, -1), 13 * scale)
            pygame.draw.polygon(
                target,
                color,
                [point(-7, 8), point(-11, 14), point(-2, 11)],
            )
            mark = self.task_icon_font.render("?", True, self.theme.button_text)
            target.blit(mark, mark.get_rect(center=point(0, -1)))
        elif task.kind == "exercise":
            pygame.draw.polygon(
                target,
                color,
                [
                    point(-9, 5),
                    point(-5, 9),
                    point(11, -7),
                    point(7, -11),
                ],
            )
            pygame.draw.polygon(
                target,
                color,
                [point(-12, 12), point(-9, 5), point(-5, 9)],
            )
            pygame.draw.line(
                target,
                self.theme.button_text,
                point(6, -6),
                point(9, -3),
                stroke(2),
            )
        elif task.kind == "project":
            self._draw_ship_shape(target, center, color, scale=scale)
        elif task.kind == "star":
            self._draw_star_shape(target, center, color, radius=13 * scale)
        elif task.kind == "summary":
            pygame.draw.line(
                target,
                color,
                point(-10, -13),
                point(-10, 13),
                stroke(4),
            )
            pygame.draw.circle(target, color, point(-10, -13), 3 * scale)
            pygame.draw.polygon(
                target,
                color,
                [
                    point(-8, -11),
                    point(13, -7),
                    point(7, -1),
                    point(-8, -4),
                ],
            )
        else:
            pygame.draw.circle(target, color, center, 12 * scale)

    def _draw_ship(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        scale: float = 1.0,
    ) -> None:
        self._draw_ship_shape(self.screen, center, color, scale=scale)

    @staticmethod
    def _draw_ship_shape(
        target: pygame.Surface,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        scale: float = 1.0,
    ) -> None:
        draw_ship_icon(target, center, color, scale=scale)

    def _draw_star(
        self,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        radius: int = 13,
    ) -> None:
        self._draw_star_shape(self.screen, center, color, radius=radius)

    @staticmethod
    def _draw_star_shape(
        target: pygame.Surface,
        center: tuple[int, int],
        color: tuple[int, int, int],
        *,
        radius: int,
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
        pygame.draw.polygon(target, color, points)

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
        color = (
            self.theme.button_disabled
            if self.controller.busy
            else self.theme.button_hover
            if hovered
            else self.theme.button
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        surface = self.small_font.render(label, True, self.theme.button_text)
        self.screen.blit(surface, surface.get_rect(center=rect.center))
        self.buttons.append(Button(label, rect, action))


def run_launcher(student_dir: Path) -> None:
    controller = LauncherController(student_dir)
    LauncherApp(controller).run()
