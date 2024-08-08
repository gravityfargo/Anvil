from anvil.config.config_options import AnvilOptions, Data


class Project(Data):
    variables = ["name", "dir", "tree_file"]
    name = ""
    directory = ""
    tree_file = ""
    inventory_file = ""
    ansible_config_file = ""
