from lessons.phase_a_checks import expect_output, expect_project_fleet, failed


def check(task_id: str, snapshot: dict[str, object], output: str):
    if task_id == "lesson_03_exercise_01":
        return expect_output(output, "(4, 7)")
    if task_id == "lesson_03_exercise_02":
        return expect_output(output, "8\n3")
    if task_id == "lesson_03_exercise_03":
        return expect_output(output, "9\n2")
    if task_id == "lesson_03_project":
        return expect_project_fleet(snapshot, ((2, 2), (5, 2)), 2)
    return failed("Для этого задания пока нет проверки.")
