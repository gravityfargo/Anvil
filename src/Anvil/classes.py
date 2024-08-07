import json, os, json, yaml, re
from PySide6.QtGui import QColor
from typing import overload

CONFIG_TEMPLATE_FILE = "core/anvil_template.yaml"

COMMANDS = {
    "-s": {
        "DESC": "Select a Project, Group, and or Host for manipulation",
        "USEAGE": "-sp <project_name>\n -sh <host_name>\n -sg <group_name>",
        "p": {
            "DESC": "Select a Project",
            "USEAGE": "-sp <project_name>",
        },
        "h": {
            "DESC": "Select a Host",
            "USEAGE": "-sh <host_name>",
        },
        "g": {
            "DESC": "Select a Group",
            "USEAGE": "-sg <group_name>",
        },
    },
    "-d": {
        "DESC": "Delete a Host, Group, or Project",
        "USEAGE": "-dg <group_name>",
        "g": {
            "DESC": "Delete Group",
            "USEAGE": "-dg <group_name>",
        },
    },
    "-i": {
        "DESC": "Import a Project",
        "USEAGE": "-ip <project_name>",
        "p": {
            "DESC": "Import Project",
            "USEAGE": "-ip <project_name>",
        },
    },
    "-l": {
        "DESC": "List Projects, Groups, or Hosts",
        "USEAGE": "-lg  List Host Groups\n -lh List Hosts\n -lp  List Projects",
        "p": {
            "DESC": "List All Known Projects",
            "USEAGE": "-lp",
        },
        "g": {
            "DESC": "List host groups of the current project.",
            "USEAGE": "-lg",
        },
        "h": {
            "DESC": "List hosts of the current project.",
            "USEAGE": "-lh",
        },
    },
    "-u": {
        "DESC": "Update configureations based on the files present.",
        "USEAGE": "-u",
    },
    "-r": {
        "DESC": "Interact with a remote host",
        "USEAGE": "-r-fetch <target_file>\n -r-send <target_file>\n -r-service-r <service_name>\n -r-file-c",
        "-fetch": {
            "DESC": "Fetch a file from the selected host.",
            "USEAGE": "-r-fetch <target_file>",
        },
        "-send": {
            "DESC": "Send a file to the selected host.",
            "USEAGE": "-r-send <target_file>",
        },
        "-service-r": {
            "DESC": "Restart a Service",
            "USEAGE": "-r-service-r <service_name>",
        },
        "-file-create": {
            "DESC": "Create a file on the selected host",
            "USEAGE": "-r-file-create <target_file>",
        },
        "-file-copy": {
            "DESC": "Copy a file to the selected host",
            "USEAGE": "-r-file-copy <target_file>",
        },
    },
}


class AnvilData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnvilData, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def __str__(self):
        # json dump everything
        return json.dumps(self.__dict__, indent=4)

    def initialize(self):
        if not hasattr(self, "_initialized"):
            template = YamlManager(CONFIG_TEMPLATE_FILE).get_all()
            if template is None:
                raise FileNotFoundError(
                    f"Anvil Template File not found: {CONFIG_TEMPLATE_FILE}"
                )
            config = YamlManager(template["options"]["config_file"]).validate_yaml_file(
                template, True
            )
            FileManager(config["options"]["temp_dir"]).check_dir(create=True)

            pwd = os.getcwd()
            config["options"]["pwd"] = pwd

            config_path = os.path.join(pwd, template["options"]["config_file"])
            config["options"]["config_file"] = config_path

            YamlManager(config_path).create_or_update_item("options", config["options"])

            self.options: dict = config["options"]
            self.debug: dict = config["debug"]
            self.projects: dict = config["projects"]
            self.s_project: dict = config["s_project"]
            self.s_group: dict = config["s_group"]
            self.s_host: dict = config["s_host"]
            self._initialized = True

    def set_s_project(self, project_name: str):
        p = Printer("function", "set_s_project()")
        if project_name == self.s_project["name"]:
            p.ok("already set")
            return
        elif project_name not in list(self.projects.keys()):
            p.error("invalid")

        self.s_project["name"] = project_name

        self.set_s_group(None)
        p.changed(project_name)

    def set_s_group(self, group_name):
        p = Printer("function", "set_s_group()")
        s_group_data = {
            "name": None,
            "path": None,
            "hosts": None,
            "var_file_path": None,
        }
        if group_name == self.s_group["name"]:
            p.ok("already set")
            return

        if group_name not in self.s_project["groups_list"]:
            p.error("invalid")
            group_name = None
            self.set_s_host(None)

        elif group_name is None:
            p.changed("None")
            self.set_s_host(None)

        else:
            s_group_data["name"] = group_name
            s_group_data["path"] = self.s_project["groups"][group_name]["path"]
            s_group_data["var_file_path"] = self.s_project["groups"][group_name][
                "var_file_path"
            ]
            hosts = []
            for host in self.s_project["hosts"]:
                if self.s_project["hosts"][host]["group"] == group_name:
                    hosts.append(host)
            s_group_data["hosts"] = hosts

        self.s_group = s_group_data
        YamlManager(self.config_file).create_or_update_item("s_group", s_group_data)
        p.changed(group_name)

    def set_s_host(self, host_name: str | None) -> None:
        p = Printer("function", "set_s_host()")
        s_host_data = {
            "name": None,
            "path": None,
            "group": None,
            "var_file_path": None,
        }

        if host_name == self.s_host["name"]:
            p.ok("already set")
            return

        if self.s_project["hosts"].get(host_name) is None:
            p.error("invalid")
            host_name = None

        else:
            s_host_data["name"] = host_name
            s_host_data["path"] = self.s_project["hosts"][host_name]["path"]
            s_host_data["group"] = self.s_project["hosts"][host_name]["group"]
            self.set_s_group(s_host_data["group"])
            s_host_data["var_file_path"] = self.s_group["var_file_path"]

        self.s_host = s_host_data
        YamlManager(self.config_file).create_or_update_item("s_host", self.s_host)
        p.changed(host_name)

    def import_existing_project(self, ad, project_name: str, project_dir: str) -> bool:
        # pdebug("broken", "red")
        # new_project = ad.project_template.copy()

        # new_project["inventory_file"] = os.path.join(project_dir, "inventory.yml")
        # new_project["ansible_config_file"] = os.path.join(project_dir, "ansible.cfg")
        # new_project["tree_file"] = os.path.join(project_dir, "tree.yaml")
        # new_project["path"] = project_dir

        # if not os.path.exists(project_dir):
        #     pcolor("Project directory not found.", "red")
        #     return False
        # pcolor("Project directory found.", "green")

        # YamlManager(ad.anvil_config_file).create_or_update_item(
        #     "projects", {project_name: new_project}
        # )
        # pcolor("Import Successful.", "green")
        # return True
        pass

    def sync_project_with_file_system(
        self, config_file: str, s_project_dict: dict = None
    ) -> dict:
        p = Printer("function", "sync_project_with_file_system()")
        found_folders = []
        found_items = []
        git_config = os.path.join(s_project_dict["path"], ".git", "config")

        for proj_root_item in os.listdir(s_project_dict["path"]):
            if os.path.isdir(os.path.join(s_project_dict["path"], proj_root_item)):
                found_folders.append(proj_root_item)
            else:
                found_items.append(proj_root_item)

        # check for git
        FileManager(s_project_dict["path"]).check_dir(".git")
        FileManager(git_config).check_file()
        with open(git_config, "r") as file:
            content = file.read()
            url = re.search(r"url\s*=\s*(.*)", content)
            if url is not None:
                s_project_dict["repo_url"] = url.group(1)

        FileManager(s_project_dict["ansible_config_file"]).check_file()
        FileManager(s_project_dict["inventory_file"]).check_file()
        FileManager(s_project_dict["tree_file"]).check_file()

        s_project_dict = self.parse_inventory_file(s_project_dict)

        # make sure directories exist
        for group in s_project_dict["groups"]:
            gpath = s_project_dict["groups"][group]["path"]
            vpath = s_project_dict["groups"][group]["var_file_path"]
            FileManager(gpath).check_dir()
            FileManager(vpath).check_file()

        for host in s_project_dict["hosts_list"]:
            hpath = s_project_dict["hosts"][host]["path"]
            FileManager(hpath).check_dir()

        YamlManager(config_file).create_or_update_item("s_project", s_project_dict)
        p.ok("Success")

        self.sync_tree_with_file_system(s_project_dict)

    def sync_tree_with_file_system(self, project_dict: dict):
        p = Printer("function", "sync_tree_with_file_system()")
        tree_file = project_dict["tree_file"]
        current_tree = YamlManager(tree_file).get_all()
        tree = {}
        project_dir = project_dict["path"]

        def inventory_directory(directory):
            for item in os.listdir(directory):
                props = {"service": None, "commands": []}
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    inventory_directory(item_path)
                else:
                    key = item_path.replace(project_dir, "")[1:]
                    if current_tree.get(key) is not None:
                        if current_tree[key] != props:
                            props = current_tree[key]
                    if key.endswith("_vars.yaml"):
                        continue
                    tree[key] = props

        for group in project_dict["groups_list"]:
            group_path = os.path.join(project_dir, group)
            if os.path.isdir(group_path):
                inventory_directory(group_path)

        YamlManager(tree_file).save_all(tree)
        p.ok("Success")

    def parse_inventory_file(self, s_project_dict: dict) -> dict:
        s_project = {
            "allgroups_content": {},
            "all_pass": False,
            "groups": {},
            "groups_list": [],
            "hosts": {},
            "hosts_list": [],
        }

        inv_file_contents = YamlManager(s_project_dict["inventory_file"]).get_all()

        def process_content(inv_file_contents):
            nonlocal s_project

            for group, value in inv_file_contents.items():
                group_data = {
                    "hosts": [],
                    "var_file_path": None,
                    "path": None,
                }
                if group == "all" and not s_project["all_pass"]:
                    s_project["all_groups_content"] = inv_file_contents["all"]["vars"][
                        "anvil_all_groups"
                    ]
                    s_project["all_pass"] = True
                    process_content(s_project["all_groups_content"])
                    continue

                group_data["path"] = os.path.join(s_project_dict["path"], group)
                if group.startswith("all"):
                    group_data.pop("hosts")
                    vars_dict = s_project["all_groups_content"][group].get("vars")
                else:
                    vars_dict = inv_file_contents[group].get("vars")
                    for host in inv_file_contents[group]["hosts"].keys():
                        host_data = {
                            "group": None,
                            "path": None,
                        }
                        group_data["hosts"].append(host)
                        host_data["path"] = os.path.join(
                            s_project_dict["path"], group, host
                        )
                        host_data["group"] = group

                        s_project["hosts"][host] = host_data
                        s_project["hosts_list"].append(host)

                if vars_dict is not None:
                    group_data["var_file_path"] = vars_dict["anvil_variable_file"]

                if group_data["var_file_path"] is not None:
                    group_data["var_file_path"] = os.path.join(
                        s_project_dict["path"], group, group_data["var_file_path"]
                    )

                s_project["groups_list"].append(group)
                s_project["groups"][group] = group_data

        process_content(inv_file_contents)

        s_project_dict["groups"] = s_project["groups"]
        s_project_dict["groups_list"] = s_project["groups_list"]
        s_project_dict["hosts"] = s_project["hosts"]
        s_project_dict["hosts_list"] = s_project["hosts_list"]

        return s_project_dict


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


class FileManager:
    def __init__(self, base_path: str):
        """
        Initialize the FileManager with the base path to build upon,
        or the complete path.
        """
        self.p = Printer("class", "FileManager:")
        self.base_path = base_path

    def check_dir(self, dir_name: str = None, create: bool = False) -> None:
        """
        Check if a directory exists. If it does not exist, create it or raise FileNotFoundError.
        """
        self.p.set("function", "check_dir()")
        dir_path = self.base_path
        if dir_name is not None:
            dir_path = os.path.join(self.base_path, dir_name)

        if not os.path.exists(dir_path):
            if create:
                self._create_dir(dir_path)
                self.p.changed(dir_path)
            else:
                raise FileNotFoundError(f"Directory not found: {dir_path}")
        else:
            self.p.ok(dir_path)

    def check_file(self, file_name: str = None, create: bool = False) -> None:
        """
        Check if a file exists. If it does not exist, create it or raise FileNotFoundError.
        """
        self.p.set("function", "check_file()")
        file_path = self.base_path
        if file_name is not None:
            file_path = os.path.join(self.base_path, file_name)

        if not os.path.exists(file_path):
            if create:
                self._create_file(file_path)
                self.p.changed(file_path)
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        else:
            self.p.ok(file_path)

    def _create_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w") as file:
                file.write("")
        except:
            raise FileNotFoundError(f"Error Creating {file_path}")

    def _create_dir(self, dir_path: str) -> None:
        try:
            os.makedirs(dir_path)
        except:
            raise FileNotFoundError(f"Error Creating {dir_path}")


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

    def get_all(self) -> dict | None:
        try:
            with open(os.path.join(self.item_path), "r") as file:
                data = yaml.safe_load(file)
            return data
        except:
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
