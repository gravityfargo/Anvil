import traceback, readline, sys
from anvil.ansible.ansibleold import ping, playbook
from os import path
import subprocess


def user_input_parser(ad: AnvilData, argument):
    cc = ConditionChecks(ad)
    if type(argument) is str:
        argument = argument.split(" ")
    pdebug(str(argument), "green")
    try:
        match argument[0]:
            case s if s.startswith("-s"):
                cc.check_len("-s", 3, s)

                s = s[2:]
                match s:
                    case "p":
                        cc.check_len("-sp", 2, argument)
                        if ad.projects is None:
                            pcolor("Invalid Project", "red")
                            return True
                        ad.set_s_project(argument[1])

                    case "h":
                        cc.check_s_project()
                        cc.check_len("-sh", 2, argument)
                        ad.set_s_host(argument[1])

                    case "g":
                        cc.check_s_project()
                        cc.check_len("-sg", 2, argument)
                        ad.set_s_group(argument[1])

                    case "pb":
                        # playboot directory
                        pass

            case s if s.startswith("-d"):
                cc.check_len("-d", 3, s)
                cc.check_s_project()
                cc.check_s_host()

                s = s[2:]
                match s:
                    case "g":
                        cc.check_len("-dg", 2, argument)

                        if argument[1] not in ad.sp_groups_list:
                            pcolor("Invalid Group", "red")
                            return True

                        pcolor("\nDo you really want to delete this group?", "red")

                        decision = input("y/n")
                        if decision == "y":
                            YamlManager(ad.anvil_config_file).delete_item(
                                "projects", ad.s_project, "groups", argument[1]
                            )
                            subprocess.run(
                                [
                                    "rm",
                                    "-rf",
                                    path.join(ad.sp_project_dir, argument[1]),
                                ]
                            )
                            sync_project_with_file_system(ad)
                            pcolor(f"Deleted Group {argument[1]}", "green")

            case s if s.startswith("-i"):
                cc.check_len("-i", 3, s)
                s = s[2:]
                match s:
                    case "p":
                        cc.check_len("-ip", 2, argument)
                        projectname = argument[1]
                        if ad.projects is not None:
                            if projectname in ad.projects.keys():
                                pcolor("Project already exists.", "red")
                                return True

                        if len(argument) > 2:
                            project_dir = argument[2]
                        else:
                            pcolor(
                                "Enter path to project:",
                                "purple",
                            )
                            project_dir = input()

                        ret_status = import_existing_project(ad, projectname, project_dir)

                        if ret_status == True:

                            pcolor(
                                f"Project {projectname} successfully imported!",
                                "yellow",
                            )

            case s if s.startswith("-l"):
                cc.check_s_project()
                cc.check_len("-l", 3, s)
                s = s[2:]
                match s:
                    case "g":
                        cc.check_s_project()
                        pcolor(f"Groups:\n { ad.sp_groups_list }", "yellow")
                    case "h":
                        cc.check_s_project()
                        cc.check_s_host()

                        pcolor(
                            f"Hosts:\n {ad.sp_hosts}",
                            "yellow",
                        )

                    case "p":
                        pcolor(f"Projects:\n { ad.projects }", "yellow")

                    case _:
                        help_message = HelpMessage("-l")
                        pcolor(f"Invalid Input\n {help_message}", "red")

            case "-u":
                cc.check_s_project()
                sync_project_with_file_system(ad.config_file, ad.s_project)

                if type(ad) is bool:
                    return False
                pcolor(f"Update Successful.", "purple")

            case s if s.startswith("-p"):
                pcolor("Ping", "cyan")
                if ad.s_project is None:
                    pcolor("ERROR:\t Select a Project First", "red")
                    return True

                if len(s) < 3:

                    pcolor(
                        "-pa Ping all Hosts\n -ph Ping <host_name>\n -pg Ping <group_name>",
                        "red",
                    )

                    return True
                s = s[2:]
                match s:
                    case "a":
                        pcolor("Ping All", "cyan")
                        ping(ad, "all")
                    case "h":
                        pcolor("Ping Host", "cyan")
                        if len(argument) != 2:
                            pcolor("-ph <host_name>", "red")
                            return True

                        if argument[1] not in ad.sp_hosts:
                            pcolor("Not a valid host.", "red")
                            return True
                        ping(ad, argument[1])

                    case "g":
                        pcolor("Ping Host Group", "cyan")
                        if len(argument) != 2:
                            pcolor("-pg <group_name>", "red")
                            return True

                        if argument[1] not in ad.sp_groups_list:
                            pcolor("Not a valid group.", "red")
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
                # pcolor(f"{list_to_str(ad.sp_groups_list)}", "yellow")

                pcolor("Hosts:", "red")
                # pcolor(f"{list_to_str(ad.sp_hosts)}", "yellow")

                if ad.s_group is not None:
                    pcolor("\nGroup", "gray")
                    pcolor(f"{ad.s_group}", "purple")

                    pcolor("Path:", "red")
                    pcolor(f"{ad.sg_path}", "yellow")

                    pcolor("Hosts:", "red")
                    # pcolor(f"{list_to_str(ad.sg_hosts)}", "yellow")
                if ad.s_host is not None:
                    pcolor("\nHost", "gray")
                    pcolor(f"{ad.s_host}", "purple")

                    pcolor("Path:", "red")
                    pcolor(f"{ad.sh_path}", "yellow")

                    pcolor("Group:", "red")
                    pcolor(f"{ad.sh_group}", "yellow")

            case "q":
                return False

    except BreakException as e:
        pcolor(f"{e}", "red")
    except:
        s = traceback.format_exc()
        pcolor(f"{s}", "red")
        quit(1)
    return True
