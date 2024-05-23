# primitive script that recursively changes a line in all package.json files,
# beginning from current directory, ignoring all files in node_modules.
# will only replace the npm package version string to the new given version

from pathlib import Path
import os
import subprocess
import argparse
from tempfile import mkstemp
from shutil import move, copymode

parser = argparse.ArgumentParser()
parser.add_argument(
    "search_string",
    help="search string, npm package name",
)
parser.add_argument(
    "version_to_set",
    help="version to set the npm package to",
)
parser.add_argument(
    "commit_message",
    help='commit message, between ""',
)
parser.add_argument(
    "--dryrun",
    help="display changes only, do not alter files",
    action="store_true",
    default=False,
)
parser.add_argument(
    "--push", help="do also a git push", action="store_true", default=False
)
args = parser.parse_args()

search_string = args.search_string
version_to_set = args.version_to_set
commit_message = args.commit_message
dry_run = args.dryrun
push = args.push

filename = "package.json"

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


def change_package_json_line(version_to_set, file_path, old_line):
    split_line = old_line.split(" ")
    version_index = len(split_line) - 1
    version_string = split_line[version_index]
    has_comma = "," in version_string
    new_version_string_ary = [f'"{version_to_set}"']
    if has_comma:
        new_version_string_ary.append(",")
    new_version_string_ary.append("\n")
    new_version_string = "".join(new_version_string_ary)
    new_version_line_ary = split_line.copy()
    new_version_line_ary[version_index] = new_version_string
    new_line = " ".join(new_version_line_ary)
    try:
        replace(file_path, old_line, new_line)
    except:
        print(f"error: could not alter file {file_path}")


for file_path in filtered_filepaths:
    with open(file_path, "r") as fp:
        for old_line in lines_that_contain(f'"{search_string}":', fp):
            change_package_json_line(version_to_set, file_path, old_line)

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


if not dry_run:
    for file_path in filtered_filepaths:
        dirname = os.path.dirname(file_path)
        for command in commands:
            exec_process(command, dirname)
        if push:
            try:
                command = ["git", "push"]
                exec_process(command, dirname)
            except:
                print(f"error: could not git push for dir {dirname}")
