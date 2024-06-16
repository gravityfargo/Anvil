#!/usr/bin/env python
import readline, sys
from core.parse_input import user_input_parser
from core.file_utils import init_anvil
from core.helpers import pcolor, pdebug
from config.vars import AnvilData
from os import path
from main import gui_main


def main(ad: AnvilData, passed_args: list):
    if len(passed_args) > 1:
        pure_args = passed_args[1:]
        num_pure_args = len(pure_args)
        i = 0
        while True:
            if pure_args[0] == "-h" or pure_args[0] == "--help":
                print(pcolor("Future Help Text", "cyan"))
                quit()
            elif pure_args[0] == "cli":
                break
            if num_pure_args % 2 == 0 and num_pure_args > 0:
                command = [pure_args[i], pure_args[i + 1]]
                user_input_parser(ad, command)
            elif num_pure_args % 2 != 0 and num_pure_args > 0:
                print(pure_args[i])
                user_input_parser(ad, [pure_args[i]])
                quit()
            else:
                quit()
            i += 2
            num_pure_args -= 2

    pcolor("Anvil CLI", "purple")
    pcolor("-------------------------------------------------", "purple")
    if ad.s_project is not None:
        pcolor(f"Current Project: \t{ad.s_project}", "purple")
        pcolor(f"Current Host: \t\t{ad.s_host}", "purple")

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
    ad = AnvilData()
    ad = init_anvil(ad)

    if len(sys.argv) > 1:
        main(ad, sys.argv)
    else:
        gui_main(ad)
