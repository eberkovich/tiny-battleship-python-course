"""A3 output contracts. The race deduction is an original task."""

from lessons.checks import check_output


CASES = {
    "a03_countdown": (("3", "2", "1"), "Покажи 3, затем 2, затем 1. Каждое число — на отдельной строке."),
    "a03_announcements": (("Старт", "Бег", "Финиш"), "Проверь порядок событий: Старт, Бег, Финиш. Каждое объявление — на отдельной строке."),
    "a03_race": (("1", "4", "2", "3"), "Программа запустилась, но порядок пока не подходит. Проверь все три подсказки и покажи каждый номер на отдельной строке."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
