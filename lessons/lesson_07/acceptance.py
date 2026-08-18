from lessons.lesson_06.acceptance import FLEET
from lessons.phase_a_checks import (
    button_events,
    expect_output,
    expect_project_fleet,
    failed,
    passed,
)


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_07_exercise_01":
        return expect_output(output, "Начинаем бой!")
    if task_id == "lesson_07_exercise_02":
        if button_events(snapshot) != [("Корабль выбран", "Готово")]:
            return failed("Покажи сообщение «Корабль выбран» и кнопку «Готово».")
        return passed("Верно! Кнопка появилась с нужным сообщением.")
    if task_id == "lesson_07_exercise_03":
        if button_events(snapshot) != [("Корабли на месте", "Вперёд")]:
            return failed("Используй обе переменные для сообщения и кнопки.")
        return passed("Верно! Кнопка собрана из сохранённых строк.")
    if task_id == "lesson_07_project":
        fleet = expect_project_fleet(snapshot, FLEET, 10)
        if not fleet.passed:
            return fleet
        if ("Флот готов!", "Начать бой") not in button_events(snapshot):
            return failed("После расстановки покажи кнопку «Начать бой».")
        return passed("Флот готов. Теперь можно начинать бой!")
    if task_id == "lesson_07_star":
        expected = [("Первый шаг", "Дальше"), ("Второй шаг", "Готово")]
        if button_events(snapshot) != expected:
            return failed("Проверь тексты и порядок двух кнопок.")
        return passed("Звёздочка твоя! Два шага идут в правильном порядке.")
    return failed("Для этого задания пока нет проверки.")
