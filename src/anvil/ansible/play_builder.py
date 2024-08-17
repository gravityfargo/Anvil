from typing import Any, Dict


class PlayBuilder:
    hosts: list = []
    BASE_PLAY = {
        "name": "Playbook",
        "hosts": hosts,
        "gather_facts": True,
        "become": True,
        "tasks": [],
    }
    private_data_dir: str = ""
    host_pattern: str = ""

    def __init__(self):
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
            "name": f"Fetch {src_file}",
            "ansible.builtin.fetch": {
                "src": src_file,
                "dest": target_file,
                "flat": True,
            },
        }
        playbook = self.BASE_PLAY.copy()
        playbook["tasks"].append(task)
        self.run_args["playbook"] = playbook
