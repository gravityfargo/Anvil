#!/usr/bin/env python
import readline
from cli.parse_input import user_input_parser, cprint

from cli.file_utils import init_anvil
from config.vars import AnvilData
from os import path
from main import gui_main


def main(ad: AnvilData):
    while True:
        try:
            command = input("anvil> ")

            if not user_input_parser(ad, command):
                break
            save_command_to_history(command)

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            print("\nExiting.")
            break


def save_command_to_history(command):
    readline.add_history(command)


if __name__ == "__main__":
    # cprint("Anvil CLI", "purple")
    # cprint("-------------------------------------------------", "purple")
    ad = AnvilData()
    ad = init_anvil(ad)

    if ad.s_project is not None:
        cprint(f"Current Project: \t{ad.s_project}", "purple")
        cprint(f"Current Host: \t\t{ad.s_host}", "purple")
    gui_main(ad)
    # main(ad)

else:

    def func():
        print("Func worked")
