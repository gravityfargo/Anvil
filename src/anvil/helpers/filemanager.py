"""
This module contains functions for managing files and directories.
"""

import os
import subprocess
from .datautils import convert_bytes


def check_dir(dir_path: str = None, create: bool = False) -> bool:
    """
    Check/create a directory.
    """
    if not os.path.exists(dir_path):
        if create:
            create_dir(dir_path)
            return True
        else:
            return False
    return True


def check_file(file_path: str = None, create: bool = False) -> bool:
    """
    Check if a file exists. If it does not exist, create it or raise FileNotFoundError.

    return True if the file exists, False if it was created
    """
    if not os.path.exists(file_path):
        if create:
            create_file(file_path)
            return True
        else:
            return False
    return True


def create_file(file_path: str) -> None:
    try:
        with open(file_path, "w") as file:
            file.write("")
    except:
        raise FileNotFoundError(f"Error Creating {file_path}")


def create_dir(dir_path: str) -> None:
    """Create a directory."""
    try:
        os.makedirs(dir_path)
    except:
        raise FileNotFoundError(f"Error Creating {dir_path}")


def get_directories(dir_path: str) -> list:
    """Get a list of directories in a directory."""
    dirs = []
    for item in os.listdir(dir_path):
        if os.path.isdir(os.path.join(dir_path, item)):
            dirs.append(item)
    return dirs


def process_line(line: str):
    """Process a line from the tree command."""
    line_copy2 = line.rstrip().split(" ")

    if len(line_copy2) == 1:
        return
    if line_copy2[0].isdigit():
        print("Summary Line")
        return

    bytes_str = ""
    for i in line:
        if i == "[":
            continue
        if i.isdigit():
            bytes_str = bytes_str + i
            continue
        if i == "]":
            break

    dir_level = 0
    for i in line_copy2:
        if i != "":
            break
        dir_level += 1

    dir_level = dir_level // 4
    return [dir_level, int(bytes_str)]


def tree(directory: str) -> list[int]:
    """Run the tree command on a directory."""
    depth = 0
    size = 0

    with subprocess.Popen(
        ["tree", directory, "-s", "-F"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as p:
        for line in p.stdout:
            ret = process_line(line)

            if ret is not None:
                depth = ret[0]
                size += ret[1]

        p.stdout.close()
        print(f"Depth = {depth}")
        print(convert_bytes(size))

        p.wait()  # Wait for the process to finish
        if p.returncode != 0:
            error_output = p.stderr.read()
            print(f"Error: {error_output}", end="")
