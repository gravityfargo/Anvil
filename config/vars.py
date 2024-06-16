import json

ANVIL_DATA_FILE = "config/anvil.yaml"
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
    "-c": {
        "DESC": "Create",
        "USEAGE": "-cp <project_name>",
        "p": {
            "DESC": "Create a new project",
            "USEAGE": "-cp <project_name>",
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
    def __init__(self):
        self.root_path = None
        self.anvil_data_file = ANVIL_DATA_FILE
        self.anvil_temp_dir = "/tmp/anvil"
        self.all_projects = None

        self.s_project = None
        self.s_group = None
        self.s_host = None

        self.sp_ansible_config_file_path = None
        self.sp_inventory_file_path = None
        self.sp_tree_file_path = None
        self.sp_variables_file_path = None
        self.sp_playbooks_directory = None

        self.sp_project_dir = None
        self.sp_groups_list = None
        self.sp_groups = None
        self.sp_hosts = None
        self.sp_repo_url = None

        self.sh_path = None
        self.sh_group = None

        self.sg_path = None
        self.sq_hosts = None

    def export_project_dict(self):
        data = {
            "ansible_config_file_path": self.sp_ansible_config_file_path,
            "playbooks_directory": self.sp_playbooks_directory,
            "variables_file_path": self.sp_variables_file_path,
            "inventory_file_path": self.sp_inventory_file_path,
            "tree_file_path": self.sp_tree_file_path,
            "project_dir": self.sp_project_dir,
            "groups_list": self.sp_groups_list,
            "groups": self.sp_groups,
            "hosts": self.sp_hosts,
            "repo_url": self.sp_repo_url,
        }
        return data

    def __str__(self):
        # json dump everything
        return json.dumps(self.__dict__, indent=4)
