from ansible_runner import *
from core.helpers import BreakException
from core.helpers import pcolor, pdebug
from os import path, getcwd
import json
from core.file_utils import (
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


def create_task(task_template: dict, **kwargs):
    task = task_template.copy()
    task.update(kwargs)
    return task


def playbook(
    ad: AnvilData,
    sender_flag: str,       
    target,
    group_name,
    host_name,
    **kwargs,
):
    local_path = str(build_group_path(ad, group_name))
    mode = kwargs.get("mode")
    owner = kwargs.get("owner")
    group = kwargs.get("group")
    progress_callback = kwargs.get("progress_callback")
    stand_alone_command = "TBD"
    
    play = {
        "name": "Anvil Playbook",
        "hosts": host_name,
        "gather_facts": True,
        "become": True,
        "tasks": [],
    }
    
    if ad.sp_variables_file_path is not None:
        play["vars_files"] = [ad.sp_variables_file_path]

    if host_name is None:
        play["hosts"] = group_name

    match sender_flag:
        case "-r-fetch":
            dest = str(build_host_path(ad, group_name, host_name)) + target
            task = {
                "name": f"Fetch {target} from {host_name}",
                "ansible.builtin.fetch": {
                    "src": target,
                    "dest": dest,
                    "flat": True,
                },
            }
            play["tasks"].append(task)
            stand_alone_command = f"./anvil.py -r-fetch {target}"

        case "-r-send":
            if host_name is not None:
                local_path = str(build_host_path(ad, group_name, host_name))
            else:
                host_name = group_name
            
            task = {
                "name": f"Send {target} to {host_name}",
                "ansible.builtin.copy": {
                    "src": local_path + target,
                    "dest": target,
                },
            }
            play["tasks"].append(task)
            stand_alone_command = f"./anvil.py -r-send {target}"

        case s if s.startswith("-r-service-"):
            if host_name is None:
                play["hosts"] = group_name
            task = {
                "ansible.builtin.systemd_service": {
                    "name": target,
                },
            }
            match s:
                case "-r-service-s":
                    task["name"] = f"Starting {target} on {host_name}"
                    task["ansible.builtin.systemd_service"]["state"] = "started"
                    stand_alone_command = f"./anvil.py -r-service-s {target}"
                case "-r-service-r":
                    task["name"] = f"Restarting {target} on {host_name}"
                    task["ansible.builtin.systemd_service"]["state"] = "restarted"
                    stand_alone_command = f"./anvil.py -r-service-r {target}"
                case "-r-service-q":
                    task["name"] = f"Stopping {target} on {host_name}"
                    task["ansible.builtin.systemd_service"]["state"] = "stopped"
                    stand_alone_command = f"./anvil.py -r-service-q {target}"
            play["tasks"].append(task)

        case s if s.startswith("-r-file"):
            if host_name is None:
                host_name = group_name
            pcolor("ansible.builtin.file", "purple", progress_callback)
            pcolor(f"Host: {host_name}", "purple", progress_callback)
            task = {
                "ansible.builtin.file": {
                },
            }
            if target.get("dirvar") is not None or target.get("filevar") is not None:
                if target["state"] == "absent":
                        tempstate = "absent"
                # files from variables.yml
                if target.get("filevar") is not None:
                    entrylist = target["filevar"]
                    if target["state"] == "create":
                        tempstate = "touch"
                    elif target["state"] == "permissions":
                        tempstate = "file"
                    task["name"] = f"Creating files from {target["varname"]}"
                # directories from variables.yml
                elif target.get("dirvar") is not None:
                    entrylist = target["dirvar"]
                    if target["state"] == "create" or target["state"] == "permissions":
                        tempstate = "directory"
                    task["name"] = f"Creating directories from {target["varname"]}"
                    
            if target.get("dirvar") is not None or target.get("filevar") is not None:
                example_keys = list(entrylist[0].keys())
                task["ansible.builtin.file"]["path"] = "{{ item.path }}"
                    
                if "mode" in example_keys:
                    task["ansible.builtin.file"]["mode"] = "{{ item.mode }}"
                if "state" in example_keys:
                    task["ansible.builtin.file"]["state"] = "{{ item.state }}"                       
                if "state" not in example_keys:
                    task["ansible.builtin.file"]["state"] = tempstate
                if "owner" in example_keys:
                    task["ansible.builtin.file"]["owner"] = "{{ item.owner }}" 
                if "group" in example_keys:
                    task["ansible.builtin.file"]["group"] = "{{ item.group }}" 
                task["loop"] = "{{ " + f"{target['varname']}" + " }}"
                
            if target.get("manual") is not None:       
                if target["manual"].get("mode") is not None:
                    task["ansible.builtin.file"]["mode"] = target["manual"]["mode"]
                if target["manual"].get("owner") is not None:
                    task["ansible.builtin.file"]["owner"] = target["manual"]["owner"]
                if target["manual"].get("group") is not None:
                    task["ansible.builtin.file"]["group"] = target["manual"]["group"]
                if target["manual"].get("state") is not None:
                    task["ansible.builtin.file"]["state"] = target["manual"]["state"]
            
            stand_alone_command = f"./anvil.py -rc {target}"
            play["tasks"].append(task)

        case "-r-shell":
            if host_name is None:
                play["hosts"] = group_name

            i = 0
            for c in target:
                task = {
                    "name": f"Running {c} on {host_name}",
                    "ansible.builtin.shell": c,
                    "register": f"shell_out{str(i)}",
                }
                play["tasks"].append(task)

                debugtask = {
                    "name": f"Output of {c}",
                    "debug": {
                        "var": f"shell_out{str(i)}.stdout_lines",
                    },
                }
                play["tasks"].append(debugtask)
           
        case "-r-apt":
            pass
        
        case "-r-playbook":
            targete = target + ".yml"
            play = path.join(ad.sp_playbooks_directory, targete)

        case "-r-file-copy":
            if host_name is None:
                play["hosts"] = group_name
            task = {
                "name": f"Copying file to {host_name}",
                "ansible.builtin.copy": {
                },
            }
            if target.get("var") is not None:
                task["ansible.builtin.copy"]["src"] = "{{ item.localpath }}"
                task["ansible.builtin.copy"]["dest"] = "{{ item.remotepath }}"
                task["ansible.builtin.copy"]["owner"] = "{{ item.owner }}"
                task["ansible.builtin.copy"]["group"] = "{{ item.group }}"
                task["ansible.builtin.copy"]["mode"] = "{{ item.mode }}"
                task["loop"] = "{{ " + f"{target['var']}" + " }}"
            elif target.get("manual") is not None:
                task["ansible.builtin.copy"]["src"] = target['manual']["localpath"]
                task["ansible.builtin.copy"]["dest"] = target['manual']["remotepath"]
                if target.get("mode") is not None:
                    task["ansible.builtin.copy"]["owner"] = target['manual']["owner"]
                if target.get("group") is not None:
                    task["ansible.builtin.copy"]["group"] = target['manual']["group"]
                if target.get("mode") is not None:
                    task["ansible.builtin.copy"]["mode"] = target['manual']["mode"]
            play["tasks"].append(task)
    
    # pdebug(json.dumps(target, indent=4))
    pdebug(json.dumps(play, indent=4))
        
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        inventory=ad.sp_inventory_file_path,
        event_handler=event_handler(progress_callback),
        status_handler=status_handler,
        playbook=play,
    )

    # # pcolor("Stand-alone CLI Command", "cyan")
    # # pcolor(f"\t{stand_alone_command}", "cyan")
        
    if r.status == "successful":
        if sender_flag == "-r-fetch":
            update_tree_file(ad)
        return True
    else:
        return False


def event_handler(progress_callback):
    last_message = ""
    if progress_callback is not None:
        pc = progress_callback
        
        
    def handler(event_data):
        nonlocal last_message
        unnecessary_keys = [
            "uuid",
            "counter",
            "stdout",
            "start_line",
            "end_line",
            "runner_ident",
            "created",
            "pid",
            "parent_uuid",
        ]
        for key in unnecessary_keys:
            event_data.pop(key, None)

        # Process nested 'event_data' if present
        if "event_data" in event_data:
            nested_keys = [
                "playbook_uuid",
                "play_pattern",
                "task_action",
                "resolved_action",
                "task_path",
                "playbook",
                "play_uuid",
                "play",
                "task_uuid",
                "task_args",
                "remote_addr",
                "is_conditional",
                "uuid",
                "start",
                "end",
                "duration",
            ]
            for key in nested_keys:
                event_data["event_data"].pop(key, None)

            # Further clean up under 'res' if it exists
            if event_data["event_data"].get("res") is not None:
                event_data["event_data"]["res"].pop("invocation", None)
                event_data["event_data"]["res"].pop("_ansible_no_log", None)
                event_data["event_data"]["res"].pop("ansible_facts", None)

        match event_data["event"]:
            case "playbook_on_start":
                pass
            case "playbook_on_play_start":
                pass
            case "playbook_on_task_start":
                pass
            case "playbook_on_include":
                pass
            case "runner_item_on_skipped":
                pass
            case "runner_on_skipped":
                pass
            case "runner_on_start":
                if event_data["event_data"]["task"] != last_message:
                    pcolor(f"{event_data["event_data"]["task"]}", "black", pc)
                    last_message = event_data["event_data"]["task"]
            case "runner_on_ok":
                pcolor("runner_on_ok", "green")
                # pdebug(json.dumps(event_data, indent=4))
                color = "green"
                host = ""
                res = event_data["event_data"]["res"]
                if event_data["event_data"].get("host") is not None:
                    host = event_data["event_data"]["host"]
                    
                if "warnings" in res.keys():
                    for warning in res["warnings"]:
                        if warning is not None:
                            pcolor(f"{host}: {warning}", "yellow", pc)
                    res.pop("warnings", None)
                
                if res.get("results") is not None:
                    for i in res["results"]:
                        i.pop("invocation", None)
                        # pdebug(json.dumps(i, indent=4))
                        if i["changed"]:
                            color = "yellow"
                        if i.get("path") is not None:
                            pcolor(f"{host}: {i["path"]}", color, pc)
                        if i.get("dest") is not None:
                            pcolor(f"{host}: {i["dest"]}", color, pc)
                else:
                    if res["changed"]:
                        color = "yellow"
                    if res.get("path") is not None:
                        pcolor(f"{host}: {res["path"]}", color, pc)
                    if res.get("path") is not None:
                        pcolor(f"{host}: {res["dest"]}", color, pc)
            case "runner_item_on_ok":
                # pdebug(json.dumps(event_data["event_data"], indent=4))
                pcolor("runner_item_on_ok", "green")
                color = "green"
                if event_data["event_data"]["res"]["changed"]:
                    color = "yellow"
                    
                # if event_data["event_data"]["res"].get("path") is not None:
                #     pcolor(event_data["event_data"]["res"]["path"], color, pc)       
            case "runner_on_unreachable":
                pcolor(event_data["event_data"]["res"]["msg"], "red", pc)
            case "playbook_on_stats":
                pcolor("Done.", "gray", pc)
            case "runner_item_on_failed":
                pcolor(event_data["event_data"]["res"]["msg"], "red", pc)
            case "runner_on_failed":
                pcolor(event_data["event_data"]["res"]["msg"], "red", pc)
                pcolor("runner_on_failed", "red")
                pdebug(json.dumps(event_data["event_data"], indent=4))
            case "verbose":
                pass  # Explicitly do nothing for 'verbose'
            case _:
                pcolor(json.dumps(event_data, indent=4), "red", pc)
                pdebug(event_data)
    return handler

def status_handler(status_data, runner_config):
    status_data.pop("env", None)
    status_data.pop("runner_ident", None)
    status_data.pop("command", None)
    status_data.pop("cwd", None)
    # print(json.dumps(status_data, indent=4))

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
