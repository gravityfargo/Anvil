# from config.vars import AnvilData, COMMANDS
import yaml, os, json


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


def pcolor(input_data, color="gray", emitter=None):
    """print colored text to stdout

    ([[input_str, color], [input_str, color]], None, None)
    (input_str, color, None)

    input_str (str): string to be printed
    color (str): color to be used

    red, green, yellow, purple, cyan, gray, black
    """

    def color_it(input_str: str, color: str):
        string = ""
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
        return string

    if emitter is None:
        if isinstance(input_data, str):
            string = color_it(input_data, color)
            print(string)

        elif isinstance(input_data, list):
            if isinstance(input_data[0], list):
                strings = []
                for i in input_data:
                    strings.append(f"{color_it(i[0], i[1])}")
                print(strings[0], strings[1])
            elif isinstance(input_data[0], str):
                if isinstance(input_data[1], list):
                    string1 = color_it(input_data[0], "purple")
                    string2 = color_it(input_data[1][0], input_data[1][1])
                    print(string1, string2)
                else:
                    string = color_it(input_data[0], input_data[1])
                    print(string)

    else:
        emitter.emit((input_data, color))


def pdebug(input_data, color="gray"):
    """Print white debugging text to stdout
    This makes removing random print statements easier after debugging.
    """
    # debug_level = YamlManager(AnvilData().anvil_config_file).get_item("debug_level")
    # if debug_level == 1:
    pcolor(input_data, color)


def pjson(data, color="gray"):
    pdebug(json.dumps(data, indent=4))


class FileManager:
    def __init__(self, item_path: str):
        self.item_path = item_path

    def check_dir(self, dir_name: str = None):
        parts = self.item_path.split("/")
        if dir_name is not None:
            self.item_path = os.path.join(self.item_path, dir_name)

        try:
            os.makedirs(self.item_path)
            pdebug(["FileManager.check_dir:", [f"created {self.item_path}", "yellow"]])
        except:
            pdebug(["FileManager.check_dir:", [f"exists {self.item_path}", "green"]])

    def check_file(self, file_name: str = None):

        if file_name is not None:
            self.item_path = os.path.join(self.item_path, file_name)

        if not os.path.exists(self.item_path):
            with open(self.item_path, "w") as file:
                file.write("")
            pdebug(["FileManager.check_file:", [f"created {self.item_path}", "yellow"]])
        else:
            pdebug(["FileManager.check_file:", [f"exists {self.item_path}", "green"]])


class YamlManager:
    def __init__(self, item_path: str):
        """Initialize the YamlManager with the path to the yaml file."""
        self.item_path = item_path

    def _recursive_search(self, data, key):
        """Recursively search for a key in a nested dictionary."""
        if isinstance(data, dict):
            if key in data:
                return data[key]
            for sub_key, sub_value in data.items():
                result = self._recursive_search(sub_value, key)
                if result is not None:
                    return result
        return None

    def get_item(self, key):
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return None
            return self._recursive_search(data, key)

    def get_all(self):
        with open(os.path.join(self.item_path), "r") as file:
            data = yaml.safe_load(file)
        return data

    def create_or_update_item(self, key, value):
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file) or {}

        if key in data and isinstance(data[key], dict) and isinstance(value, dict):
            data[key].update(value)
        else:
            data[key] = value

        with open(self.item_path, "w") as file:
            yaml.safe_dump(data, file)

    def _recursive_delete(self, data, key):
        """Recursively delete a key in a nested dictionary."""
        if isinstance(data, dict):
            if key in data:
                del data[key]
                return True
            for sub_key, sub_value in data.items():
                if self._recursive_delete(sub_value, key):
                    if isinstance(sub_value, dict) and not sub_value:
                        del data[sub_key]
                    return True
        return False

    def delete_item(self, key):
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return False

        if self._recursive_delete(data, key):
            with open(self.item_path, "w") as file:
                yaml.safe_dump(data, file)
            return True
        return False

    def save_all(self, data: dict):
        """Save all data to the yaml file."""
        with open(self.item_path, "w") as file:
            yaml.safe_dump(data, file)
