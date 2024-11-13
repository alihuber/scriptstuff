import subprocess

def exec_process(command):
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as process:
        print(f"output {" ".join(command)}: {process.stdout.read1().decode('utf-8')}")

def test_add_line_in_file():
    with open("./tests/fixtures/project1/testfile.js", "r") as myfile:
        assert 'bar' not in myfile.read()
    with open("./tests/fixtures/project2/testfile.js", "r") as myfile:
        assert 'bar' not in myfile.read()

    commands = [
        ["python3", "add_line_in_file.py", "testfile.js", "bar,", "5"],
    ]

    for command in commands:
        exec_process(command)

    with open("./tests/fixtures/project1/testfile.js", "r") as myfile:
        assert 'bar,' in myfile.read()
    with open("./tests/fixtures/project2/testfile.js", "r") as myfile:
        assert 'bar,' in myfile.read()

    cleanup_commands = [
        ["sed", "-i", "", '/bar,/d', "./tests/fixtures/project1/testfile.js"],
        ["sed", "-i", "", '/bar,/d', "./tests/fixtures/project2/testfile.js"]
    ]

    for command in cleanup_commands:
        exec_process(command)
