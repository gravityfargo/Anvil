from cli.file_utils import (
    YamlManager,
    initialize_new_project,
    import_existing_project,
    cprint,
    set_s_project,
    set_s_host,
    initial_setup,
    sync_configs_with_project_files,
)
from config.vars import AnvilData
from ansible_utils import ping, playbook
from os import path
import subprocess


def user_input_parser(ad: AnvilData, user_input):
    argument = user_input.split(" ")

    match argument[0]:
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

                    ad = set_s_project(ad, argument[1])

                case "h":
                    cprint("Set Host", "cyan")
                    if ad.s_project is None:
                        cprint("Select a Project First", "red")
                        return True

                    if len(argument) < 2:
                        cprint("-sh <hostname>", "red")
                        return True

                    ad = set_s_host(ad, argument[1])

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
                        sync_configs_with_project_files(ad)
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
                    projectname = argument[1]

                    if argument[1] in ad.all_projects:
                        cprint("Project already exists.", "red")
                        return True

                    cprint(
                        "Use an alternate directory? (y/n)",
                        "purple",
                    )
                    user_input = input()

                    if user_input == "y":
                        cprint(
                            "Enter the full path to the project directory:", "purple"
                        )
                        user_input = input()
                        ret_status = import_existing_project(
                            ad, projectname, user_input
                        )
                    else:
                        ret_status = import_existing_project(ad, projectname)

                    if ret_status == True:
                        cprint(
                            f"Project {projectname} successfully imported!",
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
                case "p":
                    cprint(f"Projects:\n { ad.all_projects }", "yellow")

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
                    "-rf <target_file> Fetch File from Selected Host\n -rs <target_file> Send a File to Target Host\n -rc <command> Run a command on Selected Host",
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
                    result = playbook(ad, "-rf", argument[1], ad.s_group, ad.s_host)
                    if result:
                        cprint("File Fetched Successfully", "green")
                    else:
                        cprint("Error Fetching File", "red")

                case "com":
                    cprint("Run command on Selected Host", "cyan")
                    # git fe
                    # git pull

                case "s":
                    cprint("Copy to Selected Host", "cyan")
                    if len(argument) < 2:
                        cprint("-rs <target_file>", "red")
                        return True

                    result = playbook(ad, "-rs", argument[1], ad.s_group, ad.s_host)
                    if result:
                        cprint("File Sent Successfully", "green")
                    else:
                        cprint("Error Sending File", "red")

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
            cprint("\t-lp\t List Projects", "cyan")

            cprint("-u Update", "red")
            cprint("\t-u\t Update Selected Project", "cyan")

            cprint("-p Ping", "red")
            cprint("\t-pa\t Ping All Hosts", "cyan")
            cprint("\t-ph <host_name>", "cyan")
            cprint("\t-pg <group_name>", "cyan")

            cprint("-r Remote", "red")
            cprint("\t-rf\t Fetch File from Selected Host", "cyan")
            cprint("\t-rs\t Send File to Selected Host", "cyan")
            cprint("\t-rcom <command>\t Run a command on Selected Host", "cyan")

            cprint("i Info", "red")
            cprint("\ti\t Info Set Vars", "cyan")

            cprint("q Quit", "red")

        case _:
            pass

    return True
