from lessons.phase_a_checks import expect_output, expect_project_fleet, failed


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_02_exercise_01":
        return expect_output(output, "12")
    if task_id == "lesson_02_exercise_02":
        return expect_output(output, "5")
    if task_id == "lesson_02_exercise_03":
        return expect_output(output, "5")
    if task_id == "lesson_02_project":
        return expect_project_fleet(snapshot, ((2, 2),), 1)
    return failed("Для этого задания пока нет проверки.")
