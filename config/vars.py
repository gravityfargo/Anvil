import json

ANVIL_DATA_FILE = "config/anvil.yaml"
PLAYBOOKS = {
    "-rf": "fetch_file.yml",
    "-rs": "send_file.yml",
}


class AnvilData:
    def __init__(self):
        self.root_path = None
        self.anvil_data_file = ANVIL_DATA_FILE
        self.anvil_temp_dir = "/tmp/anvil"
        self.playbooks = PLAYBOOKS
        self.all_projects = None

        self.s_project = None
        self.s_group = None
        self.s_host = None

        self.sp_ansible_config_file_path = None
        self.sp_inventory_file_path = None
        self.sp_tree_file_path = None

        self.sp_project_dir = None
        self.sp_groups_list = None
        self.sp_groups = None
        self.sp_hosts = None
        self.sp_repo_url = None

    def export_project_dict(self):
        data = {
            "ansible_config_file_path": self.sp_ansible_config_file_path,
            "inventory_file_path": self.sp_inventory_file_path,
            "tree_file_path": self.sp_tree_file_path,
            "project_dir": self.sp_project_dir,
            "groups_list": self.sp_groups_list,
            "groups": self.sp_groups,
            "hosts": self.sp_hosts,
            "repo_url": self.sp_repo_url,
        }
        return data

    # def __str__(self):
    #     data = {
    #         "anvil_data_file": self.anvil_data_file,
    #         "all_projects": self.all_projects,
    #         "s_project": self.s_project,
    #         "s_host": self.s_host,
    #         "s_project_inventory_file": self.s_project_inventory_file,
    #         "sp_groups_list": self.sp_groups_list,
    #         "sp_groups": self.sp_groups,
    #         "sp_hosts": self.sp_hosts,
    #     }
    #     json_data = json.dumps(data, indent=4)
    #     return json_data
