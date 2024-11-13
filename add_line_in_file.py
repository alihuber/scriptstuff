# the most primitive script that adds a given line of text into a file at given line num
# blatantly ignoring sed.. just use it in tests 🤪

from pathlib import Path
import os
import subprocess
import argparse
from tempfile import mkstemp
from shutil import move, copymode

parser = argparse.ArgumentParser()
parser.add_argument(
    "filename",
    help="files in which the string should be replaced",
)
parser.add_argument(
    "string_to_add",
    help="string to add",
)
parser.add_argument(
    "line_number",
    help="line number to add string (below)",
)
parser.add_argument(
    "--commit_message",
    help='commit message, between ""',
    action="store_true",
    default="",
)
parser.add_argument(
    "--dryrun",
    help="display changes only, do not alter files",
    action="store_true",
    default=False,
)
parser.add_argument(
    "--commit", help="do also a git commit on develop branch", action="store_true", default=False
)
parser.add_argument(
    "--push", help="do also a git push", action="store_true", default=False
)
args = parser.parse_args()

filename = args.filename
line_number = args.line_number
string_to_add = args.string_to_add
commit_message = args.commit_message
dry_run = args.dryrun
push = args.push
commit = args.commit

if commit and not commit_message:
    print("Can't commit without commit message, aborting..")
    exit(1)

found_files = Path(".").rglob(filename)
filepaths = [os.path.abspath(path) for path in found_files]
filtered_filepaths = [path for path in filepaths if "node_modules" not in path]

def lines_in_file(file_path):
    return [line for line in file_path]


def add_line(file_path, new_line, line_number):
    print(f"will add '{new_line}' after line {line_number} in file {str(file_path)} \n")
    if dry_run:
        return
    # Create temp file
    file_handle, abs_path = mkstemp()
    with os.fdopen(file_handle, "w") as new_file:
        with open(file_path) as old_file:
            file_lines = old_file.readlines()
            file_lines.insert(int(line_number)+1, f"{new_line}\n")
            for line in file_lines:
                new_file.write(line)
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    os.remove(file_path)
    # Move new file
    move(abs_path, file_path)

for file_path in filtered_filepaths:
    try:
      add_line(file_path, string_to_add, line_number)
    except Exception as e:
        print(f"error: could not alter file {file_path}")
        print(e)


commands = [
    ["git", "switch", "develop"],
    ["git", "pull"],
    ["npm", "install"],
    ["git", "add", "."],
    ["git", "commit", "-m", commit_message],
]

def exec_process(command, dirname):
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dirname
    ) as process:
        print(f"output {" ".join(command)}: {process.stdout.read1().decode('utf-8')}")


if not dry_run and commit and commit_message:
    for file_path in filtered_filepaths:
        dirname = os.path.dirname(file_path)
        for command in commands:
            exec_process(command, dirname)
        if push:
            try:
                command = ["git", "push"]
                exec_process(command, dirname)
            except Exception as e:
                print(f"error: could not git push for dir {dirname}")
                print(e)
