from cli.file_utils import (
    YamlManager,
    initialize_new_project,
    import_existing_project,
    cprint,
    set_s_project,
    set_s_host,
    initial_setup,
    sync_configs_with_project_files,
    update_tree_file,
)
from config.vars import AnvilData
from ansible_utils import ping, playbook
from os import path
import subprocess


def init_anvil():
    ad = AnvilData()
    ad = initial_setup(ad)

    anvil_data = YamlManager(ad.anvil_data_file).get_all()
    ad.all_projects = list(anvil_data["projects"].keys())
    if anvil_data["s_project"] is None:
        return ad

    ad.s_project = anvil_data["s_project"]
    if ad.s_project is not None:
        projectdata = anvil_data["projects"][anvil_data["s_project"]]
        ad.s_host = anvil_data["s_host"]
        ad.sp_groups_list = projectdata["groups_list"]
        ad.sp_groups = projectdata["groups"]
        ad.sp_inventory_file_path = path.join(
            ad.root_path, projectdata["inventory_file_path"]
        )
        ad.sp_tree_file_path = projectdata["tree_file_path"]
        ad.sp_hosts = projectdata["hosts"]
        ad.sp_repo_url = projectdata["repo_url"]
        ad.sp_project_dir = projectdata["project_dir"]

    for key, value in ad.playbooks.items():
        ad.playbooks[key] = path.join(ad.root_path, "playbooks", value)
    return ad


def user_input_parser(ad: AnvilData, user_input):
    argument = user_input.split(" ")

    match argument[0]:
        # case "":
        #     update_tree_file(ad)
        #     return False

        case s if s.startswith("-s"):
            cprint("Set", "cyan")
            if len(s) < 3:
                cprint("-sp <project_name> \n -sh <hostname>", "red")
                return True

            s = s[2:]
            match s:
                case "p":
                    cprint("Set Project", "cyan")
                    if len(argument) != 2:
                        cprint("-sp <project_name>", "red")
                        return True

                    returnval = set_s_project(ad, argument[1])
                    if type(returnval) == str:
                        ad.s_project = returnval
                        cprint(f"Current Project is now: {returnval}", "green")
                    elif type(returnval) == list:
                        cprint("Project does not exist!", "red")
                        cprint(f"Available Projects: {returnval}", "yellow")

                case "h":
                    cprint("Set Host", "cyan")
                    if ad.s_project is None:
                        cprint("Select a Project First", "red")
                        return True

                    if len(argument) != 2:
                        cprint("-sh <hostname>", "red")
                        return True

                    returnval = set_s_host(ad, ad.s_project, argument[1])
                    if type(returnval) == str:
                        ad.s_host = returnval
                        cprint(f"Current Host is now: {returnval}", "yellow")
                    elif type(returnval) == list:
                        cprint("Host does not exist!", "red")
                        cprint(f"Available Hosts: {returnval}", "yellow")

        case s if s.startswith("-c"):
            cprint("Create", "cyan")
            if len(s) < 3:
                cprint("-cp <project_name>", "red")
                return True

            s = s[2:]
            match s:
                case "p":
                    cprint("Create Project", "cyan")
                    if len(argument) == 3:
                        initialize_new_project(argument[2])
                    else:
                        cprint("-cp <project_name>", "red")

        case s if s.startswith("-d"):
            cprint("Delete", "cyan")
            if ad.s_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            if len(s) < 3:
                cprint("-dg <group_name>", "red")
                return True

            s = s[2:]
            match s:
                case "g":
                    cprint("Delete Group", "cyan")
                    if len(argument) < 2:
                        cprint("-dg <group_name>", "red")
                        return True

                    if argument[1] not in ad.sp_groups_list:
                        cprint("Invalid Group", "red")
                        return True

                    cprint(
                        "\nDo you really want to delete this group?",
                        "red",
                    )
                    decision = input("y/n")
                    if decision == "y":
                        YamlManager(ad.anvil_data_file).delete_item(
                            "projects", ad.s_project, "groups", argument[1]
                        )
                        subprocess.run(
                            [
                                "rm",
                                "-rf",
                                path.join(ad.sp_project_dir, argument[1]),
                            ]
                        )
                        init_anvil()
                        cprint(f"Deleted Group {argument[1]}", "green")

        case s if s.startswith("-i"):
            cprint("Import", "cyan")
            if len(s) < 3:
                cprint("-ip <project_name>", "red")
                return True

            s = s[2:]
            match s:
                case "p":
                    cprint("Import Project", "cyan")
                    if len(argument) != 2:
                        cprint("-ip <project_name>", "red")
                        return True
                    if argument[1] == ad.sp_project:
                        cprint("Project already exists.", "red")
                        return True
                    ret_status = import_existing_project(ad, argument[1])
                    if ret_status == True:
                        init_anvil()
                        cprint(
                            f"Project {argument[1]} successfully imported!",
                            "yellow",
                        )

        case s if s.startswith("-l"):
            cprint("List", "cyan")
            if len(s) < 3:
                cprint("-lg List Host Groups\n -lh List Hosts", "red")
                return True

            s = s[2:]
            match s:
                case "g":
                    cprint(f"Groups:\n { ad.sp_groups_list }", "yellow")
                case "h":
                    cprint(
                        f"Hosts:\n {ad.sp_hosts}",
                        "yellow",
                    )
        # UPDATE NEEDS TO GET CONFIG FILES AS WELL
        case "-u":
            cprint("Update", "cyan")
            if ad.s_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            ad = sync_configs_with_project_files(ad)

            if type(ad) is bool:
                return False
            cprint(f"Update Successful.", "purple")

        case s if s.startswith("-p"):
            cprint("Ping", "cyan")
            if ad.s_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            if len(s) < 3:
                cprint(
                    "-pa Ping all Hosts\n -ph Ping <host_name>\n -pg Ping <group_name>",
                    "red",
                )
                return True
            s = s[2:]
            match s:
                case "a":
                    cprint("Ping All", "cyan")
                    ping(ad, "all")
                case "h":
                    cprint("Ping Host", "cyan")
                    if len(argument) != 2:
                        cprint("-ph <host_name>", "red")
                        return True

                    if argument[1] not in ad.sp_hosts:
                        cprint("Not a valid host.", "red")
                        return True
                    ping(ad, argument[1])

                case "g":
                    cprint("Ping Host Group", "cyan")
                    if len(argument) != 2:
                        cprint("-pg <group_name>", "red")
                        return True

                    if argument[1] not in ad.sp_groups_list:
                        cprint("Not a valid group.", "red")
                        return True
                    ping(ad, argument[1])

        case s if s.startswith("-r"):
            cprint("Remote", "cyan")
            if ad.s_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True
            if ad.s_host is None:
                cprint("ERROR:\t Select a Host First", "red")
                return True

            if len(s) < 3:
                cprint(
                    "-rf <target_file> Fetch File from Selected Host\n -rc <command> Run a command on Selected Host",
                    "red",
                )
                return True

            s = s[2:]
            match s:
                case "f":
                    cprint("Fetch from Selected Host", "cyan")
                    if len(argument) < 2:
                        cprint("-rf <target_file>", "red")
                        return True
                    result = playbook(ad, "-rf", ad.s_host, argument[1])
                    if result:
                        cprint("File Fetched Successfully", "green")

                case "c":
                    cprint("Run command on Selected Host", "cyan")
                    # git fe
                    # git pull

        case "i" | "info":
            cprint("Current Project:", "purple")
            cprint(f"\t{ad.s_project}", "green")
            cprint("Current Host:", "purple")
            cprint(f"\t{ad.s_host}", "green")

        case "q":
            return False

        case "-h" | "--help" | "?":
            cprint("Arguments: ", "purple")

            cprint("-s Set", "red")
            cprint("\t-sp\t Set Project", "cyan")
            cprint("\t-sh\t Set Host", "cyan")

            cprint("-c Create", "red")
            cprint("\t-cp\t Create Project", "cyan")

            cprint("-d Delete", "red")
            cprint("\t-dg <group name>\t Delete Specified Group", "cyan")

            cprint("-i Import", "red")
            cprint("\t-ip\t Import Project", "cyan")

            cprint("-l List", "red")
            cprint("\t-lg\t List Host Groups", "cyan")
            cprint("\t-lg\t List All Hosts", "cyan")

            cprint("-u Update", "red")
            cprint("\t-u\t Update Selected Project", "cyan")

            cprint("-p Ping", "red")
            cprint("\t-pa\t Ping All Hosts", "cyan")
            cprint("\t-ph <host_name>", "cyan")
            cprint("\t-pg <group_name>", "cyan")

            cprint("-r Remote", "red")
            cprint("\t-rf\t Fetch File from Selected Host", "cyan")
            cprint("\t-rc\t Run a command on Selected Host", "cyan")

            cprint("i Info", "red")
            cprint("\ti\t Info Set Vars", "cyan")

            cprint("q Quit", "red")

        case _:
            pass

    return True
