"""A9¾: one independent purchase → receipt → payment → change use case.

Starting point: Code Avengers Python 1, 7.3–7.4, purchases and typed quantities:
https://assets.codeavengers.com/file/cloud/python/1/lesson-plans/ca-py1-instructions.pdf
Adaptation: three magical goods with fictional prices, integer arithmetic only,
no discount; payment/change is our extension, not part of the cited worksheet.
Currency: https://www.harrypotter.com/fact-file/objects/wizarding-money
Goods: https://www.harrypotter.com/fact-file/locations/weasleys-wizard-wheezes
No completed algorithm or hidden-input examples appear in the child's starter.
"""

import re

from lessons.checks import Outcome


CASES = (
    ("2", "1", "3", "12", "4", "7"),
    ("1", "0", "0", "1", "0", "0"),
    ("0", "1", "0", "2", "3", "8"),
    ("0", "0", "1", "2", "0", "0"),
    ("0", "0", "0", "0", "0", "0"),
    ("0", "0", "0", "0", "17", "29"),
    ("1", "0", "0", "2", "1", "1"),
    ("0", "0", "0", "0", "16", "28"),
    ("0", "0", "0", "1", "0", "0"),
    ("0", "0", "0", "0", "0", "29"),
    ("3", "0", "4", "10", "5", "19"),
    ("100", "100", "100", "500", "0", "28"),
    ("7", "3", "11", "40", "10", "18"),
)


def input_cases(task_id):
    if task_id != "a09_bonus_checkout":
        raise KeyError(task_id)
    return CASES


def numeric_rows(text):
    # Printed questions may mention prices; they are not result rows.
    return [tuple(map(int, re.findall(r"(?<!\w)-?\d+(?!\w)", line)))
            for line in text.splitlines() if "?" not in line and re.search(r"\d", line)]


def check_interaction(task_id, answers, output_segments):
    if task_id != "a09_bonus_checkout":
        raise KeyError(task_id)
    quantities = tuple(map(int, answers[:3]))
    subtotals = tuple(quantity * price for quantity, price in zip(quantities, (17, 23, 31)))
    total = sum(subtotals)
    receipt = numeric_rows(output_segments[3])
    expected_rows = list(zip(quantities, subtotals)) + [(total,)]
    if receipt != expected_rows:
        return Outcome(False, "До вопросов об оплате выведи четыре строки чека: количество и стоимость каждого товара в сиклях, затем общую стоимость. Проверь порядок товаров и не пропускай нулевые покупки.")
    if any(len(row) == 3 for segment in output_segments[:-1] for row in numeric_rows(segment)):
        return Outcome(False, "Показывай сдачу только после всех трёх ответов об оплате.")
    galleons, sickles, knuts = map(int, answers[3:])
    change = galleons * 493 + sickles * 29 + knuts - total * 29
    expected_galleons, remainder = divmod(change, 493)
    expected_sickles, expected_knuts = divmod(remainder, 29)
    rows = numeric_rows(output_segments[-1])
    if rows != [(expected_galleons, expected_sickles, expected_knuts)]:
        return Outcome(False, "После оплаты выведи три числа: количество галлеонов, сиклей и кнатов в этом порядке. Используй как можно больше крупных монет и не пропускай нулевые количества.")
    return Outcome(True, "Касса готова! Чек и сдача верны при разных покупках и оплате.")
