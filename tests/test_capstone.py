"""Metadata-driven capstone navigation and presentation contracts."""

import os
from pathlib import Path
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest
import yaml

from launcher.app import CONTENT_COLUMN_SIDE_MARGIN, GLOBAL_TOOLBAR_BOTTOM, LauncherApp
from launcher.controller import LauncherController
from launcher.course import load_course
from runner.process import run_check, start_student_process


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def small_curriculum(tmp_path):
    raw = yaml.safe_load((ROOT / "CURRICULUM.yaml").read_text())
    raw["lessons"] = raw["lessons"][:3]
    entries = raw["course"]["roadmap"][0]["lessons"][:3]
    entries[1].update(display_label="9¾", locked_title="Secret lesson")
    raw["course"]["roadmap"][0]["lessons"] = entries
    for stage in raw["course"]["roadmap"][1:]:
        stage["lessons"] = stage["lessons"][:1]
    lesson = raw["lessons"][1]
    coding = next(task for task in lesson["tasks"] if "student_file" in task)
    lesson["tasks"] = [
        {"id": "a02_intro", "kind": "article", "title": "Illustrated introduction", "section": "intro", "illustrations": {
            "picture": {"image_height": 90, "items": [{"image": "launcher/assets/submarine_divider.png", "caption": "One picture"}]},
        }},
        {**coding, "section": "coding"},
        {"id": "a02_summary", "kind": "summary", "title": "Summary", "section": "summary"},
    ]
    lesson["completion_tasks"] = [coding["id"]]
    lesson["content"] = "tests/fixtures/illustrated.md"
    lesson["presentation"] = {"background": "launcher/assets/submarine_divider.png", "plaque": "launcher/assets/submarine_divider.png"}
    path = tmp_path / "curriculum.yaml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True))
    return raw, path


def complete(controller, lesson):
    for task in lesson.tasks:
        if task.id in lesson.completion_tasks:
            controller.progress.completed_tasks.add(task.id)
            if task.kind == "question":
                controller.progress.puzzle_answers[task.id] = task.correct_choice
    controller.workspace.save_progress(controller.progress)


def test_secret_capstone_uses_normal_required_progression(small_curriculum, tmp_path):
    _, path = small_curriculum
    course = load_course(path)
    controller = LauncherController(tmp_path / "child", course=course)
    secret = course.roadmap_lesson("a02")
    assert [course.lesson_label(entry.id) for entry in course.roadmap_lessons[:3]] == ["1", "9¾", "2"]
    assert controller.total_lesson_count == len(course.roadmap_lessons)
    assert controller.roadmap_lesson_title(secret) == "Secret lesson"
    assert controller.roadmap_lesson_label(secret) == ""
    assert controller.roadmap_lesson_outcome(secret) == ""
    assert not controller.lesson_unlocked("a02")
    complete(controller, course.lesson("a01"))
    assert controller.lesson_unlocked("a02")
    assert controller.roadmap_lesson_title(secret) == secret.title
    assert controller.roadmap_lesson_label(secret) == "9¾"
    assert controller.roadmap_lesson_outcome(secret) == secret.outcome
    assert not controller.lesson_unlocked("a03")
    controller.enter_lesson("a02")
    assert not controller.task_unlocked(course.lesson("a02").tasks[-1])
    complete(controller, course.lesson("a02"))
    assert controller.task_unlocked(course.lesson("a02").tasks[-1])
    assert controller.lesson_unlocked("a03")
    assert controller.completed_lesson_count == 2


def test_debug_reveals_implemented_secret_without_saving_progress(small_curriculum, tmp_path):
    _, path = small_curriculum
    course = load_course(path)
    controller = LauncherController(tmp_path / "child", course=course, debug=True)
    before = controller.workspace.progress_path.read_bytes()
    assert controller.roadmap_lesson_title(course.roadmap_lesson("a02")) != "Secret lesson"
    assert controller.roadmap_lesson_label(course.roadmap_lesson("a02")) == "9¾"
    controller.enter_lesson("a02")
    assert controller.current_lesson_label == "9¾"
    assert controller.workspace.progress_path.read_bytes() == before
    assert not controller.lesson_unlocked(course.roadmap_lessons[-1].id)


def test_secret_number_is_not_rendered_in_roadmap_or_stage_range(tmp_path):
    controller = LauncherController(tmp_path / "child")
    app = LauncherApp(controller)
    rendered = []

    class RecordingFont:
        def __init__(self, font):
            self.font = font

        def render(self, text, *args, **kwargs):
            rendered.append(text)
            return self.font.render(text, *args, **kwargs)

        def __getattr__(self, name):
            return getattr(self.font, name)

    app.task_font = RecordingFont(app.task_font)
    app.home_plan_expanded = True
    try:
        controller.show_home()
        app.render()
        assert "Секретный урок" in rendered
        assert all("9¾" not in label for label in rendered)
        assert "Уроки 1–9" in rendered
        for lesson in controller.course.lessons:
            if lesson.id == "a09_bonus":
                break
            complete(controller, lesson)
        rendered.clear()
        app.render()
        assert "9¾" in rendered
        assert "Уроки 1–9¾" in rendered
        assert "Секретный урок" not in rendered
    finally:
        controller.shutdown()
        pygame.quit()


@pytest.mark.parametrize("invalid", ["../../missing.png", "missing.png", "", 42])
def test_metadata_rejects_missing_or_unsafe_assets(small_curriculum, invalid):
    raw, path = small_curriculum
    raw["lessons"][1]["presentation"]["background"] = invalid
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError):
        load_course(path)


def test_metadata_rejects_invalid_illustration_layout(small_curriculum):
    raw, path = small_curriculum
    group = raw["lessons"][1]["tasks"][0]["illustrations"]["picture"]
    group["items"] = group["items"] * 4
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError):
        load_course(path)


def test_metadata_rejects_undeclared_illustration_group(small_curriculum):
    raw, path = small_curriculum
    raw["lessons"][1]["tasks"][0]["illustrations"]["different"] = raw["lessons"][1]["tasks"][0]["illustrations"].pop("picture")
    path.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValueError, match="Unknown illustration"):
        load_course(path)


def test_artwork_stays_below_controls_and_clears_on_leaving(small_curriculum, tmp_path):
    _, path = small_curriculum
    controller = LauncherController(tmp_path / "review", course=load_course(path), debug=True)
    controller.enter_lesson("a02")
    app = LauncherApp(controller)
    try:
        app.render()
        assert app.illustration_rects
        assert app.background_rect.top > GLOBAL_TOOLBAR_BOTTOM
        assert app.plaque_rect.left > app.lesson_title_rect.right
        assert all(app.background_rect.contains(rect) for rect in app.illustration_rects)
        controller.show_home()
        app.render()
        assert not app.illustration_rects
        assert app.background_rect is None
        controller.enter_lesson("a01")
        app.render()
        assert app.background_rect is None
        assert app.plaque_rect is None
    finally:
        controller.shutdown()
        pygame.quit()


def test_illustrated_article_leaves_artwork_exposed_between_text_cards(
    small_curriculum, tmp_path, monkeypatch,
):
    _, path = small_curriculum
    controller = LauncherController(tmp_path / "review", course=load_course(path), debug=True)
    controller.enter_lesson("a02")
    app = LauncherApp(controller)
    fills = []
    original_rect = pygame.draw.rect

    def record_rect(surface, color, rect, *args, **kwargs):
        if color == app.theme.content_card and not args and not kwargs.get("width", 0):
            fills.append(pygame.Rect(rect))
        return original_rect(surface, color, rect, *args, **kwargs)

    monkeypatch.setattr(pygame.draw, "rect", record_rect)
    try:
        app.render()
        card_width = app.background_rect.width - CONTENT_COLUMN_SIDE_MARGIN * 2
        text_cards = [rect for rect in fills if rect.width == card_width]
        picture, caption = app.illustration_rects
        assert len(text_cards) == 3
        assert all(not card.colliderect(picture) for card in text_cards)
        assert text_cards[0].bottom < picture.top < caption.bottom < text_cards[1].top
        assert text_cards[1].bottom < text_cards[2].top
        assert caption in fills
        assert caption.width < picture.width
        assert app.background_rect.contains(text_cards[-1])
    finally:
        controller.shutdown()
        pygame.quit()


@pytest.mark.parametrize("mutation", ["late_receipt", "early_change", "small_coins", "missing_zero", "wrong_price", "wrong_count", "swapped_products", "reversed_change", "extra_read"])
def test_checkout_rejects_incomplete_or_mistimed_solutions(tmp_path, mutation):
    source = (ROOT / "lessons/a09_bonus/reference/checkout.py").read_text()
    if mutation == "late_receipt":
        first = source.index('print(ears_count, ears_cost)')
        last = source.index('print("Сколько галлеонов', first)
        receipt = source[first:last]
        source = source[:first] + source[last:] + "\n" + receipt
    elif mutation == "early_change":
        source = 'print(0, 0, 0)\n' + source
    elif mutation == "small_coins":
        source = source.replace("change_galleons = change // knuts_in_galleon", "change_galleons = 0")
    elif mutation == "missing_zero":
        source = source.replace('print(puffs_count, puffs_cost)', "")
    elif mutation == "wrong_price":
        source = source.replace("snacks_price = 23", "snacks_price = 24")
    elif mutation == "wrong_count":
        source = source.replace("print(ears_count, ears_cost)", "print(ears_count + 1, ears_cost)")
    elif mutation == "swapped_products":
        source = source.replace("print(ears_count, ears_cost)\nprint(snacks_count, snacks_cost)",
                                "print(snacks_count, snacks_cost)\nprint(ears_count, ears_cost)")
    elif mutation == "reversed_change":
        source = source.replace("print(change_galleons, change_sickles, change_knuts)",
                                "print(change_knuts, change_sickles, change_galleons)")
    else:
        source += "\ninput()\n"
    path = tmp_path / "checkout.py"
    path.write_text(source)
    result = run_check(path, "a09_bonus_checkout", lesson_id="a09_bonus")
    assert not result.passed


@pytest.mark.parametrize("style", ["labels_with_typos", "extra_spaces", "questions_with_prices"])
def test_checkout_checks_numbers_not_incidental_output_text(tmp_path, style):
    source = (ROOT / "lessons/a09_bonus/reference/checkout.py").read_text()
    if style == "labels_with_typos":
        replacements = {
            "print(ears_count, ears_cost)": 'print("Удлинтели:", ears_count, "штук —", ears_cost, "сиклй")',
            "print(snacks_count, snacks_cost)": 'print("Завтроки:", snacks_count, "коробок —", snacks_cost)',
            "print(puffs_count, puffs_cost)": 'print("Пушистки:", puffs_count, "шт.", puffs_cost)',
            "print(total)": 'print("Итго:", total, "сиклй")',
            "print(change_galleons, change_sickles, change_knuts)": 'print("Сдча:", change_galleons, "галл.", change_sickles, "сикл.", change_knuts, "кн.")',
        }
    elif style == "extra_spaces":
        replacements = {
            "print(ears_count, ears_cost)": 'print(" ", ears_count, "\\t", ears_cost, " ")',
            "print(snacks_count, snacks_cost)": 'print(" ", snacks_count, "  ", snacks_cost)',
            "print(puffs_count, puffs_cost)": 'print(puffs_count, " | ", puffs_cost)',
            "print(total)": 'print(" ", total, " ")',
            "print(change_galleons, change_sickles, change_knuts)": 'print(change_galleons, ";", change_sickles, ";", change_knuts)',
        }
    else:
        replacements = {
            'print("Сколько удлинителей ушей покупаешь?")': 'print("Сколько удлинителей по 17 сиклей покупаешь?")',
            'print("Сколько коробок забастовочных завтраков покупаешь?")': 'print("Сколько коробок по 23 сикля покупаешь?")',
            'print("Сколько карликовых пушистиков покупаешь?")': 'print("Сколько пушистиков по 31 сиклю покупаешь?")',
            'print("Сколько галлеонов отдаёшь для оплаты?")': 'print("В 1 галлеоне 17 сиклей, а в сикле 29 кнатов. Сколько галлеонов отдаёшь?")',
        }
    for original, replacement in replacements.items():
        source = source.replace(original, replacement)
    path = tmp_path / "checkout.py"
    path.write_text(source)
    result = run_check(path, "a09_bonus_checkout", lesson_id="a09_bonus")
    assert result.passed, result.message


def test_checkout_preserves_real_receipt_and_change_at_input_boundaries():
    job = start_student_process(ROOT / "lessons/a09_bonus/reference/checkout.py", mode="interactive", timeout=2)
    answers = ("4", "2", "0", "8", "1", "7")
    try:
        for index, answer in enumerate(answers):
            deadline = time.monotonic() + 3
            while not job.waiting_for_input:
                assert job.poll_result() is None
                assert time.monotonic() < deadline
                time.sleep(0.01)
            if index == 3:
                assert "\n4 68\n2 46\n0 0\n114\n" in job.output
                assert "1 6 7" not in job.output.splitlines()
            job.send_input(answer)
        deadline = time.monotonic() + 3
        result = None
        while result is None:
            result = job.poll_result()
            assert time.monotonic() < deadline
            time.sleep(0.01)
        assert result.passed
        assert "\n4 68\n2 46\n0 0\n114\n" in result.output
        assert result.output.splitlines()[-1] == "1 6 7"
    finally:
        job.cancel()


def test_capstone_reference_uses_only_established_student_syntax():
    import ast
    tree = ast.parse((ROOT / "lessons/a09_bonus/reference/checkout.py").read_text())
    allowed = (ast.Module, ast.Assign, ast.Expr, ast.Name, ast.Constant, ast.Call,
               ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Load, ast.Store)
    assert all(isinstance(node, allowed) for node in ast.walk(tree))
    assert {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call)} == {"print", "input", "int"}


def test_assets_have_valid_transparency_and_include_only_selected_artwork():
    assets = ROOT / "lessons/a09_bonus/assets"
    names = {path.stem for path in assets.glob("*.png")}
    assert names == {"diagon_alley", "twins", "extendable_ears", "skiving_snackboxes",
                     "pygmy_puff", "price_scroll", "platform_plaque", "galleon", "sickle", "knut"}
    for name in names - {"diagon_alley"}:
        surface = pygame.image.load(assets / f"{name}.png")
        bounds = surface.get_bounding_rect()
        assert bounds.width > 0 and bounds.height > 0
        # Generated soft mattes may retain negligible (1/255) corner alpha.
        # The contract is a visually transparent cutout, not byte-exact pixels.
        assert surface.get_at((0, 0)).a <= 2
        assert surface.get_at((surface.get_width() - 1, surface.get_height() - 1)).a <= 2


@pytest.mark.parametrize("size", [(1180, 760), (1600, 1000)])
def test_capstone_artwork_and_fixed_controls_do_not_overlap(tmp_path, size):
    controller = LauncherController(tmp_path / "child", debug=True)
    controller.enter_lesson("a09_bonus")
    app = LauncherApp(controller)
    app.screen = pygame.display.set_mode(size)
    try:
        for task in controller.lesson.tasks:
            controller.select_task(task.id)
            if task.is_coding:
                controller.latest_output = "receipt\nchange\n"
                controller.revealed_hints[task.id] = len(task.hints)
            for scroll in (0, 100000):
                app.scroll = scroll
                app.render()
                body = app.background_rect
                assert body.top > GLOBAL_TOOLBAR_BOTTOM
                for rect in app.illustration_rects:
                    assert body.left <= rect.left < rect.right <= body.right
                if app.plaque_rect is not None:
                    assert not app.plaque_rect.colliderect(app.lesson_title_rect)
                if task.is_coding:
                    assert body.bottom < app.output_card_rect.top
                    assert app.output_card_rect.bottom < app.note_card_rect.top
                for button in app.buttons:
                    if button.action in {"open", "run", "previous", "next"}:
                        assert body.bottom < button.rect.top
    finally:
        controller.shutdown()
        pygame.quit()
