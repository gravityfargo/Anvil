from cli.file_utils import (
    YamlManager,
    initialize_new_project,
    import_existing_project,
    cprint,
    set_selected_project,
    set_current_host,
)
from config.vars import AnvilData
from ansible_utils import ping
from copy import deepcopy


def init_anvil():
    ad = AnvilData()
    anvil_data = YamlManager(ad.anvil_data_file).get_all()
    ad.all_projects = list(anvil_data["projects"].keys())
    ad.selected_project = anvil_data["selected_project"]
    if ad.selected_project is not None:
        projectdata = anvil_data["projects"][anvil_data["selected_project"]]
        ad.selected_host = anvil_data["selected_host"]
        ad.selected_project_groups_list = list(projectdata["groups"].keys())
        ad.selected_project_groups = projectdata["groups"]
        ad.selected_project_inventory_file = projectdata["inventory_file"]
        ad.selected_project_hosts = projectdata["hosts"]
        ad.selected_project_url = projectdata["url"]
    return ad


def user_input_parser(ad: AnvilData, user_input):
    # ad = AnvilData()
    # ad = deepcopy(ad_in)
    argument = user_input.split(" ")

    match argument[0]:
        case "-sp" | "--set-project":
            if len(argument) == 2:
                returnval = set_selected_project(argument[1])
                if type(returnval) == str:
                    cprint(f"Current Project is now: {returnval}", "yellow")
                elif type(returnval) == list:
                    cprint("ERROR:\t Project does not exist!", "red")
                    cprint(f"Available Projects: {returnval}", "yellow")

        case "-sh" | "--set-host":
            if ad.selected_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            if len(argument) != 2:
                cprint("ERROR:\t Incorrect usage", "red")
                cprint("-sh <hostname>", "yellow")
                return True

            returnval = set_current_host(ad.selected_project, argument[1])
            if type(returnval) == str:
                cprint(f"Current Host is now: {returnval}", "yellow")
            elif type(returnval) == list:
                cprint("ERROR:\t Host does not exist!", "red")
                cprint(f"Available Hosts: {returnval}", "yellow")

        case "-pc" | "--project-create":
            if len(argument) == 3:
                initialize_new_project(argument[2])
            else:
                cprint("ERROR:\t initproject <project_name>", "red")

        case "-pi" | "--project-import":
            if len(argument) == 2:
                ret_status = import_existing_project(argument[1])
                if ret_status == True:
                    init_anvil()
                    cprint(f"Project {argument[1]} successfully imported!", "yellow")
                else:
                    cprint(f"ERROR:\t Import Failed", "red")
            else:
                cprint("ERROR:\t importproject <project_name>", "red")

        case "-i" | "--info":
            cprint("Current Project:", "purple")
            cprint(f"\t{ad.selected_project}", "green")
            cprint("Current Host:", "purple")
            cprint(f"\t{ad.selected_host}", "green")

        case "-dh" | "--delete-host":
            if ad.selected_project is not None:
                if len(argument) == 3:
                    print(argument)
                else:
                    cprint("ERROR:\t Not enough arguments", "red")
                    cprint("requred:\t deletehost <group> <host>", "yellow")

        case "-l" | "--list":
            if len(argument) == 2 and ad.selected_project is not None:
                if argument[1] == "groups" or argument[1] == "g":
                    cprint(f"Groups:\n { ad.selected_project }", "yellow")

        case "-g" | "--group":
            # [m]
            if len(argument) == 1:
                cprint("-g <group>", "yellow")
                cprint(
                    f"Available Groups: { ad.selected_project_groups_list }", "yellow"
                )
                return True

            if ad.selected_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            if argument[1] not in ad.selected_project_groups_list:
                cprint("ERROR:\t Invalid Group", "red")
                cprint(
                    f"Available Groups: { ad.selected_project_groups_list }", "yellow"
                )
                return True

            # [m, m]
            if len(argument) < 3:
                cprint("-l\t list sub-items\n -d\t delete group", "yellow")
                return True

            match argument[2]:
                # is the second arugement -l or -d?
                case "-l" | "--list":
                    # [m, m, m]
                    if len(argument) < 4:
                        cprint("options:\n\thosts | h", "yellow")
                        return True

                    match argument[3]:
                        case "h" | "hosts":
                            cprint(
                                f"Hosts:\n {ad.selected_project_hosts}",
                                "yellow",
                            )
                        # case "vars" | "v":
                        #     cprint(f"Vars:\n {groups[argument[1]]['vars']}", "yellow")

                case "-d" | "--delete":
                    cprint(
                        "Do you really want to delete this group?",
                        "red",
                    )
                    decision = input("y/n")
                    if decision == "y":
                        cprint("Deleting group", "red")
                        YamlManager(ad.anvil_data_file).delete_item(
                            "projects", ad.selected_project, "groups", argument[1]
                        )
                        init_anvil()

                case _:
                    cprint(f"-g {argument[1]}", "yellow")
                    cprint(
                        f"\t-l hosts\n \t-l vars",
                        "yellow",
                    )

        case "-h" | "--help":
            pass

        case "-cc" | "--create-config":
            pass

        case "-p" | "--ping":
            if ad.selected_project is None:
                cprint("ERROR:\t Select a Project First", "red")
                return True

            if len(ad.selected_project_groups_list) == 0:
                cprint("ERROR:\t There are no groups", "red")
                return True

            ping(ad.selected_project_inventory_file, "auth")
            return True

        case "-u" | "--update":
            if selected_project is None:
                cprint("ERROR:\t Select a Project First", "red")
            import_existing_project(selected_project)

        case "q":
            return False

        case _:
            cprint("ERROR:\t Command not found", "red")

    return True
