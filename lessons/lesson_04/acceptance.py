from lessons.phase_a_checks import (
    PLAYER,
    expect_decks,
    expect_output,
    expect_project_fleet,
    failed,
    passed,
)


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_04_exercise_01":
        return expect_output(output, "[4, 7, 9, 12]")
    if task_id == "lesson_04_exercise_length":
        return expect_output(output, "4")
    if task_id == "lesson_04_exercise_02":
        return expect_output(output, "9")
    if task_id == "lesson_04_exercise_03":
        failure = expect_decks(snapshot, PLAYER, ((2, 4), (8, 4)))
        return failure or passed("Верно! Первый и последний корабли найдены.")
    if task_id == "lesson_04_project":
        return expect_project_fleet(snapshot, ((1, 1), (3, 1), (5, 1)), 3)
    return failed("Для этого задания пока нет проверки.")
