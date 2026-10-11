"""A9: text/integer distinction, int, and independent numeric-input problems.

Explanatory benchmark: Automate the Boring Stuff, 3e, ch. 1, conversions:
https://automatetheboringstuff.com/3e/chapter1.html
Birthday adaptation: Raspberry Pi Foundation About Me, birth-year step:
https://projects.raspberrypi.org/en/projects/about-me
Number trick: NRICH Your number was... (add 4, double, subtract 7):
https://nrich.maths.org/problems/your-number-was
Farm: NRICH Heads and Feet (original 8 heads, 22 feet). Adapt the known totals
to typed data and check multiple valid populations, including single-species:
https://nrich.maths.org/problems/heads-and-feet
These are adaptations, not claims that the original sources teach this Python.
No invalid-input handling, float, loops, conditions, or student def is required.
"""

from lessons.checks import check_output


CASES = {
    "a09_input_birthday": (("2017",), ("2000",), ("2035",), ("2023",)),
    "a09_input_conversion_repair": (("25",), ("5",), ("137",)),
    "a09_input_number_trick": (("3",), ("25",), ("201",), ("20001",)),
    "a09_input_farm": (("8", "22"), ("7", "20"), ("1", "2"), ("1", "4"), ("37", "114")),
}


def input_cases(task_id):
    return CASES[task_id]


def check_inputs(task_id, answers, output):
    if task_id == "a09_input_birthday":
        expected = (str(2035 - int(answers[0])),)
        failure = "Вычисли возраст в день рождения в 2035 году из введённого года."
    elif task_id == "a09_input_conversion_repair":
        expected = (str(int(answers[0]) - 5),)
        failure = "Сохрани результат int перед вычитанием пяти листов."
    elif task_id == "a09_input_number_trick":
        expected = (str((int(answers[0]) - 1) // 2),)
        failure = "Проверь, восстанавливает ли твоё вычисление исходное число при разных результатах фокуса."
    else:
        animals, legs = map(int, answers)
        sheep = (legs - 2 * animals) // 2
        expected = (str(animals - sheep), str(sheep))
        failure = "Проверь и животных, и ноги. Выведи сначала количество кур, затем овец; оба количества нужны, даже если одно равно 0."
    return check_output(output, expected, failure)
