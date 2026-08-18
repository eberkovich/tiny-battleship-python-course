from battleship_ui import fake_ui
from battleship_ui.constants import DECK_IDLE, ENEMY, PLAYER
from lessons.lesson_01.acceptance import check
from launcher.course import load_course, load_lesson, load_sections


def setup_function() -> None:
    fake_ui._reset()


def test_project_requires_both_visible_boards() -> None:
    fake_ui.show_board(PLAYER)
    result = check("project", fake_ui._snapshot())

    assert not result.passed
    assert "show_board(ENEMY)" in result.message


def test_all_lesson_checks_are_behavioral() -> None:
    fake_ui.show_board(PLAYER)
    fake_ui.draw_deck(PLAYER, 2, 4, DECK_IDLE)
    assert check("exercise_02", fake_ui._snapshot()).passed

    fake_ui._reset()
    fake_ui.show_miss(ENEMY, 4, 2)
    fake_ui.show_board(ENEMY)
    assert check("exercise_03", fake_ui._snapshot()).passed


def test_star_checks_only_introduced_operations() -> None:
    fake_ui.show_board(PLAYER)
    fake_ui.show_board(ENEMY)
    for x in (3, 4, 5):
        fake_ui.draw_deck(PLAYER, x, 5, DECK_IDLE)
    fake_ui.show_miss(ENEMY, 7, 3)

    assert check("star", fake_ui._snapshot()).passed


def test_star_starter_contains_previously_completed_board_setup() -> None:
    lesson = load_lesson()
    starter = lesson.task("star").template.read_text(encoding="utf-8")
    star_text = load_sections(lesson.content)["star"].lower()

    assert "show_board(PLAYER)" in starter
    assert "show_board(ENEMY)" in starter
    assert "используй только знакомые команды `draw_deck` и `show_miss`" in star_text


def test_public_api_is_not_used_before_its_introduction_step() -> None:
    course = load_course()
    lesson = course.lessons[0]
    sections = load_sections(lesson.content)

    for api_name, reference in course.api_references.items():
        introduction_index = next(
            index
            for index, task in enumerate(lesson.tasks)
            if task.id == reference.introduced_in
        )
        assert api_name in sections[reference.introduced_in]
        for task in lesson.tasks[:introduction_index]:
            assert api_name not in sections[task.section]
            if task.template is not None:
                assert api_name not in task.template.read_text(encoding="utf-8")


def test_child_content_stays_in_russian_structure_and_lesson_scope() -> None:
    lesson = load_lesson()
    sections = load_sections(lesson.content)
    content = "\n".join(sections.values()).lower()

    for required in (
        "первое знакомство",
        "вспомогательные команды",
        "как устроена команда",
        "координаты и корабли",
        "нарисуй однопалубный корабль",
        "пишем игру",
        "задача со звёздочкой",
        "итоги урока",
    ):
        assert required in content
    assert [task.id for task in lesson.tasks[:4]] == [
        "intro",
        "api",
        "exercise_01",
        "coordinates",
    ]
    assert lesson.task("intro").title == "Первое знакомство"
    assert lesson.task("recap").kind == "summary"
    assert "show_board" in sections["api"]
    assert "draw_deck" not in sections["api"]
    assert "show_miss" not in sections["api"]
    assert "draw_deck" in sections["coordinates"]
    assert "deck_idle" in sections["coordinates"].lower()
    assert "Система координат — это способ дать каждой клетке точный адрес" in sections[
        "coordinates"
    ]
    assert sections["coordinates"].index("Система координат") < sections[
        "coordinates"
    ].index("draw_deck")
    assert sections["coordinates"].index("Система координат") < sections[
        "coordinates"
    ].index("show_miss")
    assert "`board` —" in sections["api"]
    for argument in ("`board` —", "`x` —", "`y` —", "`state` —"):
        assert argument in sections["coordinates"]
    assert sections["coordinates"].count("`board` —") == 2
    assert "Возможные значения:" in sections["api"]
    assert "enum" not in content
    assert "перечислен" not in content
    assert "draw_water" not in content
    assert "water_idle" not in content
    assert "water_fired" not in content
    assert "предскажи клетку" not in content
    assert "покажи пальцем" not in content
    assert "thonny" not in content
    assert "exercise_01.py" not in content
    assert "battleship.py" not in content
    assert "show_board(player)" not in sections["project"].lower()
    assert "show_board(enemy)" not in sections["project"].lower()
    assert sections["intro"].count("\n---\n") == 0
    assert sections["api"].count("\n---\n") == 2
    assert sections["coordinates"].count("\n---\n") == 2
    assert "framework" not in content
    assert "фреймвор" not in content
    assert "библиотек" not in content
    assert "полностью создашь игру «морской бой»" in sections["intro"].lower()
    assert "каждый такой корабль занимает одну клетку" in sections["intro"].lower()
    assert "сам напишешь всю логику игры" in sections["intro"].lower()
    assert "вспомогательные команды" in sections["intro"].lower()
    assert "следующих разделах" in sections["intro"].lower()
    assert "подключает вспомогательные команды" in sections["api"].lower()
    assert "функции python" in sections["api"].lower()
    assert "вызовом функции" in sections["api"].lower()
    assert "аргументом" in sections["api"].lower()
    assert "синтаксисом вызова" in sections["api"].lower()
    assert sections["coordinates"].index("разделяют запятыми") < sections[
        "coordinates"
    ].index("draw_deck(board")
    for task in lesson.tasks:
        if not task.is_coding:
            continue
        task_text = sections[task.section]
        goal, note = task_text.split("> [!NOTE]", maxsplit=1)
        assert "Открой редактор" not in goal
        note_lines = [line.removeprefix("> ") for line in note.strip().splitlines()]
        assert note_lines == [
            "Открой редактор → выполни задание → сохрани изменения → "
            "нажми **«Запустить»**."
        ]
        assert "Запустить" not in goal
    for unintroduced in ("переменн", "цикл", "список", "условие"):
        assert unintroduced not in content
