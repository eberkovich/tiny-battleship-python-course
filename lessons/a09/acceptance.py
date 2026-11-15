"""A10: named actions, definition/call order, indentation, and composition.

Editorial benchmarks, consulted for the authored explanations:
Think Python 3e, 3.1 and 3.3 (definitions and calls):
https://allendowney.github.io/ThinkPython/chap03.html
Invent Your Own Computer Games with Python, chapter 5, Functions in Dragon Realm:
https://inventwithpython.com/invent4thed/chapter5.html
Python for Kids, official lesson plans, topic 6, Code Reuse:
https://nostarch.com/download/samples/PFK_lessonplans_full.pdf

The book-refactoring premise, four scenes, deliberate typos, corrected reaction,
divider, and shorter-code requirement were supplied/approved by the user.
It is guided refactoring, not the lesson's independent reasoning challenge.
The window adapts Think Python 2e, 3.14, exercise 3 (two-by-two printed grid):
https://greenteapress.com/thinkpython2/html/thinkpython2004.html
Use shorter panes, complete printed rows, and no arguments, print keywords,
string operations, loops, conditions, return, or global state.

Only the explicit refactoring contract inspects source structure/line count.
Function behavior and real invocation counts are checked in the child process;
names/formatting/decomposition are otherwise not prescribed.
"""

import ast
import contextlib
import io
import tokenize
from types import FunctionType

from lessons.checks import Outcome, check_output


REACTION = "Гарри, Рон и Гермиона закатили глаза"
SCENES = (
    ("Локонс объявил конкурс на лучший портрет Локонса.", "Первое место занял Локонс."),
    ("Перси сказал, что сейчас подробно расскажет о толщине донышек котлов.",),
    ("Трелони сказала: «Я чувствую, что восемнадцать из вас не доживут до выпускных экзаменов».",),
    ("Хагрид погладил трёхголового пса: «Ласковый такой, мухи не обидит!»",),
)
WINDOW = (
    "+---+---+", "|   |   |", "|   |   |", "+---+---+",
    "|   |   |", "|   |   |", "+---+---+",
)
EXPECTED = {
    "a09_book": tuple(line for scene in SCENES for line in (*scene, REACTION, "***")),
    "a09_ticket": ("Билет", "Место 8", "Билет", "Место 8"),
    "a09_window": WINDOW,
}
FAILURES = {
    "a09_book": "Сохрани все четыре эпизода и их порядок. После каждого выведи правильную фразу, затем три звёздочки на отдельной строке.",
    "a09_ticket": "При каждом вызове show_ticket должны появляться обе строки: Билет, затем Место 8.",
    "a09_window": "Проверь рисунок: четыре стекла, общие границы, по три пробела между вертикальными линиями и никаких лишних строк.",
}


def check(task_id, snapshot, output):
    return check_output(output, EXPECTED[task_id], FAILURES[task_id])


def _function_outputs(source, namespace, calls):
    """Probe only already-called student functions that accept empty parentheses."""
    for name, function in namespace.items():
        if not isinstance(function, FunctionType):
            continue
        code = function.__code__
        if code.co_filename != str(source) or not calls[code]:
            continue
        if code.co_argcount or code.co_kwonlyargcount:
            continue
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            function()
        yield name, calls[code], tuple(line.strip() for line in captured.getvalue().strip().splitlines())


def check_program(task_id, source, namespace, calls):
    if task_id == "a09_book":
        text = source.read_text(encoding="utf-8")
        statements = [node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.stmt)]
        if len({node.lineno for node in statements}) != len(statements):
            return Outcome(False, "Запиши каждое действие на отдельной строке. Склеивание действий не считается сокращением.")
        ignored = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                   tokenize.DEDENT, tokenize.ENDMARKER}
        code_lines = set()
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type not in ignored:
                code_lines.update(range(token.start[0], token.end[0] + 1))
        if len(code_lines) >= 13:
            return Outcome(False, f"Пока строк с кодом {len(code_lines)}. Нужно меньше 13: вынеси и фразу, и разделитель в одну функцию.")
        if any(count == 4 and output == (REACTION, "***")
               for _, count, output in _function_outputs(source, namespace, calls)):
            return Outcome(True, "Получилось! Четыре вызова одной функции заменили повторяющиеся строки, и код стал короче.")
        return Outcome(False, "Одна и та же функция должна выводить фразу и разделитель и вызываться во всех четырёх эпизодах.")

    functions = list(_function_outputs(source, namespace, calls))
    if task_id == "a09_ticket":
        if ("show_ticket", 2, ("Билет", "Место 8")) in functions:
            return Outcome(True, "Получилось! Оба print относятся к функции, поэтому каждый билет полный.")
        return Outcome(False, "Оставь оба вызова show_ticket. Функция должна выводить обе строки билета при каждом вызове.")

    if ("draw_window", 1, WINDOW) not in functions:
        return Outcome(False, "Определи draw_window и один раз вызови её после определений. Этот вызов должен выводить всё окно.")
    reused_rows = {
        row for name, count, output in functions
        if name != "draw_window" and count >= 2 and output and all(row in WINDOW for row in output)
        for row in output
    }
    if not set(WINDOW).issubset(reused_rows):
        return Outcome(False, "Вынеси повторяющиеся части окна в функции и используй их повторными вызовами, а не копиями print.")
    return Outcome(True, "Получилось! Окно собрано из повторных вызовов твоих функций.")
