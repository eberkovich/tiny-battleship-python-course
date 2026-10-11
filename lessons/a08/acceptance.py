"""A8: standard input, separate saved answers, and multiple print arguments.

Editorial starting point: Invent Your Own Computer Games with Python, ch. 2:
https://inventwithpython.com/invent4thed/chapter2.html
Independent story: adaptation of Bryson Payne's Mad Libs challenge, Teach Your
Kids to Code, ch. 1, pp. 8-9 (publisher's detailed contents):
https://nostarch.com/download/Teach_Your_Kids_to_Code_detailedTOC.pdf
Russian templates avoid requiring string formatting or grammatical inflection.
Private cases compare final answers, not incidental question wording.
"""

from lessons.checks import check_output


CASES = {
    "a08_introduce": (("Луна",), ("Капитан Сова",), ("7",)),
    "a08_lost_answer": (("Искры", "Вперёд!"), ("Ночные совы", "Не спать!"), ("А", "Б")),
    "a08_announcement": (("шляпа", "библиотека"), ("ключ от ракеты", "Лунная база"), ("мяч", "зал")),
    "a08_story": (("робот", "Лунная база", "есть печенье"), ("Сова", "Тихий лес", "видеть в темноте"), ("Дракон", "Остров", "считать звёзды")),
}


def input_cases(task_id):
    return CASES[task_id]


def check_inputs(task_id, answers, output):
    if task_id == "a08_introduce":
        expected = ("Наш участник:", answers[0])
    elif task_id == "a08_lost_answer":
        expected = answers
    elif task_id == "a08_announcement":
        item, place = answers
        expected = (f"Найден предмет: {item} Место: {place}",)
    else:
        hero, place, power = answers
        expected = (
            f"В месте под названием {place} появился герой: {hero}",
            f"{hero} объявляет: моя суперсила — {power}",
            f"Теперь {place} ждёт новых приключений!",
        )
    return check_output(output, expected, "Проверь ответы и порядок строк после последнего вопроса. Используй введённые значения, а не готовые слова.")
