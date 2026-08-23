from lessons.phase_a_checks import (
    ENEMY,
    cell,
    expect_output,
    expect_project_fleet,
    failed,
    passed,
)


FLEET = (
    (1, 1), (3, 1), (5, 1), (7, 1), (9, 1),
    (1, 3), (3, 3), (5, 3), (7, 3), (9, 3),
)
STAR_FLEET = ((1, 2), (3, 2), (5, 2), (7, 2), (9, 2))


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_06_exercise_01":
        return expect_output(output, "2\n4\n6\n8")
    if task_id == "lesson_06_exercise_03":
        return expect_output(output, "1\n3\n5")
    if task_id == "lesson_06_exercise_02":
        return expect_output(output, "2\n4\n5\n4\n8\n4")
    if task_id == "lesson_06_project":
        return expect_project_fleet(snapshot, FLEET, 10)
    if task_id == "lesson_06_star":
        fleet = expect_project_fleet(snapshot, STAR_FLEET, 5)
        if not fleet.passed:
            return fleet
        for x in range(1, 11):
            for y in range(1, 11):
                if cell(snapshot, ENEMY, x, y)[0] == "deck":
                    return failed("Поле противника должно остаться пустым.")
        return passed("Звёздочка твоя! Все ошибки найдены и исправлены.")
    return failed("Для этого задания пока нет проверки.")
