import json

ANVIL_DATA_FILE = "config/anvil.yaml"


class AnvilData:
    def __init__(self):
        self.anvil_data_file = ANVIL_DATA_FILE
        self.all_projects = None

        self.selected_project = None
        self.selected_host = None

        self.selected_project_inventory_file = None
        self.selected_project_groups_list = None
        self.selected_project_groups = None
        self.selected_project_hosts = None
        self.selected_project_url = None

    # def __str__(self):
    #     data = {
    #         "anvil_data_file": self.anvil_data_file,
    #         "all_projects": self.all_projects,
    #         "selected_project": self.selected_project,
    #         "selected_host": self.selected_host,
    #         "selected_project_inventory_file": self.selected_project_inventory_file,
    #         "selected_project_groups_list": self.selected_project_groups_list,
    #         "selected_project_groups": self.selected_project_groups,
    #         "selected_project_hosts": self.selected_project_hosts,
    #     }
    #     json_data = json.dumps(data, indent=4)
    #     return json_data
