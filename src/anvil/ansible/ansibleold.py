from ansible_runner import run
import json , os



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

    match sender_flag:

        case s if s.startswith("-r-service-"):
            if host_name is None:
                play["hosts"] = group_name

            match s:
                case "-r-service-s":
                    task["name"] = f"Starting {target} on {host_name}"
                    task[]["state"] = "started"
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
            play = os.path.join(ad.sp_playbooks_directory, targete)

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

    #








def ad_hoc_shell(ad: AnvilData, host_pattern: str, command: str):
    r = run(
        private_data_dir=ad.anvil_temp_dir,
        host_pattern=host_pattern,
        module="shell",
        module_args="whoami",
    )
