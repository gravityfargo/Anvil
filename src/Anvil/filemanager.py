"""
This module contains functions for managing files and directories.
"""

import os


def check_dir(dir_path: str = None, create: bool = False) -> None:
    """
    Check if a directory exists. If it does not exist, create it or raise FileNotFoundError.
    """
    if not os.path.exists(dir_path):
        if create:
            create_dir(dir_path)
        else:
            raise FileNotFoundError(f"Directory not found: {dir_path}")


def check_file(file_path: str = None, create: bool = False) -> bool:
    """
    Check if a file exists. If it does not exist, create it or raise FileNotFoundError.

    return True if the file exists, False if it was created
    """
    if not os.path.exists(file_path):
        if create:
            create_file(file_path)
            return False
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
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
