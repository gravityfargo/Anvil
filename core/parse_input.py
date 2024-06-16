from core.helpers import ConditionChecks, HelpMessage
import traceback
from core.helpers import pcolor, pdebug
from core.file_utils import (
    YamlManager,
    initialize_new_project,
    import_existing_project,
    set_s_project,
    set_s_host,
    set_s_group,
    list_to_str,
    sync_configs_with_project_files,
)
from config.vars import AnvilData

from ansible import ping, playbook
from os import path
import subprocess

# cli question and import project playbook directory

def user_input_parser(ad: AnvilData, argument):
    cc = ConditionChecks(ad)
    try:
        match argument[0]:
            case s if s.startswith("-s"):
                cc.check_len("-s", 3, s)

                s = s[2:]
                match s:
                    case "p":
                        cc.check_len("-sp", 2, argument)
                        ad = set_s_project(ad, argument[1])

                    case "h":
                        cc.check_s_project()
                        cc.check_len("-sh", 2, argument)
                        ad = set_s_host(ad, argument[1])

                    case "g":
                        cc.check_s_project()
                        cc.check_len("-sg", 2, argument)
                        ad = set_s_group(ad, argument[1])
                        
                    case "pb":
                        # playboot directory
                        pass
                        
            case s if s.startswith("-c"):
                cc.check_len("-c", 3, s)
                s = s[2:]
                match s:
                    case "p":
                        cc.check_len("-cp", 2, argument)
                        initialize_new_project(argument[2])

            case s if s.startswith("-d"):
                cc.check_len("-d", 3, s)
                cc.check_s_project()
                cc.check_s_host()

                s = s[2:]
                match s:
                    case "g":
                        cc.check_len("-dg", 2, argument)

                        if argument[1] not in ad.sp_groups_list:
                            print(pcolor("Invalid Group", "red"))
                            return True

                        print(
                            pcolor(
                                "\nDo you really want to delete this group?",
                                "red",
                            )
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
                            print(pcolor(f"Deleted Group {argument[1]}", "green"))

            case s if s.startswith("-i"):
                cc.check_len("-i", 3, s)
                s = s[2:]
                match s:
                    case "p":
                        cc.check_len("-ip", 2, argument)
                        projectname = argument[1]
                        if argument[1] in ad.all_projects:
                            print(pcolor("Project already exists.", "red"))
                            return True
                        print(
                            pcolor(
                                "Use an alternate directory? (y/n)",
                                "purple",
                            )
                        )
                        user_input = input()
                        if user_input == "y":
                            print(
                                pcolor(
                                    "Enter the full path to the project directory:",
                                    "purple",
                                )
                            )
                            user_input = input()
                            ret_status = import_existing_project(
                            ad, projectname, user_input
                            )
                        else:
                            ret_status = import_existing_project(ad, projectname)
                            ret_status = False

                        if ret_status == True:
                            print(
                                pcolor(
                                    f"Project {projectname} successfully imported!",
                                    "yellow",
                                )
                            )

            case s if s.startswith("-l"):
                cc.check_s_project()
                cc.check_len("-l", 3, s)
                s = s[2:]
                match s:
                    case "g":
                        cc.check_s_project()
                        print(pcolor(f"Groups:\n { ad.sp_groups_list }", "yellow"))
                    case "h":
                        cc.check_s_project()
                        cc.check_s_host()
                        print(
                            pcolor(
                                f"Hosts:\n {ad.sp_hosts}",
                                "yellow",
                            )
                        )
                    case "p":
                        print(pcolor(f"Projects:\n { ad.all_projects }", "yellow"))

                    case _:
                        print(pcolor(f"Invalid Input\n {HelpMessage("-l")}", "red"))

            case "-u":
                cc.check_s_project()
                ad = sync_configs_with_project_files(ad)

                if type(ad) is bool:
                    return False
                print(pcolor(f"Update Successful.", "purple"))

            case s if s.startswith("-p"):
                print(pcolor("Ping", "cyan"))
                if ad.s_project is None:
                    print(pcolor("ERROR:\t Select a Project First", "red"))
                    return True

                if len(s) < 3:
                    print(
                        pcolor(
                            "-pa Ping all Hosts\n -ph Ping <host_name>\n -pg Ping <group_name>",
                            "red",
                        )
                    )
                    return True
                s = s[2:]
                match s:
                    case "a":
                        print(pcolor("Ping All", "cyan"))
                        ping(ad, "all")
                    case "h":
                        print(pcolor("Ping Host", "cyan"))
                        if len(argument) != 2:
                            print(pcolor("-ph <host_name>", "red"))
                            return True

                        if argument[1] not in ad.sp_hosts:
                            print(pcolor("Not a valid host.", "red"))
                            return True
                        ping(ad, argument[1])

                    case "g":
                        print(pcolor("Ping Host Group", "cyan"))
                        if len(argument) != 2:
                            print(pcolor("-pg <group_name>", "red"))
                            return True

                        if argument[1] not in ad.sp_groups_list:
                            print(pcolor("Not a valid group.", "red"))
                            return True
                        ping(ad, argument[1])

            case s if s.startswith("-r"):
                cc.check_s_project()
                cc.check_s_host()
                cc.check_len("-r", 3, s)

                s = s[2:]
                match s:
                    # fetch file
                    case "-fetch":
                        cc.check_len("-r-fetch", 2, argument)
                        result = playbook(ad, "-r-fetch", argument[1], ad.s_group, ad.s_host)
                    # send file
                    case "-send":
                        cc.check_len("-r-send", 2, argument)
                        result = playbook(ad, "-r-r-send", argument[1], ad.s_group, ad.s_host)
                    # restart service
                    case "-service-r":
                        cc.check_len("-r-service-r", 2, argument)
                        result = playbook(ad, "-r-service-r", argument[1], ad.s_group, ad.s_host)
                    case "-file-create":
                        cc.check_len("-r-file-create", 2, argument)
                        result = playbook(ad, "-r-file-create", argument[1], ad.s_group, ad.s_host)
                    case "-file-copy":
                        pass                         
            case "i":
                cc.check_s_project()

                pcolor("Project", "gray")
                pcolor(f"{ad.s_project}", "yellow")

                pcolor("Path:", "red")
                pcolor(f"{ad.sp_project_dir}", "yellow")

                pcolor("Groups:", "red")
                pcolor(f"{list_to_str(ad.sp_groups_list)}", "yellow")

                pcolor("Hosts:", "red")
                pcolor(f"{list_to_str(ad.sp_hosts)}", "yellow")

                
                if ad.s_group is not None: 
                    pcolor("\nGroup", "gray")
                    pcolor(f"{ad.s_group}", "purple")

                    pcolor("Path:", "red")
                    pcolor(f"{ad.sg_path}", "yellow")

                    pcolor("Hosts:", "red")
                    pcolor(f"{list_to_str(ad.sg_hosts)}", "yellow")
                if ad.s_host is not None: 
                    pcolor("\nHost", "gray")
                    pcolor(f"{ad.s_host}", "purple")

                    pcolor("Path:", "red")
                    pcolor(f"{ad.sh_path}", "yellow")

                    pcolor("Group:", "red")
                    pcolor(f"{ad.sh_group}", "yellow")

            case "q":
                return False

            case "-h" | "--help" | "?":
                print(pcolor("Arguments: ", "purple"))

                print(pcolor("-s Set", "red"))
                print(pcolor("\t-sp\t Set Project", "cyan"))
                print(pcolor("\t-sh\t Set Host", "cyan"))

                print(pcolor("-c Create", "red"))
                print(pcolor("\t-cp\t Create Project", "cyan"))

                print(pcolor("-d Delete", "red"))
                print(pcolor("\t-dg <group name>\t Delete Specified Group", "cyan"))

                print(pcolor("-i Import", "red"))
                print(pcolor("\t-ip\t Import Project", "cyan"))

                print(pcolor("-l List", "red"))
                print(pcolor("\t-lg\t List Host Groups", "cyan"))
                print(pcolor("\t-lg\t List All Hosts", "cyan"))
                print(pcolor("\t-lp\t List Projects", "cyan"))

                print(pcolor("-u Update", "red"))
                print(pcolor("\t-u\t Update Selected Project", "cyan"))

                print(pcolor("-p Ping", "red"))
                print(pcolor("\t-pa\t Ping All Hosts", "cyan"))
                print(pcolor("\t-ph <host_name>", "cyan"))
                print(pcolor("\t-pg <group_name>", "cyan"))

                print(pcolor("-r Remote", "red"))
                print(pcolor("\t-rf\t Fetch File from Selected Host", "cyan"))
                print(pcolor("\t-rs\t Send File to Selected Host", "cyan"))
                print(
                    pcolor("\t-rcom <command>\t Run a command on Selected Host", "cyan")
                )

                print(pcolor("i Info", "red"))
                print(pcolor("\ti\t Info Set Vars", "cyan"))

                print(pcolor("q Quit", "red"))

            case _:
                pass
    except:
        s = traceback.format_exc()
        print(pcolor(f"{s}", "red"))
    return True
