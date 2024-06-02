from ansible_runner import *
import sys
from os import path, getcwd
from cli.file_utils import (
    YamlManager,
    build_group_path,
    build_host_path,
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


def playbook(ad: AnvilData, sender: str, target: str, group_name="", host_name=""):

    match sender:
        case "-rf":
            local_path = str(build_group_path(ad, group_name))
            src_path = target
            dest_path = local_path

        case "-rs":
            local_path = str(build_host_path(ad, group_name, host_name))
            src_path = local_path + target
            dest_path = target

    extra_vars = {
        "arg_host_name": host_name,
        "arg_src_path": src_path,
        "arg_dest_path": dest_path,
    }
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        inventory=ad.sp_inventory_file_path,
        playbook=ad.playbooks[sender],
        extravars=extra_vars,
    )

    if r.status == "successful":
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
