"""A2 output contracts. Reasoning answers are not Python algorithms.

The houses task adapts the two-condition design of Zhenya Katz's
"Igray, reshay" workbook, shown by its publisher in the "Koshkin dom" example:
https://deti.mann-ivanov-ferber.ru/2023/11/18/10-veselyx-golovolomok-dlya-razvitiya-logiki-skachat-zadaniya/
All house counts are our own; no book images or pages are reproduced.
The stickers task is an original arithmetic exercise.
"""

from lessons.checks import check_output


CASES = {
    "a02_greeting": (("Привет!",), "Покажи только сообщение Привет! Проверь текст внутри кавычек."),
    "a02_repair": (("8",), "Скобки теперь читаются, но результат должен быть только числом 8."),
    "a02_houses": (("2",), "Программа запустилась, но ответ пока не подходит. Проверь оба условия для каждого дома и посчитай только подходящие дома."),
    "a02_stickers": (("11",), "Программа запустилась, но ответ пока не подходит. Учти подарки обоим друзьям, а затем полученные наклейки."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
