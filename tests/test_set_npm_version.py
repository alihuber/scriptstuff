import subprocess


def exec_process(command):
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as process:
        print(f"output {" ".join(command)}: {process.stdout.read1().decode('utf-8')}")


def test_set_no_comma():
    with open("./tests/fixtures/project1/package.json", "r") as myfile:
        assert '"winston": "^3.12.0"' in myfile.read()
    with open("./tests/fixtures/project2/package.json", "r") as myfile:
        assert '"winston": "^3.12.0"' in myfile.read()

    commands = [
        ["python3", "set_npm_version.py", "winston", "^3.17.0"],
    ]

    for command in commands:
        exec_process(command)

    with open("./tests/fixtures/project1/package.json", "r") as myfile:
        assert '"winston": "^3.17.0"' in myfile.read()
    with open("./tests/fixtures/project2/package.json", "r") as myfile:
        assert '"winston": "^3.17.0"' in myfile.read()

    cleanup_commands = [
        ["rm", "-rf", "./tests/fixtures/project1/node_modules"],
        ["rm", "-rf", "./tests/fixtures/project2/node_modules"],
        ["rm", "./tests/fixtures/project1/package-lock.json"],
        ["rm", "./tests/fixtures/project2/package-lock.json"],
        ["python3", "set_npm_version.py", "winston", "^3.12.0"],
    ]

    for command in cleanup_commands:
        exec_process(command)


def test_set_version():
    with open("./tests/fixtures/project1/package.json", "r") as myfile:
        assert '"express": "^4.18.3"' in myfile.read()
    with open("./tests/fixtures/project2/package.json", "r") as myfile:
        assert '"express": "^4.18.3"' in myfile.read()

    commands = [
        ["python3", "set_npm_version.py", "express", "4.21.1"],
    ]

    for command in commands:
        exec_process(command)

    with open("./tests/fixtures/project1/package.json", "r") as myfile:
        assert '"express": "4.21.1"' in myfile.read()
    with open("./tests/fixtures/project2/package.json", "r") as myfile:
        assert '"express": "4.21.1"' in myfile.read()

    cleanup_commands = [
        ["rm", "-rf", "./tests/fixtures/project1/node_modules"],
        ["rm", "-rf", "./tests/fixtures/project2/node_modules"],
        ["rm", "./tests/fixtures/project1/package-lock.json"],
        ["rm", "./tests/fixtures/project2/package-lock.json"],
        ["python3", "set_npm_version.py", "express", "^4.18.3"],
    ]

    for command in cleanup_commands:
        exec_process(command)
