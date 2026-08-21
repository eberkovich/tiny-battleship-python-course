import re

from battleship_ui import fake_ui
from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER
from launcher.course import load_course, load_sections
from lessons.lesson_01.acceptance import check as check_boards
from lessons.lesson_01_coordinates.acceptance import check as check_coordinates


def setup_function() -> None:
    fake_ui._reset()


def test_first_project_requires_both_visible_boards() -> None:
    fake_ui.show_board(PLAYER)
    result = check_boards("project", fake_ui._snapshot(), "")

    assert not result.passed
    assert "show_board(ENEMY)" in result.message


def test_coordinate_project_requires_boards_and_first_ship() -> None:
    fake_ui.show_board(PLAYER)
    fake_ui.show_board(ENEMY)
    result = check_coordinates(
        "lesson_01_coordinates_project", fake_ui._snapshot(), ""
    )
    assert not result.passed
    assert "(2, 2)" in result.message

    fake_ui.draw_deck(PLAYER, 2, 2, DECK_IDLE)
    assert check_coordinates(
        "lesson_01_coordinates_project", fake_ui._snapshot(), ""
    ).passed


def test_coordinate_exercises_and_star_are_behavioral() -> None:
    fake_ui.show_board(PLAYER)
    fake_ui.draw_deck(PLAYER, 3, 7, DECK_IDLE)
    assert check_coordinates(
        "lesson_01_coordinates_exercise_02", fake_ui._snapshot(), ""
    ).passed

    fake_ui._reset()
    fake_ui.show_board(PLAYER)
    fake_ui.show_board(ENEMY)
    for x, y in ((2, 2), (3, 5), (4, 8), (9, 2), (8, 5), (7, 8)):
        fake_ui.draw_deck(PLAYER, x, y, DECK_IDLE)
    assert check_coordinates(
        "lesson_01_coordinates_star", fake_ui._snapshot(), ""
    ).passed


def test_mirror_starter_contains_completed_board_setup() -> None:
    lesson = load_course().lesson("lesson_01_coordinates")
    starter = lesson.task("lesson_01_coordinates_star").template.read_text(
        encoding="utf-8"
    )
    star_text = load_sections(lesson.content)["star"].lower()

    assert "show_board(PLAYER)" in starter
    assert "show_board(ENEMY)" in starter
    assert starter.count("draw_deck(PLAYER") == 3
    assert "зеркальн" in star_text


def test_public_api_is_not_used_before_its_introduction_step() -> None:
    course = load_course()
    ordered_tasks = [
        (lesson, task) for lesson in course.lessons for task in lesson.tasks
    ]
    task_ids = [task.id for _, task in ordered_tasks]
    for api_name, reference in course.api_references.items():
        if reference.introduced_in not in task_ids:
            continue
        introduction = task_ids.index(reference.introduced_in)
        introduction_lesson, introduction_task = ordered_tasks[introduction]
        sections = load_sections(introduction_lesson.content)
        assert api_name in sections[introduction_task.section]
        for lesson, task in ordered_tasks[:introduction]:
            assert api_name not in load_sections(lesson.content)[task.section]
            if task.template is not None:
                assert api_name not in task.template.read_text(encoding="utf-8")


def test_first_lesson_contains_only_board_milestone_material() -> None:
    lesson = load_course().lesson("lesson_01")
    sections = load_sections(lesson.content)
    content = "\n".join(sections.values()).lower()

    assert [task.id for task in lesson.tasks] == [
        "intro",
        "support",
        "api",
        "execution",
        "comments",
        "exercise_comments",
        "exercise_01",
        "exercise_enemy",
        "project",
        "recap",
    ]
    for required in (
        "первое знакомство",
        "вспомогательные команды",
        "как устроена команда",
        "строка за строкой",
        "комментарии в коде",
        "пишем игру",
        "итоги урока",
    ):
        assert required in content
    assert "show_board" in sections["api"]
    assert "draw_deck" not in content
    assert "show_miss" not in content
    assert "в упражнениях" in sections["recap"].lower()
    assert "в твоей игре теперь" in sections["recap"].lower()


def test_coordinate_lesson_introduces_and_integrates_draw_deck() -> None:
    lesson = load_course().lesson("lesson_01_coordinates")
    sections = load_sections(lesson.content)
    content = "\n".join(sections.values()).lower()

    coordinate_article = sections["coordinates"].lower()
    assert "систем" in coordinate_article
    assert "координат" in coordinate_article
    assert "draw_deck(board, x, y, state)" in sections["deck_api"]
    assert "draw_deck" in sections["project"]
    assert "show_miss" not in content
    for argument in ("`board` —", "`x` —", "`y` —", "`state` —"):
        assert argument in sections["deck_api"]
    assert "в упражнениях" in sections["recap"].lower()
    assert "в твоей игре теперь" in sections["recap"].lower()

    for task in lesson.tasks:
        if not task.is_coding:
            continue
        goal, note = sections[task.section].split("> [!NOTE]", maxsplit=1)
        assert "Открой редактор" not in goal
        note_lines = [line.removeprefix("> ") for line in note.strip().splitlines()]
        assert note_lines == [
            "Открой редактор → выполни задание → сохрани изменения → "
            "нажми **«Запустить»**."
        ]
    assert re.search(r"\bidle\b", content) is None
