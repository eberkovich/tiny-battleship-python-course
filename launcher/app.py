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
from launcher.course import RoadmapLesson, RoadmapStage, Task
from launcher.theme import DARK_THEME_NAME, THEMES, ThemePalette


WINDOW_SIZE = (1180, 760)
WINDOW_FLAGS = pygame.RESIZABLE
SIDEBAR_WIDTH = 350
FENCE = chr(96) * 3
SUBMARINE_DIVIDER_ASSET = Path(__file__).with_name("assets") / "submarine_divider.png"
CONTENT_COLUMN_SIDE_MARGIN = 31
CONTENT_PADDING_X = 32
CONTENT_PADDING_Y = 26
NOTE_PADDING_X = CONTENT_PADDING_X
NOTE_PADDING_Y = 10
NOTE_LINE_HEIGHT = 21
NOTE_LINE_GAP = 2
RECAP_PADDING_X = 20
RECAP_PADDING_Y = 14
EXAMPLE_PADDING_X = 20
EXAMPLE_PADDING_Y = 18
OUTPUT_PADDING_X = 18
OUTPUT_PADDING_Y = 12
OUTPUT_LINE_HEIGHT = 22
OUTPUT_MAX_LINES = 6
DIVIDER_HEIGHT = 40
GLOBAL_TOOLBAR_BOTTOM = 64
HOME_SCROLL_VIEW_TOP = 136
HOME_PLAN_REVEAL_TOP = HOME_SCROLL_VIEW_TOP + 86
TASK_ICON_SIZE = 36
TASK_ICON_RENDER_SCALE = 4
SIDEBAR_TASK_HEIGHT = 50
SIDEBAR_TASK_GAP = 4
DIALOG_OVERLAY_ALPHA = 135
HOME_SIDE_MARGIN = 60
HOME_STAGE_GAP = 17


@dataclass(frozen=True)
class Button:
    label: str
    rect: pygame.Rect
    action: str


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


def _content_column_width(available_width: int) -> int:
    return max(1, available_width - CONTENT_COLUMN_SIDE_MARGIN * 2)


def _markdown_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False
    callout_kind: str | None = None
    paragraph: list[str] = []
    callout: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(("text", " ".join(paragraph)))
            paragraph.clear()

    def flush_callout() -> None:
        nonlocal callout_kind
        if callout and callout_kind is not None:
            blocks.append((callout_kind, "\n".join(callout)))
            callout.clear()
        callout_kind = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if callout_kind is not None:
            if stripped.startswith(">"):
                # Remove only the Markdown quote marker and its optional
                # separator. Preserve the remaining leading spaces: they are
                # meaningful Python indentation inside quoted code examples.
                callout_line = raw_line[1:]
                if callout_line.startswith(" "):
                    callout_line = callout_line[1:]
                callout_line = callout_line.rstrip()
                if callout_line or callout_kind == "example":
                    callout.append(callout_line)
                continue
            flush_callout()
        if stripped.startswith(FENCE):
            flush_paragraph()
            in_code = not in_code
            continue
        if in_code:
            # Empty quoted lines are Markdown spacing around a code block, not
            # executable code. Rendering them as rows creates a misleading
            # blank code card between adjacent statements.
            if stripped:
                blocks.append(("code", raw_line))
        elif stripped == "> [!NOTE]":
            flush_paragraph()
            if blocks and blocks[-1][0] == "space":
                blocks.pop()
            callout_kind = "note"
        elif stripped == "> [!RECAP]":
            flush_paragraph()
            if blocks and blocks[-1][0] == "space":
                blocks.pop()
            callout_kind = "recap"
        elif stripped == "> [!EXAMPLE]":
            flush_paragraph()
            if blocks and blocks[-1][0] == "space":
                blocks.pop()
            callout_kind = "example"
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
    flush_callout()
    while blocks and blocks[-1][0] == "space":
        blocks.pop()
    return blocks


class LauncherApp:
    def __init__(self, controller: LauncherController):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("Морской бой — курс Python")
        self.screen = pygame.display.set_mode(WINDOW_SIZE, WINDOW_FLAGS)
        self.clock = pygame.time.Clock()
        self.controller = controller
        self.scroll = 0
        self.sidebar_scroll = 0
        self.sidebar_focus_key: tuple[str, str, int] | None = None
        self.buttons: list[Button] = []
        self.task_rects: list[tuple[pygame.Rect, str]] = []
        self.task_status_rects: dict[str, pygame.Rect] = {}
        self.lesson_rects: list[tuple[pygame.Rect, str]] = []
        self.api_links: list[tuple[pygame.Rect, str]] = []
        self.api_dialog: str | None = None
        self.command_reference_open = False
        self.reference_api_links: list[tuple[pygame.Rect, str]] = []
        self.copy_signature_links: list[tuple[pygame.Rect, str]] = []
        self.copied_signature: str | None = None
        self.clipboard_error = False
        self.note_card_rect: pygame.Rect | None = None
        self.output_card_rect: pygame.Rect | None = None
        self.debug_badge_rect: pygame.Rect | None = None
        self.home_title_rect: pygame.Rect | None = None
        self.home_hero_rect: pygame.Rect | None = None
        self.lesson_title_rect: pygame.Rect | None = None
        self.home_plan_expanded = False
        self.home_content_height = self.screen.get_height()
        self.home_plan_top = 0
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.code_font = pygame.font.SysFont("Menlo", 18)
        self.note_font = pygame.font.SysFont("Arial", 15, italic=True)
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.hero_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.home_goal_font = pygame.font.SysFont("Arial", 26, bold=True)
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
                elif event.type == pygame.VIDEORESIZE:
                    self._resize_window(event.size)
                elif event.type == pygame.WINDOWRESIZED:
                    resized = (event.x, event.y)
                    if (
                        resized[0] < WINDOW_SIZE[0]
                        or resized[1] < WINDOW_SIZE[1]
                    ):
                        self._resize_window(resized)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._click(event.pos)
                elif (
                    event.type == pygame.MOUSEWHEEL
                    and self.api_dialog is None
                    and not self.command_reference_open
                ):
                    if (
                        self.controller.view != "home"
                        and pygame.mouse.get_pos()[0] < SIDEBAR_WIDTH
                    ):
                        self.sidebar_scroll = max(
                            0, self.sidebar_scroll - event.y * 32
                        )
                    else:
                        self.scroll = max(0, self.scroll - event.y * 32)
            self.controller.poll()
            self.render()
            if autoclose_ms and (time.monotonic() - started) * 1000 >= autoclose_ms:
                running = False
            self.clock.tick(60)
        self.controller.shutdown()
        pygame.quit()

    def _resize_window(self, size: tuple[int, int]) -> None:
        width = max(WINDOW_SIZE[0], size[0])
        height = max(WINDOW_SIZE[1], size[1])
        self.screen = pygame.display.set_mode((width, height), WINDOW_FLAGS)

    def _click(self, position: tuple[int, int]) -> None:
        if self.api_dialog is not None:
            for rect, signature in self.copy_signature_links:
                if rect.collidepoint(position):
                    self._copy_signature(signature)
                    return
            for button in self.buttons:
                if (
                    button.action == "close_api"
                    and button.rect.collidepoint(position)
                ):
                    self.api_dialog = None
                    self.copied_signature = None
                    self.clipboard_error = False
                    return
            return
        if self.command_reference_open:
            for rect, signature in self.copy_signature_links:
                if rect.collidepoint(position):
                    self._copy_signature(signature)
                    return
            for rect, api_name in self.reference_api_links:
                if rect.collidepoint(position):
                    self.api_dialog = api_name
                    self.copied_signature = None
                    self.clipboard_error = False
                    return
            for button in self.buttons:
                if (
                    button.action == "close_reference"
                    and button.rect.collidepoint(position)
                ):
                    self.command_reference_open = False
                    self.copied_signature = None
                    self.clipboard_error = False
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
                self.scroll = 0
            elif button.action == "continue":
                self.controller.continue_course()
                self.scroll = 0
            elif button.action == "toggle_plan":
                self.home_plan_expanded = not self.home_plan_expanded
                self.scroll = (
                    max(0, self.home_plan_top - HOME_PLAN_REVEAL_TOP)
                    if self.home_plan_expanded
                    else 0
                )
            elif button.action == "open":
                self.controller.open_code()
            elif button.action == "run":
                self.controller.start_run()
            elif button.action == "game":
                self.controller.start_game()
            elif button.action == "previous":
                self.controller.move(-1)
                self.scroll = 0
            elif button.action == "next":
                self.controller.move(1)
                self.scroll = 0
            elif button.action == "next_lesson":
                lesson_index = self.controller.course.lessons.index(
                    self.controller.lesson
                )
                next_lesson = self.controller.course.lessons[lesson_index + 1]
                self.controller.enter_lesson(next_lesson.id)
                self.scroll = 0
            elif button.action == "theme":
                self.controller.toggle_theme()
            elif button.action == "command_reference":
                self.command_reference_open = True
                self.copied_signature = None
                self.clipboard_error = False
            return

    def render(self) -> None:
        self.screen.fill(self.theme.background)
        self.buttons = []
        self.task_rects = []
        self.task_status_rects = {}
        self.lesson_rects = []
        self.api_links = []
        self.reference_api_links = []
        self.copy_signature_links = []
        self.note_card_rect = None
        self.debug_badge_rect = None
        self.home_title_rect = None
        self.home_hero_rect = None
        self.lesson_title_rect = None
        if self.controller.view == "home":
            self._render_home()
            self.scroll = min(
                self.scroll,
                max(
                    0,
                    self.home_content_height - self.screen.get_height(),
                    self.home_plan_top - HOME_PLAN_REVEAL_TOP
                    if self.home_plan_expanded
                    else 0,
                ),
            )
        else:
            self._render_sidebar()
            self._render_lesson_content()
        self._render_theme_switch()
        self._render_command_reference_button()
        self._render_game_button()
        self._render_debug_badge()
        self._render_game_message()
        if self.command_reference_open:
            self._render_command_reference()
        if self.api_dialog is not None:
            self.copy_signature_links = []
            self._render_api_dialog()
        pygame.display.flip()

    def _render_debug_badge(self) -> None:
        if not self.controller.debug:
            return
        rect = pygame.Rect(self.screen.get_width() - 680, 16, 180, 38)
        pygame.draw.rect(self.screen, self.theme.panel, rect, border_radius=9)
        pygame.draw.rect(self.screen, self.theme.gold, rect, 2, border_radius=9)
        label = self.small_font.render(
            "РЕЖИМ ОТЛАДКИ", True, self.theme.gold
        )
        self.screen.blit(label, label.get_rect(center=rect.center))
        self.debug_badge_rect = rect

    def _render_game_button(self) -> None:
        if not self.controller.game_available:
            return
        rect = pygame.Rect(self.screen.get_width() - 484, 16, 138, 38)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = (
            self.theme.button_disabled
            if self.controller.busy
            else self.theme.button_hover
            if hovered
            else self.theme.button
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=9)
        draw_ship_icon(
            self.screen,
            (rect.x + 20, rect.centery),
            self.theme.button_text,
            scale=0.5,
        )
        label = self.small_font.render("Моя игра", True, self.theme.button_text)
        self.screen.blit(
            label,
            label.get_rect(midleft=(rect.x + 38, rect.centery)),
        )
        self.buttons.append(Button("Моя игра", rect, "game"))

    def _render_game_message(self) -> None:
        if not self.controller.game_message:
            return
        color = {
            "success": self.theme.success,
            "error": self.theme.error,
        }.get(self.controller.game_message_level, self.theme.muted)
        message = _wrap(
            self.small_font,
            self.controller.game_message,
            465 if self.controller.debug else 650,
        )[0]
        surface = self.small_font.render(message, True, color)
        self.screen.blit(surface, (20, 26))

    def _render_command_reference_button(self) -> None:
        rect = pygame.Rect(self.screen.get_width() - 330, 16, 168, 38)
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = (
            self.theme.button_disabled
            if self.controller.busy
            else self.theme.button_hover
            if hovered
            else self.theme.button
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=9)

        icon_x = rect.x + 20
        icon_y = rect.centery
        pygame.draw.polygon(
            self.screen,
            self.theme.button_text,
            [
                (icon_x - 8, icon_y - 8),
                (icon_x - 1, icon_y - 5),
                (icon_x - 1, icon_y + 8),
                (icon_x - 8, icon_y + 5),
            ],
        )
        pygame.draw.polygon(
            self.screen,
            self.theme.button_text,
            [
                (icon_x + 8, icon_y - 8),
                (icon_x + 1, icon_y - 5),
                (icon_x + 1, icon_y + 8),
                (icon_x + 8, icon_y + 5),
            ],
        )
        surface = self.small_font.render(
            "Справочник", True, self.theme.button_text
        )
        self.screen.blit(
            surface,
            surface.get_rect(midleft=(rect.x + 38, rect.centery)),
        )
        self.buttons.append(Button("Справочник", rect, "command_reference"))

    def _render_theme_switch(self) -> None:
        rect = pygame.Rect(self.screen.get_width() - 146, 16, 128, 38)
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

    def _render_command_reference(self) -> None:
        viewport_size = self.screen.get_size()
        overlay = pygame.Surface(viewport_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, DIALOG_OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(0, 0, 860, 620)
        dialog.center = (viewport_size[0] // 2, viewport_size[1] // 2)
        pygame.draw.rect(
            self.screen, self.theme.content_card, dialog, border_radius=16
        )
        pygame.draw.rect(
            self.screen, self.theme.accent, dialog, 2, border_radius=16
        )

        self.screen.blit(
            self.title_font.render(
                "Справочник команд", True, self.theme.text
            ),
            (dialog.x + 28, dialog.y + 24),
        )
        self.screen.blit(
            self.small_font.render(
                "Здесь собраны все вспомогательные команды игры.",
                True,
                self.theme.muted,
            ),
            (dialog.x + 28, dialog.y + 66),
        )

        row_x = dialog.x + 28
        row_width = dialog.width - 56
        row_y = dialog.y + 102
        for api_name, reference in self.controller.course.api_references.items():
            row = pygame.Rect(row_x, row_y, row_width, 72)
            pygame.draw.rect(
                self.screen, self.theme.note_background, row, border_radius=9
            )
            self.screen.blit(
                self.code_font.render(
                    reference.signature, True, self.theme.text
                ),
                (row.x + 16, row.y + 9),
            )
            summary = _wrap(self.small_font, reference.summary, row.width - 280)[0]
            self.screen.blit(
                self.small_font.render(summary, True, self.theme.muted),
                (row.x + 16, row.y + 42),
            )

            details_rect = pygame.Rect(row.right - 232, row.y + 19, 104, 34)
            copy_rect = pygame.Rect(row.right - 116, row.y + 19, 104, 34)
            self._draw_reference_action(details_rect, "Подробнее")
            copy_label = "Копировать"
            if self.copied_signature == reference.signature:
                copy_label = (
                    "Не скопировано"
                    if self.clipboard_error
                    else "Скопировано"
                )
            self._draw_reference_action(copy_rect, copy_label)
            self.reference_api_links.append((details_rect, api_name))
            self.copy_signature_links.append((copy_rect, reference.signature))
            row_y += 80

        self._add_button(
            "Закрыть",
            dialog.right - 138,
            dialog.bottom - 50,
            110,
            "close_reference",
            height=36,
        )

    def _draw_reference_action(self, rect: pygame.Rect, label: str) -> None:
        color = (
            self.theme.button_hover
            if rect.collidepoint(pygame.mouse.get_pos())
            else self.theme.button
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=7)
        font = (
            self.task_font
            if self.task_font.size(label)[0] <= rect.width - 12
            else self.small_font
        )
        surface = font.render(label, True, self.theme.button_text)
        self.screen.blit(surface, surface.get_rect(center=rect.center))

    def _copy_signature(self, signature: str) -> None:
        self.copied_signature = signature
        self.clipboard_error = False
        try:
            self._set_clipboard_text(signature)
        except (pygame.error, RuntimeError):
            self.clipboard_error = True

    @staticmethod
    def _set_clipboard_text(text: str) -> None:
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))

    def _render_home(self) -> None:
        offset = -self.scroll
        course = self.controller.course
        home_left = HOME_SIDE_MARGIN
        home_width = self.screen.get_width() - HOME_SIDE_MARGIN * 2
        draw_ship_icon(
            self.screen,
            (home_left + 15, 101),
            self.theme.project,
            scale=1.25,
        )
        title = self.hero_font.render(course.title, True, self.theme.text)
        self.home_title_rect = title.get_rect(topleft=(home_left + 48, 77))
        self.screen.blit(title, self.home_title_rect)

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(
            pygame.Rect(
                0,
                HOME_SCROLL_VIEW_TOP,
                self.screen.get_width(),
                self.screen.get_height() - HOME_SCROLL_VIEW_TOP,
            )
        )

        hero = pygame.Rect(home_left, 144 + offset, home_width, 212)
        self.home_hero_rect = hero
        pygame.draw.rect(self.screen, self.theme.card, hero, border_radius=18)
        self.screen.blit(
            self.small_font.render("ТВОЯ ЦЕЛЬ", True, self.theme.accent),
            (hero.x + 28, hero.y + 22),
        )
        hero_text_width = hero.width - 385
        goal_lines = _wrap(self.home_goal_font, course.goal, hero_text_width)[:3]
        for index, line in enumerate(goal_lines):
            self.screen.blit(
                self.home_goal_font.render(line, True, self.theme.text),
                (hero.x + 28, hero.y + 49 + index * 31),
            )
        promise_y = hero.y + 55 + len(goal_lines) * 31
        promise_lines = _wrap(self.small_font, course.promise, hero_text_width)[:2]
        for index, line in enumerate(promise_lines):
            self.screen.blit(
                self.small_font.render(line, True, self.theme.muted),
                (hero.x + 28, promise_y + index * 21),
            )
        self._render_home_route(course.route, hero.x + 28, hero.bottom - 43)
        self._render_home_progress(
            pygame.Rect(hero.right - 305, hero.y + 22, 277, hero.height - 44)
        )

        section_y = 386 + offset
        self.screen.blit(
            self.title_font.render("Путь к готовой игре", True, self.theme.text),
            (home_left, section_y),
        )
        subtitle = self.small_font.render(
            "Три этапа — каждый заканчивается видимым результатом.",
            True,
            self.theme.muted,
        )
        self.screen.blit(subtitle, (home_left, section_y + 39))

        card_y = section_y + 76
        card_width = (home_width - HOME_STAGE_GAP * 2) // 3
        for index, stage in enumerate(course.roadmap, start=1):
            rect = pygame.Rect(
                home_left + (index - 1) * (card_width + HOME_STAGE_GAP),
                card_y,
                card_width,
                154,
            )
            self._render_home_stage(stage, index, rect)

        actions_y = card_y + 177
        first_task = course.lessons[0].tasks[0]
        has_progress = bool(
            self.controller.progress.completed_tasks
            or self.controller.progress.earned_stars
            or self.controller.progress.current_task != first_task.id
        )
        action = (
            f"Продолжить урок {self.controller.current_lesson_number}"
            if has_progress
            else "Начать первый урок"
        )
        self._add_button(
            action,
            home_left,
            actions_y,
            250,
            "continue",
            height=48,
        )
        toggle = (
            "Скрыть полный план"
            if self.home_plan_expanded
            else f"Показать все {self.controller.total_lesson_count} уроков"
        )
        self._add_button(
            toggle,
            home_left + 266,
            actions_y,
            245,
            "toggle_plan",
            height=48,
        )
        pace = self.small_font.render(
            f"{self.controller.total_lesson_count} коротких уроков · Иди в своём темпе",
            True,
            self.theme.muted,
        )
        self.screen.blit(pace, (home_left + 536, actions_y + 15))

        self.home_plan_top = actions_y - offset + 76

        if self.home_plan_expanded:
            self.home_content_height = (
                self._render_full_roadmap(self.home_plan_top + offset)
                - offset
                + 34
            )
        else:
            self.home_content_height = self.screen.get_height()
        self.screen.set_clip(previous_clip)

    def _render_home_route(
        self, route: tuple[str, ...], x: int, y: int
    ) -> None:
        cursor = x
        for index, item in enumerate(route):
            label = self.task_font.render(item, True, self.theme.text)
            width = label.get_width() + 18
            rect = pygame.Rect(cursor, y, width, 28)
            pygame.draw.rect(
                self.screen, self.theme.note_background, rect, border_radius=8
            )
            self.screen.blit(label, label.get_rect(center=rect.center))
            cursor = rect.right + 8
            if index < len(route) - 1:
                arrow = self.small_font.render("→", True, self.theme.muted)
                self.screen.blit(arrow, (cursor, y + 4))
                cursor += arrow.get_width() + 8

    def _render_home_progress(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(
            self.screen, self.theme.note_background, rect, border_radius=14
        )
        self.screen.blit(
            self.small_font.render("СЕЙЧАС", True, self.theme.accent),
            (rect.x + 20, rect.y + 18),
        )
        lesson = self.title_font.render(
            f"Урок {self.controller.current_lesson_number} из "
            f"{self.controller.total_lesson_count}",
            True,
            self.theme.text,
        )
        self.screen.blit(lesson, (rect.x + 20, rect.y + 43))
        stage = self.small_font.render(
            f"Этап {self.controller.current_stage_number} · "
            f"{self.controller.current_stage.title}",
            True,
            self.theme.muted,
        )
        self.screen.blit(stage, (rect.x + 20, rect.y + 81))
        track = pygame.Rect(rect.x + 20, rect.y + 113, rect.width - 40, 11)
        pygame.draw.rect(
            self.screen, self.theme.progress_idle, track, border_radius=6
        )
        completed = self.controller.completed_lesson_count
        fill_width = round(track.width * completed / self.controller.total_lesson_count)
        if fill_width:
            pygame.draw.rect(
                self.screen,
                self.theme.accent,
                (track.x, track.y, fill_width, track.height),
                border_radius=6,
            )
        progress = self.small_font.render(
            f"Пройдено: {completed}", True, self.theme.muted
        )
        self.screen.blit(progress, (track.x, track.bottom + 8))

    def _render_home_stage(
        self, stage: RoadmapStage, number: int, rect: pygame.Rect
    ) -> None:
        current = stage.id == self.controller.current_stage.id
        pygame.draw.rect(self.screen, self.theme.card, rect, border_radius=15)
        if current:
            pygame.draw.rect(
                self.screen, self.theme.accent, rect, 2, border_radius=15
            )
        badge = pygame.Rect(rect.x + 18, rect.y + 17, 34, 34)
        pygame.draw.rect(
            self.screen, self.theme.note_background, badge, border_radius=10
        )
        number_surface = self.font.render(str(number), True, self.theme.accent)
        self.screen.blit(number_surface, number_surface.get_rect(center=badge.center))
        marker = self._roadmap_stage_marker(stage)
        if marker == "current":
            label = self.small_font.render("ТЫ ЗДЕСЬ", True, self.theme.accent)
            self.screen.blit(label, (rect.right - label.get_width() - 18, rect.y + 21))
        elif marker == "planned":
            label = self.small_font.render("В ПЛАНЕ", True, self.theme.muted)
            self.screen.blit(
                label,
                (rect.right - label.get_width() - 18, rect.y + 21),
            )
        else:
            self._draw_lock((rect.right - 29, rect.y + 33), self.theme.muted)
        self.screen.blit(
            self.font.render(stage.title, True, self.theme.text),
            (rect.x + 18, rect.y + 61),
        )
        first = self.controller.course.roadmap_position(stage.lessons[0].id)
        last = self.controller.course.roadmap_position(stage.lessons[-1].id)
        self.screen.blit(
            self.task_font.render(
                f"Уроки {first}–{last}", True, self.theme.project
            ),
            (rect.x + 18, rect.y + 91),
        )
        lines = _wrap(self.small_font, stage.summary, rect.width - 36)[:2]
        for index, line in enumerate(lines):
            self.screen.blit(
                self.small_font.render(line, True, self.theme.muted),
                (rect.x + 18, rect.y + 116 + index * 19),
            )

    def _roadmap_stage_marker(self, stage: RoadmapStage) -> str:
        if stage.id == self.controller.current_stage.id:
            return "current"
        if self.controller.debug and all(
            self.controller.roadmap_lesson_status(lesson) == "future"
            for lesson in stage.lessons
        ):
            return "planned"
        return "locked"

    def _roadmap_entry_marker(self, status: str) -> str | None:
        if status == "completed":
            return "completed"
        if status == "future" and self.controller.debug:
            return "planned"
        if status in {"locked", "future"}:
            return "locked"
        return None

    def _render_full_roadmap(self, top: int) -> int:
        course = self.controller.course
        offset_top = top
        row_height = 36
        first_row_offset = 94
        bottom_padding = 14
        lesson_count = max((len(stage.lessons) for stage in course.roadmap), default=0)
        height = first_row_offset + lesson_count * row_height + bottom_padding
        panel_width = self.screen.get_width() - HOME_SIDE_MARGIN * 2
        panel = pygame.Rect(
            HOME_SIDE_MARGIN,
            offset_top,
            panel_width,
            height,
        )
        pygame.draw.rect(self.screen, self.theme.card, panel, border_radius=16)
        self.screen.blit(
            self.title_font.render("Все уроки", True, self.theme.text),
            (panel.x + 24, panel.y + 20),
        )
        column_gap = 16
        column_width = (panel.width - 48 - column_gap * 2) // 3
        for stage_index, stage in enumerate(course.roadmap):
            x = panel.x + 24 + stage_index * (column_width + column_gap)
            self.screen.blit(
                self.task_font.render(
                    f"Этап {stage_index + 1} · {stage.title}",
                    True,
                    self.theme.accent,
                ),
                (x, panel.y + 65),
            )
            y = panel.y + 94
            for planned in stage.lessons:
                number = course.roadmap_position(planned.id)
                status = self.controller.roadmap_lesson_status(planned)
                row = pygame.Rect(x, y, column_width, 32)
                unlocked = status not in {"locked", "future"}
                if unlocked:
                    pygame.draw.rect(
                        self.screen,
                        self.theme.note_background,
                        row,
                        border_radius=7,
                    )
                color = self.theme.text if unlocked else self.theme.muted
                number_surface = self.task_font.render(str(number), True, self.theme.project)
                self.screen.blit(number_surface, (row.x + 8, row.y + 7))
                title = _wrap(self.task_font, planned.title, row.width - 72)[0]
                self.screen.blit(
                    self.task_font.render(title, True, color),
                    (row.x + 36, row.y + 7),
                )
                marker = self._roadmap_entry_marker(status)
                if marker == "completed":
                    self._draw_check((row.right - 17, row.centery), self.theme.success)
                elif marker == "planned":
                    planned_label = self.task_font.render(
                        "план", True, self.theme.muted
                    )
                    self.screen.blit(
                        planned_label,
                        planned_label.get_rect(
                            midright=(row.right - 7, row.centery)
                        ),
                    )
                elif marker == "locked":
                    self._draw_lock((row.right - 17, row.centery), self.theme.muted)
                if unlocked:
                    self.lesson_rects.append((row, planned.id))
                y += row_height
        return panel.bottom

    def _render_sidebar(self) -> None:
        pygame.draw.rect(
            self.screen,
            self.theme.panel,
            (0, 0, SIDEBAR_WIDTH, self.screen.get_height()),
        )
        self._add_button("Все уроки", 18, 76, 125, "home", height=38)
        lesson_label = self.small_font.render(
            f"УРОК {self.controller.current_lesson_number} ИЗ "
            f"{self.controller.total_lesson_count} · "
            f"ЭТАП {self.controller.current_stage_number}",
            True,
            self.theme.accent,
        )
        self.screen.blit(lesson_label, (20, 126))
        title_lines = _wrap(
            self.task_font,
            self.controller.lesson.title,
            SIDEBAR_WIDTH - 40,
        )[:2]
        for index, line in enumerate(title_lines):
            self.screen.blit(
                self.task_font.render(line, True, self.theme.text),
                (20, 149 + index * 20),
            )

        task_area = pygame.Rect(
            0,
            195,
            SIDEBAR_WIDTH,
            self.screen.get_height() - 195,
        )
        task_step = SIDEBAR_TASK_HEIGHT + SIDEBAR_TASK_GAP
        task_count = len(self.controller.lesson.tasks)
        content_height = max(0, task_count * task_step - SIDEBAR_TASK_GAP)
        max_scroll = max(0, content_height - task_area.height)
        focus_key = (
            self.controller.lesson.id,
            self.controller.current_task.id,
            self.screen.get_height(),
        )
        if focus_key != self.sidebar_focus_key:
            active_index = self.controller.current_index
            active_top = active_index * task_step
            active_bottom = active_top + SIDEBAR_TASK_HEIGHT
            if active_top < self.sidebar_scroll:
                self.sidebar_scroll = active_top
            elif active_bottom > self.sidebar_scroll + task_area.height:
                self.sidebar_scroll = active_bottom - task_area.height
            self.sidebar_focus_key = focus_key
        self.sidebar_scroll = min(max_scroll, max(0, self.sidebar_scroll))

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(task_area)
        y = task_area.y - self.sidebar_scroll
        for task in self.controller.lesson.tasks:
            rect = pygame.Rect(14, y, SIDEBAR_WIDTH - 28, SIDEBAR_TASK_HEIGHT)
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
            status_rect = self._draw_task_status_mark(
                task, (rect.right - 24, rect.centery)
            )
            if status_rect is not None:
                self.task_status_rects[task.id] = status_rect
            task_lines = _wrap(self.task_font, task.title, rect.width - 94)[:2]
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
            visible_rect = rect.clip(task_area)
            if unlocked and visible_rect.width and visible_rect.height:
                self.task_rects.append((visible_rect, task.id))
            else:
                self._draw_lock(
                    (rect.right - 22, rect.centery), self.theme.muted
                )
            y += SIDEBAR_TASK_HEIGHT + SIDEBAR_TASK_GAP
        self.screen.set_clip(previous_clip)
        if max_scroll:
            track = pygame.Rect(
                SIDEBAR_WIDTH - 7,
                task_area.y + 4,
                3,
                task_area.height - 8,
            )
            pygame.draw.rect(
                self.screen,
                self.theme.progress_idle,
                track,
                border_radius=2,
            )
            thumb_height = max(
                28,
                round(track.height * task_area.height / content_height),
            )
            thumb_y = track.y + round(
                (track.height - thumb_height) * self.sidebar_scroll / max_scroll
            )
            pygame.draw.rect(
                self.screen,
                self.theme.accent,
                (track.x, thumb_y, track.width, thumb_height),
                border_radius=2,
            )

    def _render_lesson_content(self) -> None:
        left = SIDEBAR_WIDTH + 34
        width = self.screen.get_width() - left - 34
        button_y = self.screen.get_height() - 60
        task = self.controller.current_task
        self.output_card_rect = None
        self._draw_task_icon(task, (left + 17, 98), self._task_color(task))
        title = self.title_font.render(task.title, True, self.theme.text)
        self.lesson_title_rect = title.get_rect(topleft=(left + 42, 78))
        self.screen.blit(title, self.lesson_title_rect)

        body_top = 132
        section_blocks = _markdown_blocks(self.controller.sections[task.section])
        if task.kind == "summary":
            next_lesson = self.controller.next_roadmap_lesson()
            if next_lesson is not None:
                number = self.controller.course.roadmap_position(next_lesson.id)
                section_blocks.extend(
                    [
                        ("divider", ""),
                        ("text", f"Дальше — урок {number}. {next_lesson.title}"),
                    ]
                )
        note_values = [value for kind, value in section_blocks if kind == "note"]
        message_lines: list[str] = []
        message_color = self.theme.muted
        if task.is_coding and self.controller.message:
            message_color = {
                "success": self.theme.success,
                "error": self.theme.error,
                "info": self.theme.muted,
            }.get(self.controller.message_level, self.theme.muted)
            message_width = _content_column_width(width) - CONTENT_PADDING_X * 2
            message_lines = _wrap(
                self.small_font, self.controller.message, message_width
            )[:2]
        if task.is_coding and note_values:
            note_value = note_values[0]
            note_height = self._note_card_height(note_value, width)
            note_top = button_y - 14 - note_height
            fixed_top = note_top
            message_y: int | None = None
            if message_lines:
                message_y = fixed_top - 10 - len(message_lines) * 20
                fixed_top = message_y
            output_top: int | None = None
            if self.controller.latest_output:
                output_height = self._output_card_height(
                    self.controller.latest_output,
                    width,
                )
                output_top = fixed_top - 10 - output_height
                fixed_top = output_top
            content_bottom = fixed_top - 14
            content_rect = pygame.Rect(
                left, body_top, width, content_bottom - body_top
            )
            self._render_markdown_blocks(
                [block for block in section_blocks if block[0] != "note"],
                content_rect,
            )
            self._render_fixed_note(note_value, left, note_top, width)
            if output_top is not None:
                self._render_output_card(
                    self.controller.latest_output,
                    left,
                    output_top,
                    width,
                )
            if message_y is not None:
                card_x = left + (width - _content_column_width(width)) // 2
                for index, line in enumerate(message_lines):
                    self.screen.blit(
                        self.small_font.render(line, True, message_color),
                        (card_x + CONTENT_PADDING_X, message_y + index * 20),
                    )
        else:
            content_bottom = button_y - 14
            output_top = None
            if task.is_coding and self.controller.latest_output:
                output_height = self._output_card_height(
                    self.controller.latest_output,
                    width,
                )
                output_top = content_bottom - output_height
                content_bottom = output_top - 14
            content_rect = pygame.Rect(left, body_top, width, content_bottom - body_top)
            self._render_markdown_blocks(section_blocks, content_rect)
            if output_top is not None:
                self._render_output_card(
                    self.controller.latest_output,
                    left,
                    output_top,
                    width,
                )

        if self.controller.current_index > 0:
            self._add_button("Назад", left, button_y, 105, "previous")
        if task.is_coding:
            self._add_button(
                "Открыть редактор", left + 125, button_y, 185, "open"
            )
            self._add_button("Запустить", left + 325, button_y, 135, "run")
        can_advance = (
            self.controller.debug
            or not task.is_coding
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
        if task.kind == "summary" and (
            self.controller.debug or self.controller.lesson_complete()
        ):
            lesson_index = self.controller.course.lessons.index(
                self.controller.lesson
            )
            if lesson_index + 1 < len(self.controller.course.lessons):
                next_lesson = self.controller.course.lessons[lesson_index + 1]
                if self.controller.lesson_unlocked(next_lesson.id):
                    self._add_button(
                        "Следующий урок",
                        left + width - 180,
                        button_y,
                        180,
                        "next_lesson",
                    )

    def _render_markdown(self, text: str, rect: pygame.Rect) -> None:
        self._render_markdown_blocks(_markdown_blocks(text), rect)

    def _render_markdown_blocks(
        self,
        blocks: list[tuple[str, str]],
        rect: pygame.Rect,
    ) -> None:
        self.screen.set_clip(rect)
        card_width = _content_column_width(rect.width)
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
            elif block[0] in {"note", "recap", "example"}:
                flush_group()
                example_group = (
                    _markdown_blocks(block[1])
                    if block[0] == "example"
                    else [block]
                )
                items.append((block[0], example_group))
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
                else card_width - RECAP_PADDING_X * 2
                if item_kind == "recap"
                else card_width - EXAMPLE_PADDING_X * 2
                if item_kind == "example"
                else inner_width
            )
            item_padding_y = (
                NOTE_PADDING_Y if item_kind == "note" else CONTENT_PADDING_Y
            )
            if item_kind == "recap":
                item_padding_y = RECAP_PADDING_Y
            elif item_kind == "example":
                item_padding_y = EXAMPLE_PADDING_Y
            content_height = self._markdown_group_height(group, item_inner_width)
            card = pygame.Rect(
                card_x,
                y,
                card_width,
                content_height + item_padding_y * 2,
            )
            background = {
                "note": self.theme.note_background,
                "recap": self.theme.recap_background,
                "example": self.theme.example_background,
            }.get(item_kind, self.theme.content_card)
            pygame.draw.rect(self.screen, background, card, border_radius=14)
            if item_kind == "recap":
                pygame.draw.rect(
                    self.screen,
                    self.theme.recap_border,
                    card,
                    width=2,
                    border_radius=14,
                )
            elif item_kind == "example":
                pygame.draw.rect(
                    self.screen,
                    self.theme.example_border,
                    card,
                    width=1,
                    border_radius=12,
                )
            self._draw_markdown_group(
                group,
                card.x
                + (
                    NOTE_PADDING_X
                    if item_kind == "note"
                    else RECAP_PADDING_X
                    if item_kind == "recap"
                    else EXAMPLE_PADDING_X
                    if item_kind == "example"
                    else CONTENT_PADDING_X
                ),
                card.y + item_padding_y,
                item_inner_width,
            )
            y = card.bottom
            previous_was_card = True
        self.screen.set_clip(None)

    def _note_card_height(self, value: str, available_width: int) -> int:
        card_width = _content_column_width(available_width)
        inner_width = card_width - NOTE_PADDING_X * 2
        return (
            self._markdown_group_height([("note", value)], inner_width)
            + NOTE_PADDING_Y * 2
        )

    def _output_lines(self, value: str, available_width: int) -> list[str]:
        card_width = _content_column_width(available_width)
        inner_width = card_width - OUTPUT_PADDING_X * 2
        lines: list[str] = []
        for raw_line in value.splitlines() or [""]:
            lines.extend(_wrap(self.code_font, raw_line, inner_width))
        if len(lines) > OUTPUT_MAX_LINES:
            return lines[: OUTPUT_MAX_LINES - 1] + ["…"]
        return lines

    def _output_card_height(self, value: str, available_width: int) -> int:
        line_count = len(self._output_lines(value, available_width))
        return OUTPUT_PADDING_Y * 2 + 22 + 6 + line_count * OUTPUT_LINE_HEIGHT

    def _render_output_card(
        self,
        value: str,
        left: int,
        top: int,
        available_width: int,
    ) -> None:
        card_width = _content_column_width(available_width)
        card_x = left + (available_width - card_width) // 2
        card = pygame.Rect(
            card_x,
            top,
            card_width,
            self._output_card_height(value, available_width),
        )
        pygame.draw.rect(
            self.screen,
            self.theme.code_background,
            card,
            border_radius=10,
        )
        icon = pygame.Rect(card.x + OUTPUT_PADDING_X, card.y + OUTPUT_PADDING_Y, 22, 18)
        pygame.draw.rect(self.screen, self.theme.code_text, icon, 2, border_radius=3)
        prompt = self.small_font.render(">_", True, self.theme.code_text)
        self.screen.blit(prompt, prompt.get_rect(center=icon.center))
        title = self.small_font.render(
            "Результат программы",
            True,
            self.theme.code_text,
        )
        self.screen.blit(
            title,
            (icon.right + 9, card.y + OUTPUT_PADDING_Y - 1),
        )
        line_y = card.y + OUTPUT_PADDING_Y + 28
        for line in self._output_lines(value, available_width):
            rendered = self.code_font.render(line, True, self.theme.code_text)
            self.screen.blit(rendered, (card.x + OUTPUT_PADDING_X, line_y))
            line_y += OUTPUT_LINE_HEIGHT
        self.output_card_rect = card

    def _render_fixed_note(
        self,
        value: str,
        left: int,
        top: int,
        available_width: int,
    ) -> None:
        card_width = _content_column_width(available_width)
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

        viewport_size = self.screen.get_size()
        overlay = pygame.Surface(viewport_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, DIALOG_OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(0, 0, 700, 390)
        dialog.center = (viewport_size[0] // 2, viewport_size[1] // 2)
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
        copy_label = "Копировать"
        if self.copied_signature == reference.signature:
            copy_label = (
                "Не скопировано"
                if self.clipboard_error
                else "Скопировано"
            )
        copy_surface = self.small_font.render(
            copy_label, True, self.theme.accent
        )
        self.screen.blit(
            copy_surface,
            copy_surface.get_rect(midright=(code_rect.right - 14, code_rect.centery)),
        )
        self.copy_signature_links.append((code_rect, reference.signature))

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

    def _draw_task_status_mark(
        self,
        task: Task,
        center: tuple[int, int],
    ) -> pygame.Rect | None:
        rect = pygame.Rect(0, 0, 24, 24)
        rect.center = center
        if self._task_has_completion_badge(task):
            pygame.draw.circle(self.screen, self.theme.success, center, 12)
            x, y = center
            pygame.draw.lines(
                self.screen,
                self.theme.button_text,
                False,
                [(x - 8, y), (x - 3, y + 5), (x + 9, y - 7)],
                3,
            )
        elif self._task_has_failure_badge(task):
            pygame.draw.circle(self.screen, self.theme.error, center, 12)
            marker = self.font.render("!", True, self.theme.button_text)
            self.screen.blit(marker, marker.get_rect(center=center))
        else:
            return None
        return rect

    def _task_has_completion_badge(self, task: Task) -> bool:
        return task.is_coding and self.controller.task_passed(task)

    def _task_has_failure_badge(self, task: Task) -> bool:
        return (
            task.is_coding
            and not self.controller.task_passed(task)
            and task.id in self.controller.failed_tasks
        )

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


def run_launcher(student_dir: Path, *, debug: bool = False) -> None:
    controller = LauncherController(student_dir, debug=debug)
    LauncherApp(controller).run()
