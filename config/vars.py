import json, os
from core.helpers import YamlManager, FileManager, pcolor, pdebug, pjson, BreakException
from core.file_utils import (
    validate_yaml_file,
    sync_project_with_file_system,
    import_existing_project,
    sync_project_with_file_system,
)


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
        "USEAGE": "-lg\t List Host Groups\n -lh List Hosts\n -lp\t List Projects",
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
            pdebug("initialize()", "purple")
            anvil_template_data = YamlManager("config/anvil_template.yaml").get_all()
            FileManager(anvil_template_data["temp_dir"]).check_dir()
            FileManager(anvil_template_data["config_file"]).check_file()
            anvil_data = YamlManager("config/anvil.yaml").get_all()
            if not validate_yaml_file(anvil_data["config_file"], anvil_template_data):
                anvil_data = YamlManager("config/anvil.yaml").get_all()

            anvil_data["pwd"] = os.getcwd()
            anvil_data["config_file"] = os.path.join(
                anvil_data["pwd"], anvil_template_data["config_file"]
            )
            YamlManager(anvil_data["config_file"]).create_or_update_item(
                "pwd", anvil_data["pwd"]
            )
            YamlManager(anvil_data["config_file"]).create_or_update_item(
                "config_file", anvil_data["config_file"]
            )

            setattr(self, "config_file", anvil_data["config_file"])
            setattr(self, "pwd", anvil_data["pwd"])
            setattr(self, "debug_level", anvil_data["debug_level"])
            setattr(self, "temp_dir", anvil_data["temp_dir"])

            if anvil_data["projects"] is None:
                pdebug("No projects found.", "red")
            else:
                setattr(self, "projects", anvil_data["projects"])
                setattr(self, "s_project", anvil_data["s_project"])
                setattr(self, "s_group", anvil_data["s_group"])
                setattr(self, "s_host", anvil_data["s_host"])
                setattr(self, "debug_level", anvil_data["debug_level"])

            sync_project_with_file_system(self.config_file, self.s_project)
            self._initialized = True

    def set_s_project(self, project_name: str):
        if project_name == self.s_project["name"]:
            pcolor(["set_s_project:", ["already set", "green"]])
            return
        elif project_name not in list(self.projects.keys()):
            pcolor(["set_s_project:", ["invalid", "red"]])

        self.s_project["name"] = project_name

        self.set_s_group(None)
        pcolor("set_s_project:", [project_name, "yellow"])

    def set_s_group(self, group_name):
        s_group_data = {
            "name": None,
            "path": None,
            "hosts": None,
            "var_file_path": None,
        }
        if group_name == self.s_group["name"]:
            pcolor(["set_s_group:", ["already set", "green"]])
            return

        if group_name not in self.s_project["groups_list"]:
            pcolor(["set_s_group:", ["invalid", "red"]])
            group_name = None
            self.set_s_host(None)

        elif group_name is None:
            pcolor(["set_s_group:", [group_name, "yellow"]])
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

        pcolor(["set_s_group:", [group_name, "yellow"]])
        self.s_group = s_group_data
        YamlManager(self.config_file).create_or_update_item("s_group", s_group_data)

    def set_s_host(self, host_name: str | None) -> None:
        s_host_data = {
            "name": None,
            "path": None,
            "group": None,
            "var_file_path": None,
        }

        if host_name == self.s_host["name"]:
            pcolor(["set_s_host:", ["already set", "green"]])
            return

        if self.s_project["hosts"].get(host_name) is None:
            pcolor(["set_s_host:", ["invalid", "red"]])
            host_name = None

        else:
            s_host_data["name"] = host_name
            s_host_data["path"] = self.s_project["hosts"][host_name]["path"]
            s_host_data["group"] = self.s_project["hosts"][host_name]["group"]
            self.set_s_group(s_host_data["group"])
            s_host_data["var_file_path"] = self.s_group["var_file_path"]

        pcolor(["set_s_host:", [host_name, "yellow"]])
        self.s_host = s_host_data
        YamlManager(self.config_file).create_or_update_item("s_host", self.s_host)
