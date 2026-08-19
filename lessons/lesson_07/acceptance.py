from lessons.lesson_06.acceptance import FLEET
from lessons.phase_a_checks import (
    message_events,
    expect_output,
    expect_project_fleet,
    failed,
    passed,
)


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_07_exercise_01":
        return expect_output(output, "Начинаем бой!")
    if task_id == "lesson_07_exercise_02":
        if message_events(snapshot) != [("Корабль выбран", "Готово")]:
            return failed("Покажи диалог с сообщением «Корабль выбран» и кнопкой «Готово».")
        return passed("Верно! Диалог появился с нужным сообщением.")
    if task_id == "lesson_07_exercise_03":
        if message_events(snapshot) != [("Корабли на месте", "Вперёд")]:
            return failed("Проверь порядок аргументов message и label.")
        return passed("Верно! В диалоге сообщение и подпись кнопки стоят на своих местах.")
    if task_id == "lesson_07_project":
        fleet = expect_project_fleet(snapshot, FLEET, 10)
        if not fleet.passed:
            return fleet
        if ("Флот готов!", "Начать бой") not in message_events(snapshot):
            return failed("После расстановки покажи диалог с кнопкой «Начать бой».")
        return passed("Флот готов. Теперь можно начинать бой!")
    if task_id == "lesson_07_star":
        expected = [
            ("Три", "Дальше"),
            ("Два", "Дальше"),
            ("Один", "Дальше"),
            ("Огонь!", "Дальше"),
        ]
        if message_events(snapshot) != expected:
            return failed("Проверь четыре диалога, порядок сообщений и подпись кнопки.")
        return passed("Звёздочка твоя! Обратный отсчёт работает.")
    return failed("Для этого задания пока нет проверки.")
