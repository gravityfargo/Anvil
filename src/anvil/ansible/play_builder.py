import json
from typing import Any, Dict


class PlayBuilder:
    private_data_dir: str = ""
    gather_facts: bool = True

    def __init__(self):
        self.host_pattern: str = ""
        self.hosts: list = []
        self.playbook = {
            "name": "Playbook",
            "hosts": self.hosts,
            "gather_facts": self.gather_facts,
            "become": True,
            "tasks": [],
        }
        self.run_args: Dict[str, Any] = {
            "private_data_dir": self.private_data_dir,
        }

    def get_run_args(self) -> dict:
        return self.run_args

    def module(self, module: str):
        """Set the module to run on the host/group.
        - `ping`
        """
        self.run_args["host_pattern"] = self.host_pattern
        self.run_args["module"] = module

    def fetch(self, src: str, dest: str):
        """
        src = ui.target_file_lineedit.text()
        dest = location of anvil instance
        """
        task = {
            "name": f"Fetching {src}",
            "ansible.builtin.fetch": {
                "src": src,
                "dest": dest,
                "flat": True,
            },
        }
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def send(self, src: str, dest: str):
        task = {
            "name": f"Sending {dest}",
            "ansible.builtin.copy": {
                "src": src,
                "dest": dest,
            },
        }
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def service(self, service_name: str, state: str, daemon_reload: bool = False):
        """Start, stop, or restart a service on the host/group."""
        task = {
            "name": f"Setting service {service_name} to {state}",
            "ansible.builtin.systemd_service": {
                "state": state,
                "name": service_name,
            },
        }
        if daemon_reload:
            task["ansible.builtin.systemd_service"]["daemon_reload"] = True
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def shell(self, commands: list[str]):
        for i, cmd in enumerate(commands):
            task = {
                "name": f"$ {cmd}",
                "ansible.builtin.command": {
                    "cmd": cmd,
                },
                "register": f"shell_out{i}",
            }

            self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def apt(self, package: str, state: str):
        task = {
            "name": f"Install {package}",
            "ansible.builtin.apt": {
                "name": package,
                "state": state,
            },
        }
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def print_json(self):
        print(json.dumps(self.run_args, indent=2))
