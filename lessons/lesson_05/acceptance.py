from lessons.phase_a_checks import expect_output, expect_project_fleet, failed


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_05_exercise_01":
        return expect_output(output, "[2, 5]\n2")
    if task_id == "lesson_05_exercise_02":
        return expect_output(output, "3")
    if task_id == "lesson_05_exercise_03":
        return expect_output(output, "[(1, 1), (4, 1), (7, 1)]")
    if task_id == "lesson_05_project":
        return expect_project_fleet(
            snapshot, ((1, 1), (3, 1), (5, 1), (7, 1)), 4
        )
    return failed("Для этого задания пока нет проверки.")
