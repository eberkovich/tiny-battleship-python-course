"""A6 contracts: assign, read, distinguish quoted text, and reuse values.

Prerequisites: A1 comments, A2 calls/text/numbers, A3 execution order,
A4 arithmetic and A5 grouping. Creation and lookup precede coins; spelling
and case precede repair; lookup in arithmetic and saving a computed result
precede prediction, packing, card sharing, and optional pair weighing.
The opening compares repeated input literals with one saved ticket price;
the computed-result example retains a child count for another calculation.
Card sharing reuses the transfer for both final counts. Pair weighing retains
the combined weight for three further calculations; neither task gives the
child its calculation strategy.

Editorial checks: Think Python, chapter 2, assignment/state diagrams;
Invent Your Own Computer Games with Python, chapter 1, storing values:
https://allendowney.github.io/ThinkPython/chap02.html
https://inventwithpython.com/invent4thed/chapter1.html
Briggs' publisher overview/contents support the child-facing, terminology-first
approach; its public sample is chapter 8, not the variables chapter. Do not claim
the unavailable chapter was consulted:
https://nostarch.com/python-kids-2nd-edition

Card-sharing source: New Syllabus Mathematics Strategies Primary 3, Yee Fook
Shiong, Educational Publishing House, 2007. Problem verified in Cassy Turner's
June 14, 2017 "Word Problem Wednesday - Gavin and Howie" post, which names the
book; no page or exercise number is supplied:
https://singaporemathsource.com/blog/page/8/
Original data preserved: Gavin has 356 cards, 286 more than Howie; find the
transfer making the counts equal. Our extension also prints both final counts,
so the retained transfer is useful twice. Russian wording is a paraphrase.

Optional weighing source: University of Regina's Math Central, September 2015,
"Three chickens weighed in pairs":
https://mathcentral.uregina.ca/QQ/database/QQ.09.15/h/shelly1.html
The original asks for combined weight from pair weights 10.6, 8.5, 6.1 kg.
Our adaptation expresses the same measurements as whole grams (10600, 8500,
6100), avoiding untaught decimals, and also asks for individual weights.
The source's solution discusses both combined and individual weights; no
unverified workbook attribution is made. Hints reveal the double-count insight
progressively. Packing is original programming practice, not a sourced puzzle.

Checks verify output; using variable names and explaining lookup are reviewed
in the child pilot, not enforced by brittle source-pattern assertions.
"""

from lessons.checks import check_output


CASES = {
    "a06_coins": (("136", "coins"), "Проверь порядок: сначала количество монет, затем слово coins. Различай имя без кавычек и текст в кавычках."),
    "a06_repair": (("18",), "Проверь написание имени в print: оно должно совпадать с именем слева от =."),
    "a06_packs": (("59", "23"), "Проверь количество полных наборов и оставшихся наклеек. Нужны два числа, именно в этом порядке."),
    "a06_cards": (("143", "213", "213"), "Проверь передачу: у Гэвина карточек становится меньше, у Хоуи — больше. В конце у них должно быть поровну, а общее количество не меняется."),
    "a06_weights": (("12600", "6500", "4100", "2000"), "Проверь общий вес и веса по отдельности: каждая указанная пара должна дать своё показание весов. Выведи общий вес, затем вес первой, второй и третьей курицы."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
