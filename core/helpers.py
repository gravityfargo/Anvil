# from config.vars import AnvilData, COMMANDS
import yaml, os, json
from PySide6.QtCore import QObject


class ConditionChecks:
    def __init__(self, ad):
        self.ad = ad

    def check_len(self, command: str, length: int, argument):
        if len(argument) < length:
            # msg = HelpMessage(command, "USEAGE")
            raise BreakException(f"failed check_len")

    def check_s_project(self):
        if self.ad.s_project["name"] is None:
            raise BreakException("ERROR:\t Select a Project First")

    def check_s_host(self):
        if self.ad.s_host["name"] is None:
            msg = "ERROR:\t Select a Host First"
            # raise BreakException(msg)
            raise BreakException(self.ad.__str__())


class BreakException(Exception):
    def __init__(self, msg=None):
        self.msg = msg
        super().__init__(msg)


class HelpMessage:
    def __init__(self, command="", purpose=""):
        self.command = command
        self.purpose = purpose
        root_cmd = command[:2]
        # if len(command) == 2:
        #     self.msg = COMMANDS[root_cmd]["USEAGE"]
        # elif len(command) > 2:
        #     self.msg = COMMANDS[root_cmd][command[2:]]["USEAGE"]

    def __str__(self):
        return self.msg


def print_attributes(obj):

    def convert(attr, value):
        if issubclass(type(value), QObject):
            return f"{value.__class__.__name__} -> {value.objectName()}"
        elif isinstance(value, list):
            print(f"{attr}:")
            for i in value:
                print(f"\t{convert(attr, i)}")
            return ""
        elif type(value) in [str, int, float, bool]:
            return value
        else:
            return type(value)

    if hasattr(obj, "__dict__"):
        for attr, value in vars(obj).items():
            i = convert(attr, value)
            if i:
                print(f"{attr}: {i}")
    else:
        print("Object has no attributes.")
