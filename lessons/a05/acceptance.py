"""A5 output contracts: grouping precedes its use in every task.

Practice: predict a subtraction with an inner sum, choose grouping for a target,
repair an unmatched call parenthesis, then independently model two word
problems. Worked examples teach notation, not the word problems' methods.

Source for saving: Challenging Word Problems 2, Singapore Math Inc., printed
page 155, exercise 8. Original: already $5, saves $2/day, dictionary costs $13.
Adaptation: 137 already saved, 29/day, price 1210; currency localized to rubles.
Source for ropes: same book, reproduced by Cassandra Turner:
https://singaporemathsource.com/word-problem-wednesday-dogs-and-ropes/
Original: combined length 36 inches, difference 4 inches, find longer rope.
Adaptation: total 2367 cm, difference 683 cm. Unit localized; reasoning unchanged.
Publisher sample for the saving problem:
https://singapore-math.s3.us-west-2.amazonaws.com/Samples/sf_cwpcc2.pdf
No individual author is credited in the verified sample; publisher attribution
is used instead. Both problems remain exact positive-integer calculations.

Editorial benchmark: Think Python, chapter 1, expressions and parentheses.
Checks verify output, not source spelling or conceptual mastery.
"""

from lessons.checks import check_output


CASES = {
    "a05_target": (("54",), "Проверь, какую часть выражения ты заключил в скобки. Нужен результат 54."),
    "a05_repair": (("135",), "Проверь обе пары скобок. Нужно сложить 13 и 2, затем умножить результат на 9."),
    "a05_dictionary": (("37",), "Программа запустилась, но количество дней пока не подходит. Учти уже накопленные деньги и ежедневную сумму."),
    "a05_ropes": (("1525",), "Программа запустилась, но длина пока не подходит. Проверь общую длину и разницу. В ответе нужна более длинная верёвка."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
