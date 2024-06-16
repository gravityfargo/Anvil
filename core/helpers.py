from config.vars import AnvilData, COMMANDS


class ConditionChecks:
    def __init__(self, ad: AnvilData):
        self.ad = ad

    def check_len(self, command: str, length: int, argument):
        if len(argument) < length:
            msg = HelpMessage(command, "USEAGE")
            raise BreakException(msg)

    def check_s_project(self):
        if self.ad.s_project is None:
            raise BreakException("ERROR:\t Select a Project First")

    def check_s_host(self):
        if self.ad.s_host is None:
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
        if len(command) == 2:
            self.msg = COMMANDS[root_cmd]["USEAGE"]
        elif len(command) > 2:
            self.msg = COMMANDS[root_cmd][command[2:]]["USEAGE"]

    def __str__(self):
        return self.msg


def pcolor(input_str: str, color: str, emitter=None):
    """print colored text to stdout

    input_str (str): string to be printed
    color (str): color to be used

    red, green, yellow, purple, cyan, gray, black
    """

    string = ""
    if emitter is None:
        match color:
            case "red":
                string = "\033[91m {}\033[00m".format(input_str)
            case "green":
                string = "\033[92m {}\033[00m".format(input_str)
            case "yellow":
                string = "\033[93m {}\033[00m".format(input_str)
            case "purple":
                string = "\033[95m {}\033[00m".format(input_str)
            case "cyan":
                string = "\033[96m {}\033[00m".format(input_str)
            case "gray":
                string = "\033[97m {}\033[00m".format(input_str)
            case "black":
                string = "\033[98m {}\033[00m".format(input_str)
        print(string)
    else:
        emitter.emit((input_str, color))


def pdebug(inputstr: str):
    """Print white debugging text to stdout
    This makes removing random print statements easier after debugging.
    """
    pcolor(inputstr, "gray")
