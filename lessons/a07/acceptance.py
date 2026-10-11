"""A7 contracts: reassignment, old-value updates, and preserving numeric values.

Prerequisites: A6 assignment/lookup and saved results; A3 order; A4/A5 integer
arithmetic and grouping. Replacement precedes output prediction. The
evaluate-right-then-store-left trace precedes balance updates; print versus
save precedes balance debugging. Saving a number under another name precedes
a second concrete code prediction and the independent swap challenge.
Six required activities: four console scripts and two predictions. No loops,
function definitions, tuple assignment, modulo, or abbreviated updates.

Challenge sources:
- Al Sweigart, Python Programming Exercises, Gently Explained, exercise 37,
  Change Maker: https://inventwithpython.com/pythongently/exercise37/
  Original: a function returns minimum counts of 25-, 10-, 5-, and 1-cent
  coins. Adaptation: unlimited 10-, 5-, and 1-ruble coins; initial amount 137;
  print three counts from an ordinary script. Students use known integer
  division, multiplication, subtraction, and saved intermediate values;
  no dictionary, function, modulo, or supplied greedy algorithm.
- Allen Downey, Think Python 2, section 12.2:
  https://greenteapress.com/thinkpython2/html/thinkpython2013.html
  Adapt the ordinary three-assignment swapping example into an independent
  problem with left=137 and right=284. Do not supply its assignments or
  introduce the later tuple shortcut. The earlier article explains saving
  a number, not the swap algorithm.

Editorial benchmarks for explanations, not copied prose:
https://allendowney.github.io/ThinkPython/chap02.html
https://inventwithpython.com/invent4thed/chapter1.html

Balance construction/debugging are original programming exercises, not
purported workbook problems. Output checks verify the stated default case,
not mastery, the algorithm, or arbitrary changed starting data. The child
must still use the requested calculations; review that during the pilot.
Private challenge references are also checked with varied starting values.
"""

from lessons.checks import check_output


CASES = {
    "a07_balance": (("136", "217", "119"), "Покажи количество монет до награды, после всей награды и после обеих покупок. При каждом изменении используй текущее значение coins."),
    "a07_balance_repair": (("55", "65"), "После траты количество должно измениться в coins. Находку прибавь уже к оставшемуся количеству, затем выведи его."),
    "a07_change": (("13", "1", "2"), "Собери ровно 137 рублей с наименьшим количеством монет. Покажи отдельно количества монет по 10, 5 и 1 рублю, в этом порядке."),
    "a07_swap": (("284", "137"), "Поменяй значения местами, не потеряв ни одного числа. Выведи сначала left, затем right."),
}


def check(task_id, snapshot, output):
    expected, failure = CASES[task_id]
    return check_output(output, expected, failure)
