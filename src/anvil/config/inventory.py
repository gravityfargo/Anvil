import os
from typing import Any, Dict, List

from anvil.helpers import datautils, filemanager, yamlmanager


class Inventory:
    VARS = {
        "ansible_connection": "",
        "ansible_host": "",
        "ansible_port": "",
        "ansible_user": "",
        "ansible_password": "",
        "ansible_ssh_private_key_file": "",
        "ansible_ssh_common_args": "",
        "ansible_sftp_extra_args": "",
        "ansible_scp_extra_args": "",
        "ansible_ssh_extra_args": "",
        "ansible_ssh_pipelining": "",
        "ansible_ssh_executable": "",
        "ansible_become": "",
        "ansible_become_method": "",
        "ansible_become_user": "",
        "ansible_become_password": "",
        "ansible_become_exe": "",
        "ansible_become_flags": "",
        "ansible_shell_type": "",
        "ansible_python_interpreter": "",
        "ansible_shell_executable": "",
    }

    class Host:
        empty = {"ansible_host": ""}

        def __init__(self, name: str):
            self.name = name
            self.vars = Inventory.VARS.copy()
            self.storage_dir: str = ""
            self.configkey: str = ""
            self.member_of: List[Inventory.Group] = []

        def to_dict(self):
            data = {}
            for key, val in self.vars.items():
                if key == "ansible_host":
                    data[key] = val
                if val:
                    data[key] = val

            return {self.name: data}

        def __repr__(self) -> str:
            return self.name

    class Group:
        empty = {"hosts": {}, "vars": {}}

        def __init__(self, name: str):
            self.name: str = name
            self.storage_dir: str = ""
            self.configkey: str = ""
            self.children: List[Inventory.Group] = []
            self.hosts: List[Inventory.Host] = []
            self.vars = Inventory.VARS.copy()

        def get_host(self, host_name: str):
            for host in self.hosts:
                if host.name == host_name:
                    return host
            return None

        def add_host(self, host):
            if host not in self.hosts:
                self.hosts.append(host)

                if self not in host.member_of:
                    host.member_of.append(self)

        def to_dict(self):
            hosts_data: Dict[str, Any] = {}
            vars_data: Dict[str, Any] = {}
            # children_data: Dict[str, Any] = {}
            all_data: Dict[str, Any] = {
                "hosts": hosts_data,
                "vars": vars_data,
            }

            for host in self.hosts:
                if self.name != "all":
                    # freeipa_clients:
                    #   hosts:
                    #     server_one:
                    # hosts_data.append({host.name: {}})
                    hosts_data[host.name] = {}
                else:
                    # all:
                    #   hosts:
                    #     server_one:
                    #       ansible_host: 0.0.0.0
                    hosts_data.update(host.to_dict())

            for key, val in self.vars.items():
                if val:
                    vars_data[key] = val

            return {self.name: all_data}

        def __repr__(self) -> str:
            return self.name

    def __init__(self, path: str, project_dir: str):
        self.path = path
        self.project_dir = project_dir
        self.hosts: List[Inventory.Host] = []
        self.host_names: List[str] = []
        self.groups: List[Inventory.Group] = []
        self.group_names: List[str] = []

    def setup(self):
        default = {"all": {"hosts": {}}}
        data = yamlmanager.read(self.path)
        if data is None:
            yamlmanager.write(self.path, default)
            return

        data, _ = datautils.fix_dict(default, data)

        # parse the groups
        for group_name, group_data in data.items():
            group, _ = self.add_group(group_name)
            group_data, _ = datautils.fix_dict(self.Group.empty, group_data)

            for key, value in group_data.items():
                # group variables
                if key == "vars":
                    for varkey, varval in value.items():
                        group.vars[varkey] = varval

                # group members
                if key == "hosts":
                    for host_name, host_data in value.items():
                        host, was_created = self.add_host(host_name)
                        if was_created:
                            host.vars, _ = datautils.fix_dict(self.Host.empty, host_data)
                        group.add_host(host)

    def add_host(self, host_name: str) -> tuple[Host, bool]:
        """Add a host to the inventory.

        - Trys to get the host from the inventory
        - Creates a new host if it doesn't exist
        - Adds the host to the "all" group.
        - Creates a storage directory for the host

        Arguments:
            host_name -- Name of the host to add

        Keyword Arguments:
            target_group -- Group to add the host to (default: {"all"})

        Returns:
            tuple -- (object: Host, bool: was_created)
        """
        was_created = False
        if not host_name:
            raise ValueError("Host name is required")

        host = self.get_host(host_name)
        if host is None:
            host = self.Host(host_name)
            was_created = True
        host.storage_dir = os.path.join(self.project_dir, "files", "hosts", host_name)
        filemanager.check_dir(host.storage_dir, create=True)
        host.configkey = host_name

        group = self.get_group("all")
        if group is None:
            raise ReferenceError("Group 'all' not found in inventory")

        group.add_host(host)

        if host_name not in self.host_names:
            self.host_names.append(host_name)

        if host not in self.hosts:
            self.hosts.append(host)

        return host, was_created

    def add_group(self, group_name: str) -> tuple[Group, bool]:
        was_created = False
        group = self.get_group(group_name)
        if group is None:
            group = self.Group(group_name)
            if group not in self.groups:
                self.groups.append(group)
            if group_name not in self.group_names:
                self.group_names.append(group_name)
            was_created = True

        group.storage_dir = os.path.join(self.project_dir, "files", "groups", group_name)
        filemanager.check_dir(group.storage_dir, create=True)
        group.configkey = group_name

        return group, was_created

    def get_host(self, host_name: str):
        for host in self.hosts:
            if host.name == host_name:
                return host
        return None

    def get_group(self, group_name: str) -> Group | None:
        for group in self.groups:
            if group.name == group_name:
                return group
        return None

    def delete_host(self, host: Host):
        for group in host.member_of:
            group.hosts.remove(host)
        self.update_config()

    def update_config(self):
        for host in self.hosts:
            self.save_host(host)
        for group in self.groups:
            self.save_group(group)
        print("Inventory updated")

    def save_group(self, group: Group):
        group_data = group.to_dict()
        if group.name != group.configkey:
            yamlmanager.delete(self.path, group.configkey)

            new_dir = group.storage_dir.replace(f"/{group.configkey}", f"/{group.name}")
            os.rename(group.storage_dir, new_dir)

            print(f"save_group: {group.configkey} -> {group.name}")
            group.storage_dir = new_dir
            group.configkey = group.name
        yamlmanager.update(self.path, group.name, group_data[group.name])
        print(f"save_group: {group.name}")

    def save_host(self, host: Host):
        """Save the host to the inventory config file.

        Host variables are saved to their host entry in the
        all group.

        Arguments:
            host -- Host object to save

        Raises:
            Exception: The "all" group is required in the inventory.
        """
        group = self.get_group("all")
        if group is None:
            raise ReferenceError("Group 'all' not found in inventory")
        group_data = group.to_dict()

        if host.name != host.configkey:
            yamlmanager.delete(self.path, "all")

            new_dir = host.storage_dir.replace(f"/{host.configkey}", f"/{host.name}")
            os.rename(host.storage_dir, new_dir)

            host.storage_dir = new_dir
            host.configkey = host.name

        yamlmanager.update(self.path, "all", group_data["all"])
        print(f"save_host: {host.name}")
