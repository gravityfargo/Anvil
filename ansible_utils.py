from ansible_runner import *
import sys
from os import path, getcwd
from cli.file_utils import (
    YamlManager,
    build_host_parent_path,
    return_hosts_parent_group,
    update_tree_file,
)
from config.vars import AnvilData


def ping(ad: AnvilData, host_pattern: str):
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        inventory=ad.sp_inventory_file_path,
        host_pattern=host_pattern,
        module="ping",
    )


def playbook(ad: AnvilData, sender: str, host_pattern: str, target: str):
    host_parent_path = build_host_parent_path(ad, host_pattern)
    extra_vars = {
        "arg_host": host_pattern,
        "arg_src": target,
        "arg_dest": host_parent_path,
    }
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        inventory=ad.sp_inventory_file_path,
        playbook=ad.playbooks[sender],
        extravars=extra_vars,
    )
    if r.status == "successful":
        parent = return_hosts_parent_group(ad, host_pattern)
        update_tree_file(ad)
        return True
    else:
        return False


def ad_hoc_shell(ad: AnvilData, host_pattern: str, command: str):
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        host_pattern=host_pattern,
        module="shell",
        module_args="whoami",
    )
    for event in r.events:
        print(event)
    # print(r.stats)
