from typing import Dict, List, Union

from anvil.helpers import datautils, yamlmanager


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
            self.configkey: str = ""
            self.member_of: List[Inventory.Group] = []

        def to_dict(self):
            data = {}
            for key, val in self.vars.items():
                if key == "ansible_host":
                    data[key] = val
                if val:
                    data[key] = val

            return {
                self.name: data,
            }

        def __repr__(self) -> str:
            return self.name

    class Group:
        empty = {"hosts": {}, "vars": {}}

        def __init__(self, name: str):
            self.name: str = name
            self.children: List[Inventory.Group] = []
            self.hosts: List[Inventory.Host] = []
            self.vars = Inventory.VARS.copy()

        def get_host(self, host_name: str):
            for host in self.hosts:
                if host.name == host_name:
                    return host
            return None

        def to_dict(self):
            group_dict = {
                self.name: {
                    "children": [],
                    "hosts": {},
                    "vars": {},
                }
            }
            data = group_dict[self.name]

            for host in self.hosts:
                group_hosts: dict = data["hosts"]
                group_hosts.update(host.to_dict())
                if self.name != "all":
                    group_hosts[host.name] = {}

            for v, k in self.vars.items():
                if k:
                    data["vars"][v] = k

            if not data["vars"]:
                data.pop("vars")

            if not data["children"]:
                data.pop("children")

            return group_dict

        def __repr__(self) -> str:
            return self.name

    def __init__(self, path: str):
        self.path = path
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
            group = self.add_group(group_name)
            group_data, _ = datautils.fix_dict(self.Group.empty, group_data)

            for key, value in group_data.items():
                # group variables
                if key == "vars":
                    for varkey, varval in value.items():
                        group.vars[varkey] = varval

                # group members
                if key == "hosts":
                    for host, host_data in value.items():
                        host, was_created = self.add_host(host, group_name)
                        if was_created:
                            host.vars, _ = datautils.fix_dict(self.Host.empty, host_data)

        # Make sure all hosts are in the "all" group
        all_group = self.get_group("all")
        all_group.hosts = self.hosts

    def add_host(self, host_name: str, target_group: str = "all", update: bool = False) -> tuple[Host, bool]:
        # TODO: add to "all" group
        was_created = False
        host = self.get_host(host_name)
        if host is None:
            host = self.Host(host_name)
            was_created = True

        host.configkey = host_name

        group = self.get_group(target_group)
        if group.get_host(host_name) is None:
            group.hosts.append(host)

        host.member_of.append(group)

        if host_name not in self.host_names:
            self.hosts.append(host)
            self.host_names.append(host_name)

        if update:
            self.update_config()
        return host, was_created

    def add_group(self, group_name: str, update: bool = False) -> Group:
        """Add a group if it does not exist.

        Arguments:
            group_name -- name of group

        Keyword Arguments:
            update -- push changes to config file (default: {False})

        Returns:
            Group object
        """
        group = self.Group(group_name)
        if group_name not in self.group_names:
            self.groups.append(group)
            self.group_names.append(group_name)

        if update:
            self.update_config()
        return group

    def get_host(self, host_name: str):
        for host in self.hosts:
            if host.name == host_name:
                return host
        return None

    def get_group(self, group_name: str) -> Group:
        """Get a group by name, or create it if it does not exist.

        Arguments:
            group_name -- Name of the group to get.

        Returns:
            Group -- The group object.
        """
        for group in self.groups:
            if group.name == group_name:
                return group
        group = self.add_group(group_name)
        return group

    def delete_host(self, host: Host):
        for group in host.member_of:
            group.hosts.remove(host)
        self.update_config()

    def update_config(self):
        for group in self.groups:
            data = group.to_dict()
            for g, d in data.items():
                yamlmanager.update(self.path, g, d)
