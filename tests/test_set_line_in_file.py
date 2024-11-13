import subprocess

def exec_process(command):
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as process:
        print(f"output {" ".join(command)}: {process.stdout.read1().decode('utf-8')}")

def test_replace_line_in_file():
    with open("./tests/fixtures/project1/Dockerfile", "r") as myfile:
        assert 'FROM node:10-alpine' in myfile.read()
    with open("./tests/fixtures/project2/Dockerfile", "r") as myfile:
        assert 'FROM node:10-alpine' in myfile.read()

    commands = [
        ["python3", "replace_line_in_file.py", "Dockerfile", "FROM node:10-alpine", "FROM node:22-alpine"],
    ]

    for command in commands:
        exec_process(command)

    with open("./tests/fixtures/project1/Dockerfile", "r") as myfile:
        assert 'FROM node:22-alpine' in myfile.read()
    with open("./tests/fixtures/project2/Dockerfile", "r") as myfile:
        assert 'FROM node:22-alpine' in myfile.read()

    cleanup_commands = [
        ["python3", "replace_line_in_file.py", "Dockerfile", "FROM node:22-alpine", "FROM node:10-alpine"],
    ]

    for command in cleanup_commands:
        exec_process(command)
