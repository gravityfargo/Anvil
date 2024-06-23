import re, os
from core.helpers import YamlManager, FileManager, pcolor, pdebug, pjson


def import_existing_project(ad, project_name: str, project_dir: str) -> bool:
    pdebug("broken", "red")
    new_project = ad.project_template.copy()

    new_project["inventory_file"] = os.path.join(project_dir, "inventory.yml")
    new_project["ansible_config_file"] = os.path.join(project_dir, "ansible.cfg")
    new_project["tree_file"] = os.path.join(project_dir, "tree.yaml")
    new_project["path"] = project_dir

    if not os.path.exists(project_dir):
        pcolor("Project directory not found.", "red")
        return False
    pcolor("Project directory found.", "green")

    YamlManager(ad.anvil_config_file).create_or_update_item(
        "projects", {project_name: new_project}
    )
    pcolor("Import Successful.", "green")
    return True


def sync_project_with_file_system(
    config_file: str, s_project_dict: dict = None
) -> dict:
    found_folders = []
    found_items = []
    git_config = os.path.join(s_project_dict["path"], ".git", "config")

    for proj_root_item in os.listdir(s_project_dict["path"]):
        if os.path.isdir(os.path.join(s_project_dict["path"], proj_root_item)):
            found_folders.append(proj_root_item)
        else:
            found_items.append(proj_root_item)

    # check for git
    FileManager(s_project_dict["path"]).check_dir(".git")
    FileManager(git_config).check_file()
    with open(git_config, "r") as file:
        content = file.read()
        url = re.search(r"url\s*=\s*(.*)", content)
        if url is not None:
            s_project_dict["repo_url"] = url.group(1)

    FileManager(s_project_dict["ansible_config_file"]).check_file()
    FileManager(s_project_dict["inventory_file"]).check_file()
    FileManager(s_project_dict["tree_file"]).check_file()

    s_project_dict = parse_inventory_file(s_project_dict)

    # make sure directories exist
    for group in s_project_dict["groups"]:
        gpath = s_project_dict["groups"][group]["path"]
        vpath = s_project_dict["groups"][group]["var_file_path"]
        FileManager(gpath).check_dir()
        FileManager(vpath).check_file()

    for host in s_project_dict["hosts_list"]:
        hpath = s_project_dict["hosts"][host]["path"]
        FileManager(hpath).check_dir()

    YamlManager(config_file).create_or_update_item("s_project", s_project_dict)
    pcolor(["sync_project_with_file_system:", ["complete", "green"]])

    sync_tree_with_file_system(s_project_dict)


def sync_tree_with_file_system(project_dict: dict):
    tree_file = project_dict["tree_file"]
    current_tree = YamlManager(tree_file).get_all()
    tree = {}
    project_dir = project_dict["path"]

    def inventory_directory(directory):
        for item in os.listdir(directory):
            props = {"service": None, "commands": []}
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                inventory_directory(item_path)
            else:
                key = item_path.replace(project_dir, "")[1:]
                if current_tree.get(key) is not None:
                    if current_tree[key] != props:
                        props = current_tree[key]
                if key.endswith("_vars.yaml"):
                    continue
                tree[key] = props

    for group in project_dict["groups_list"]:
        group_path = os.path.join(project_dir, group)
        if os.path.isdir(group_path):
            inventory_directory(group_path)

    YamlManager(tree_file).save_all(tree)
    pcolor(["sync_tree_with_file_system:", ["complete", "green"]])


def parse_inventory_file(s_project_dict: dict) -> dict:
    s_project = {
        "allgroups_content": {},
        "all_pass": False,
        "groups": {},
        "groups_list": [],
        "hosts": {},
        "hosts_list": [],
    }

    inv_file_contents = YamlManager(s_project_dict["inventory_file"]).get_all()

    def process_content(inv_file_contents):
        nonlocal s_project

        for group, value in inv_file_contents.items():
            group_data = {
                "hosts": [],
                "var_file_path": None,
                "path": None,
            }
            if group == "all" and not s_project["all_pass"]:
                s_project["all_groups_content"] = inv_file_contents["all"]["vars"][
                    "anvil_all_groups"
                ]
                s_project["all_pass"] = True
                process_content(s_project["all_groups_content"])
                continue

            group_data["path"] = os.path.join(s_project_dict["path"], group)
            if group.startswith("all"):
                group_data.pop("hosts")
                vars_dict = s_project["all_groups_content"][group].get("vars")
            else:
                vars_dict = inv_file_contents[group].get("vars")
                for host in inv_file_contents[group]["hosts"].keys():
                    host_data = {
                        "group": None,
                        "path": None,
                    }
                    group_data["hosts"].append(host)
                    host_data["path"] = os.path.join(
                        s_project_dict["path"], group, host
                    )
                    host_data["group"] = group

                    s_project["hosts"][host] = host_data
                    s_project["hosts_list"].append(host)

            if vars_dict is not None:
                group_data["var_file_path"] = vars_dict["anvil_variable_file"]

            if group_data["var_file_path"] is not None:
                group_data["var_file_path"] = os.path.join(
                    s_project_dict["path"], group, group_data["var_file_path"]
                )

            s_project["groups_list"].append(group)
            s_project["groups"][group] = group_data

    process_content(inv_file_contents)

    s_project_dict["groups"] = s_project["groups"]
    s_project_dict["groups_list"] = s_project["groups_list"]
    s_project_dict["hosts"] = s_project["hosts"]
    s_project_dict["hosts_list"] = s_project["hosts_list"]

    return s_project_dict


def validate_yaml_file(file_path: str, defaults: dict) -> bool:
    file_contents = YamlManager(file_path).get_all()
    file_name = file_path.split("/")[-1]
    ret_val = True

    if file_contents is None:
        data = defaults
        pdebug(["validate_yaml_file:", [f"created {file_name}", "yellow"]])
        ret_val = False
    else:
        data, ret_val = align_dicts(file_contents, defaults)
        if not ret_val:
            pdebug(["validate_yaml_file:", [f"fixed {file_name}", "yellow"]])
        else:
            pdebug(["validate_yaml_file:", [f"valid {file_name}", "green"]])

    YamlManager(file_path).save_all(data)
    return ret_val


def align_dicts(target_dict, defaults_dict) -> tuple:
    ret_val = True
    # add missing keys
    for key, value in defaults_dict.items():
        if target_dict.get(key) is None:
            target_dict[key] = value
            ret_val = False

    # remove extra keys
    keys_to_remove = [key for key in target_dict if key not in defaults_dict]
    for key in keys_to_remove:
        del target_dict[key]
        ret_val = False

    return target_dict, ret_val
