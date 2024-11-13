# even more primitive script that changes a given line of text in a given file name
# could be a awk script, but meh

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
    "search_string",
    help="search string, string to replace",
)
parser.add_argument(
    "replacement_string",
    help="replacement string",
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

search_string = args.search_string
replacement_string = args.replacement_string
filename = args.filename
commit_message = args.commit_message
dry_run = args.dryrun
push = args.push
commit = args.commit


found_files = Path(".").rglob(filename)
filepaths = [os.path.abspath(path) for path in found_files]
filtered_filepaths = [path for path in filepaths if "node_modules" not in path]

def lines_that_contain(string, file_path):
    return [line for line in file_path if string in line]


def replace(file_path, pattern, replacement):
    print(f"will replace {pattern} with {replacement} in file {str(file_path)} \n")
    if dry_run:
        return
    # Create temp file
    file_handle, abs_path = mkstemp()
    with os.fdopen(file_handle, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, replacement))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    os.remove(file_path)
    # Move new file
    move(abs_path, file_path)

def change_file_line(replacement_string, file_path, old_line):
    try:
        replace(file_path, old_line, f"{replacement_string}\n")
    except exception as e:
        print(f"error: could not alter file {file_path}")
        print(e)


for file_path in filtered_filepaths:
    with open(file_path, "r") as fp:
        for old_line in lines_that_contain(search_string, fp):
            change_file_line(replacement_string, file_path, old_line)


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
