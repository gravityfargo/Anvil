#!/usr/bin/env python
import readline, importlib
import cli.parse_input as parse_input
import cli.file_utils as file_utils
from cli.file_utils import (
    cprint,
)
from os import path

from cli.parse_input import init_anvil


def main(ad):
    parser_module = parse_input
    parser_last_mod = path.getmtime("cli/parse_input.py")

    file_utils_module = file_utils
    file_utils_last_mod = path.getmtime("cli/file_utils.py")

    while True:
        try:
            print("\n")
            command = input("anvil> ")

            if not parser_module.user_input_parser(ad, command):
                break
            save_command_to_history(command)

            parser_current_mod = path.getmtime("cli/parse_input.py")
            file_utils_current_mod = path.getmtime("cli/file_utils.py")

            if parser_current_mod != parser_last_mod:
                importlib.reload(parser_module)
                parser_last_mod = parser_current_mod

            if file_utils_current_mod != file_utils_last_mod:
                importlib.reload(file_utils_module)
                file_utils_last_mod = file_utils_current_mod

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            print("\nExiting.")
            break


def save_command_to_history(command):
    readline.add_history(command)


if __name__ == "__main__":
    cprint("Anvil CLI", "purple")
    cprint("-------------------------------------------------", "purple")

    ad = init_anvil()
    cprint(f"Current Project: \t{ad.selected_project}", "purple")
    cprint(f"Current Host: \t\t{ad.selected_host}", "purple")
    main(ad)

else:

    def func():
        print("Func worked")
