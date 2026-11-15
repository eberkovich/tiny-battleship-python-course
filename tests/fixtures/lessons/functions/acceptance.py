import sys


class Outcome:
    def __init__(self, passed, message):
        self.passed = passed
        self.message = message


def check(task_id, snapshot, output):
    return Outcome(output == "7\n7\n", "Output checked.")


def check_program(task_id, source, namespace, calls):
    assert sys.getprofile() is None
    function = namespace.get("greet")
    if function is None or calls[function.__code__] != 2:
        return Outcome(False, "Call the function twice.")
    assert function.__code__.co_filename == str(source)
    # Extra checker/probe output must never replace or append to student output.
    function()
    print("private checker output")
    return Outcome(True, "Calls checked in the subprocess.")
