from os import getenv, path

from anvil.helpers import filemanager

from .inventory import Inventory


class Project:
    def __init__(self, name: str):
        self.name = name
        self.root_dir = path.join(getenv("DATA_DIR", "/tmp/anvil/data"), name)
        self.size = 0
        self.dir_count = 0
        self.file_count = 0
        self.tree_file = path.join(self.root_dir, "tree.yaml")
        self.inventory_path = path.join(self.root_dir, "inventory/hosts")
        self.inventory = Inventory(self.inventory_path)

    def setup(self):
        dir_structure = [
            "env",
            "inventory",
            "inventory/group_vars",
            "inventory/host_vars",
            "project",
            "project/roles",
        ]

        files = [
            "env/envvars",
            "env/extravars",
            "env/passwords",
            "env/cmdline",
            "env/settings",
            "env/ssh_key",
            "inventory/hosts",
        ]
        for directory in dir_structure:
            d = path.join(self.root_dir, directory)
            filemanager.check_dir(d, create=True)

        for file in files:
            f = path.join(self.root_dir, file)
            filemanager.check_file(f, create=True)

        self.inventory.setup()
        self.inventory.update_config()
