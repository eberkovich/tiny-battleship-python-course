from lessons.checks import Outcome


def input_cases(task_id):
    return (("2", "5"), ("13", "7"))


def check_interaction(task_id, answers, segments):
    expected = ("start\n", f"receipt {answers[0]}\n", f"change {int(answers[0]) + int(answers[1])}\n")
    return Outcome(segments == expected, "Check chronological segments")
