import json, os, json, yaml, re
from PySide6.QtGui import QColor
from typing import overload


class Printer:
    def __init__(self, obj: str, input_str: str):
        if hasattr(AnvilData(), "debug"):
            a = AnvilData().debug
            self.debug_level = a["level"]
            self.class_color = a["class_color"]
            self.function_color = a["function_color"]
            self.changed_color = a["changed_color"]
            self.error_color = a["error_color"]
            self.ok_color = a["ok_color"]
            self.info_color = a["info_color"]
        else:
            self.debug_level = 1
            self.class_color = None
            self.function_color = None
            self.changed_color = None
            self.error_color = None
            self.ok_color = None
            self.info_color = None
        self.route = None
        self.vclass = None
        self.vfunc = None

        self.mute = False

        self.cli_color = {
            "red": "\033[91m{}\033[00m",
            "green": "\033[92m{}\033[00m",
            "yellow": "\033[93m{}\033[00m",
            "purple": "\033[95m{}\033[00m",
            "cyan": "\033[96m{}\033[00m",
            "gray": "\033[97m{}\033[00m",
            "black": "\033[98m{}\033[00m",
        }
        self.gui_color = {
            "red": QColor(192, 57, 43),
            "green": QColor(39, 174, 96),
            "yellow": QColor(241, 196, 15),
            "purple": QColor(155, 89, 182),
            "cyan": QColor(93, 173, 226),
            "gray": QColor(149, 165, 166),
            "black": QColor(23, 32, 42),
        }

        self.set(obj, input_str)

    def set(self, obj: str, input_str: str) -> None:

        if obj == "class":
            self.vclass = self._apply_color(input_str, self.class_color)
        else:
            func = self._apply_color(input_str, self.function_color)
            self.vfunc = f"{self.vclass}:{func}"
            # self._print(self.vfunc)

    def print(self, input_str: str, color: str = "gray") -> None:
        """
        self._print a string with a color.
        """
        string = self._apply_color(input_str, color)
        self._print(string)

    def created(self, input_str: str, modifier="CREATED:"):
        """
        self._print a changed
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.changed_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def inserted(self, input_str: str, modifier="INSERTED:"):
        """
        self._print a changed
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.changed_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def changed(self, input_str: str, modifier="CHANGED:"):
        """
        self._print a changed
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.changed_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def error(self, input_str: str, modifier="ERROR:") -> None:
        """
        self._print an error
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.error_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def ok(self, input_str: str, modifier="OK:") -> None:
        """
        self._print an ok
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.ok_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def info(self, input_str: str, modifier="INFO:") -> None:
        """
        self._print some info
        """
        string = self._apply_color(f"{modifier : <10}\t{input_str}", self.info_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def type(self, input_obj) -> None:
        """
        self._print a type
        """
        obj_type = type(input_obj).__name__
        string = self._apply_color(f"TYPE -> {obj_type}", self.info_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def cjson(self, input_obj) -> None:
        """
        self._print a json object
        """
        string = self._apply_color(json.dumps(input_obj, indent=4), self.info_color)
        self._print(f"{self.vfunc : <25}\t{string}")

    def _apply_color(self, input_str: str, color) -> str:
        if color is None:
            color = "gray"
        return self.cli_color[color].format(input_str)

    def _print(self, input_str: str) -> None:
        if not self.mute:
            print(input_str)


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

    def get_item(self, key) -> dict | str | int | None:
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return None
            return self._recursive_search(data, key)

    @staticmethod
    def get_all(item_path) -> dict | None:
        """Get all data from the yaml file."""
        if os.path.exists(item_path):
            with open(os.path.join(item_path), "r") as file:
                data = yaml.safe_load(file)
            return data
        else:
            return None

    def create_or_update_item(self, key, value) -> None:
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

    def align_dicts(self, target_dict, defaults_dict) -> tuple:
        ret_val = True
        # add missing keys
        for key, value in defaults_dict.items():
            if target_dict.get(key) is None:
                target_dict[key] = value
                ret_val = False
        # remove extra keys
        keys_to_remove = [key for key in target_dict if key not in defaults_dict]
        for key in keys_to_remove:
            del target_dict[key]
            ret_val = False

        return target_dict, ret_val

    def validate_yaml_file(self, defaults_dict: dict, create: bool = True) -> dict:
        """
        Validates a yaml file against a dictionary of defaults. \n
        - If file missing, optionally create it. \n
        - If missing keys, they will be added. \n
        - If extra keys, they will be removed. \n
        - If is empty, it will be populated with defaults. \n
        returns the validated data.
        """
        p = Printer("function", "validate_yaml_file()")
        p.type(defaults_dict)
        if not isinstance(defaults_dict, dict):
            raise ValueError("defaults must be a dictionary")

        FileManager(self.item_path).check_file(create=create)
        file_name = self.item_path.split("/")[-1]
        file_contents = self.get_all()
        if isinstance(file_contents, dict):
            data, ret_val = self.align_dicts(file_contents, defaults_dict)
            if not ret_val:
                self.save_all(data)
                p.changed(f"fixed {file_name}")
            else:
                p.ok(file_name)
        else:
            data = defaults_dict
            self.save_all(data)
            p.changed(f"create {file_name}")
        return data
