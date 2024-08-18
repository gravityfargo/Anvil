from typing import Any, Dict


class SystemdService:
    # "reloaded"
    # "restarted"
    # "started"
    # "stopped"

    def __init__(self, service_name: str):
        self.service_name = service_name

        self.task_args = {
            "name": service_name,
        }

        self.task = {
            "name": f"Start {service_name}",
            "ansible.builtin.systemd_service": self.task_args,
        }

    def start(self):
        self.task_args["state"] = "started"

    def __repr__(self):
        return "systemd_service"

    def export_task(self):
        return self.task


class PlayBuilder:
    private_data_dir: str = ""

    def __init__(self):
        self.host_pattern: str = ""
        self.hosts: list = []
        self.playbook = {
            "name": "Playbook",
            "hosts": self.hosts,
            "gather_facts": True,
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

    def fetch(self, src_file: str, target_file: str):
        task = {
            "name": f"Fetch {src_file} from {self.hosts}",
            "ansible.builtin.fetch": {
                "src": src_file,
                "dest": target_file,
                "flat": True,
            },
        }
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def send(self, src_file: str, target_file: str):
        task = {
            "name": f"Send {src_file} to {self.hosts}",
            "ansible.builtin.copy": {
                "src": src_file,
                "dest": target_file,
            },
        }
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook

    def service(self, service: SystemdService):
        """Start, stop, or restart a service on the host/group."""
        task = service.export_task()
        self.playbook["tasks"].append(task)
        self.run_args["playbook"] = self.playbook
