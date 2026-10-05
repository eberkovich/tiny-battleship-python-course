"""A4 output contracts; all tasks use expressions without grouping parentheses.

Focused practice: arithmetic, quoted text prediction, addition-to-product
rewriting with a changed count, whole groups, and a wrong operator. Independent
transfer: a two-step exchange, not a shopping/sharing example with changed numbers.

Exchange source: Challenging Word Problems 2, Singapore Math Inc., printed
page 138, exercise 2. Publisher sample:
https://singapore-math.s3.us-west-2.amazonaws.com/Samples/sf_cwpcc2.pdf
Original: 2 squares -> 3 triangles; 2 triangles -> 6 circles; start with
2 squares. Adaptation: start with 52 squares and use 74 circles per exchange.
Only numerical data changes. Both exchanges remain exact. No individual author
is credited in the verified sample; do not invent one.

Editorial benchmarks: Think Python, chapter 1 (operators/expressions), and
Invent Your Own Computer Games with Python, chapter 2 (evaluation before print).
Checks verify output, not source spelling or conceptual mastery.
"""

from lessons.checks import check_output


CASES = {
    "a04_score": (("8036",), "Проверь начисленные и снятые баллы. Выведи только оставшееся количество."),
    "a04_shorten": (("22257",), "Теперь нужно сложить число 2473 девять раз, а не четыре. Проверь множитель и выведи одно число."),
    "a04_boxes": (("24",), "Посчитай только полные коробки по 24 бусины. Неполная коробка в ответ не входит."),
    "a04_repair": (("180",), "После деления результат нужно увеличить в два раза, а не прибавить к нему 2."),
    "a04_exchange": (("2886",), "Программа запустилась, но количество кружков пока не подходит. Проверь оба правила обмена и начальное количество квадратов."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
