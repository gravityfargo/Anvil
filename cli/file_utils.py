import yaml, re, git
from os import makedirs, path, listdir, getcwd
from config.vars import AnvilData


class YamlManager:
    def __init__(self, filename: str):
        self.filename = filename

        if not path.exists(self.filename):
            with open(self.filename, "w") as f:
                yaml.dump({}, f)

    def get_item(self, key1, key2=False, key3=False, key4=False):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file)
            if key1 in data and not key2 and not key3 and not key4:
                return data[key1]
            elif key1 in data and key2 in data[key1] and not key3 and not key4:
                return data[key1][key2]
            elif (
                key1 in data
                and key2 in data[key1]
                and key3 in data[key1][key2]
                and not key4
            ):
                return data[key1][key2][key3]
            elif (
                key1 in data
                and key2 in data[key1]
                and key3 in data[key1][key2]
                and key4 in data[key1][key2][key3]
            ):
                return data[key1][key2][key3][key4]
            else:
                return None  # key does not exist

    def get_all(self):
        with open(path.normpath(self.filename), "r") as file:
            data = yaml.safe_load(file)
            if data:
                return data
            else:
                return None  # data does not exist

    def create_or_update_item(self, key, value):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file) or {}
        data[key] = value
        with open(self.filename, "w") as file:
            yaml.safe_dump(data, file)

    def delete_item(self, key1, key2=False, key3=False, key4=False):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file)
            if key1 in data and not key2 and not key3 and not key4:
                del data[key1]
            elif key1 in data and key2 in data[key1] and not key3 and not key4:
                del data[key1][key2]
            elif (
                key1 in data
                and key2 in data[key1]
                and key3 in data[key1][key2]
                and not key4
            ):
                del data[key1][key2][key3]
            elif (
                key1 in data
                and key2 in data[key1]
                and key3 in data[key1][key2]
                and key4 in data[key1][key2][key3]
            ):
                del data[key1][key2][key3][key4]
            else:
                return False  # key does not exist
        with open(self.filename, "w") as file:
            yaml.safe_dump(data, file)
        return True


def build_host_parent_path(ad: AnvilData, host_name: str) -> str:
    groups_dict = ad.sp_groups
    for key, val in groups_dict.items():
        if host_name in list(val["hosts"].keys()):
            return path.join(ad.sp_project_dir, key)
    return None


def return_hosts_parent_group(ad: AnvilData, host_name: str) -> str:
    groups_dict = ad.sp_groups
    for key, val in groups_dict.items():
        if host_name in list(val["hosts"].keys()):
            return key
    return None


def set_s_project(ad: AnvilData, project_name: str):
    available_projects = YamlManager(ad.anvil_data_file).get_item("projects")
    if project_name in available_projects.keys():
        YamlManager(ad.anvil_data_file).create_or_update_item(
            "current_project", project_name
        )
        return project_name
    else:
        return list(available_projects.keys())


def set_s_host(ad: AnvilData, current_project: str, host_name: str):
    available_hosts = YamlManager(ad.anvil_data_file).get_item(
        "projects", current_project, "hosts"
    )
    if host_name in available_hosts:
        YamlManager(ad.anvil_data_file).create_or_update_item("s_host", host_name)
        return host_name
    else:
        return available_hosts


def initialize_new_project(project_name: str):
    project_dir = path.join("repo/", project_name)

    if not path.isdir(project_dir):
        git.Repo.init(project_dir)
    else:
        return False

    create_file_if_missing(project_dir, "inventory.yml")
    create_file_if_missing(project_dir, "tree.yaml")


def initial_setup(ad: AnvilData):
    create_directory_if_missing([ad.anvil_temp_dir])
    ad.root_path = getcwd()
    return ad


def import_existing_project(ad: AnvilData, project_name: str) -> bool:
    nad = AnvilData()
    nad.sp_project_dir = path.join(ad.root_path, "repo/", project_name)
    print(nad.sp_project_dir)

    nad.sp_inventory_file_path = path.join(nad.sp_project_dir, "inventory.yml")
    nad.sp_ansible_config_file_path = path.join(nad.sp_project_dir, "ansible.cfg")
    nad.sp_tree_file_path = path.join(nad.sp_project_dir, "tree.yaml")

    i = 1
    if not path.exists(nad.sp_project_dir):
        cprint(f"[{str(i)}] Project directory not found. Quitting.", "red")
        return False
    cprint(f"[{str(i)}] Project directory found.", "green")

    i += 1
    cprint(f"[{str(i)}] Now Syncing project fileswith Anvil.", "yellow")
    new_ad = sync_configs_with_project_files(nad, i)

    if type(new_ad) is bool:
        return False

    YamlManager(ad.anvil_data_file).create_or_update_item(
        "projects", {project_name: new_ad.export_project_dict()}
    )
    cprint(f"[{str(i)}] Import Successful.", "green")

    return True


def sync_configs_with_project_files(ad: AnvilData, i=0) -> bool:
    group_folders = []
    base_dir_items = []
    git_config = path.join(ad.sp_project_dir, ".git", "config")
    ad.sp_groups_list = []
    ad.sp_groups = {}
    ad.sp_hosts = []

    i += 1
    cprint(f"[{str(i)}] Searching Project Directory.", "green")
    for proj_root_item in listdir(ad.sp_project_dir):
        if path.isdir(path.join(ad.sp_project_dir, proj_root_item)):
            cprint(f"[{str(i)}] Found Group Folder: {proj_root_item}", "yellow")
            group_folders.append(proj_root_item)
        else:
            base_dir_items.append(proj_root_item)
            cprint(f"[{str(i)}] Found File: {proj_root_item}", "yellow")
        i += 1

    # check for .git folder
    if ".git" not in group_folders:
        i += 1
        cprint(f"[{str(i)}] .git folder not found. Fix that.", "red")
        return False

    # check for git config
    if not path.exists(git_config):
        i += 1
        cprint(f"[{str(i)}] .git/config not found. Fix that.", "red")
        return False

    # check git config for url
    with open(git_config, "r") as file:
        content = file.read()
        url = re.search(r"url\s*=\s*(.*)", content)
        if url is not None:
            ad.sp_repo_url = url.group(1)
        else:
            i += 1
            cprint(f"[{str(i)}] .git/config is missing its url. Fix that.", "red")
            return False

    # check for ansible.cfg
    if "ansible.cfg" not in base_dir_items:
        i += 1
        cprint(f"[{str(i)}] ansible.cfg is missing. Creating Now.", "yellow")
        create_file_if_missing(ad.sp_project_dir, "ansible.cfg")
        ad.sp_ansible_config_file_path = path.join(ad.sp_project_dir, "ansible.cfg")
    cprint(f"[{str(i)}] Ansible config found.", "green")

    i += 1
    # check for inventory.yml
    if "inventory.yml" not in base_dir_items:
        cprint(f"[{str(i)}] inventory.yml is missing. Fix that.", "red")
        return False
    cprint(f"[{str(i)}] Ansible hosts file found.", "green")

    # check for tree.yaml
    if "tree.yaml" not in base_dir_items:
        i += 1
        cprint(f"[{str(i)}] tree.yaml is missing. Creating Now.", "yellow")
        create_file_if_missing(ad.sp_project_dir, "tree.yaml")
        ad.sp_tree_file_path = path.join(ad.sp_project_dir, "tree.yaml")

    # extract hosts from inventory.yml
    with open(ad.sp_inventory_file_path, "r") as file:
        content = yaml.safe_load(file)
        group_data = {}
        for group, value in content.items():
            if group != "all":
                ad.sp_groups_list.append(group)
                i += 1
                cprint(f"[{str(i)}] Found Group: {group}", "yellow")
                group_data = content[group]
                ad.sp_groups[group] = group_data
    i += 1
    cprint(f"[{str(i)}] Ansible Host Groups imported from inventory.yaml.", "yellow")

    # TODO: compare directories to the existing folders
    update_tree_file(ad)

    # create directories for each host
    for group in ad.sp_groups:
        for hostname in ad.sp_groups[group]["hosts"].keys():
            i += 1
            cprint(f"[{str(i)}] Found Host: {hostname}", "yellow")
            ad.sp_hosts.append(hostname)
            create_directory_if_missing([ad.sp_project_dir, group, hostname])

    i += 1
    cprint(f"[{str(i)}] Ansible Hosts imported from inventory.yaml.", "yellow")
    cprint(f"[{str(i)}] Project Sync Complete.", "green")
    return ad


def update_tree_file(ad: AnvilData):
    tree_data = {}
    spd = ad.sp_project_dir

    def inventory_directory(directory):
        contents = {}
        for item in listdir(directory):
            item_path = path.join(directory, item)
            if path.isdir(item_path):
                contents[item] = inventory_directory(item_path)
            else:
                if "files" not in contents:
                    contents["files"] = []
                contents["files"].append(item)
        return contents

    for group in ad.sp_groups:
        group_path = path.join(spd, group)
        if path.isdir(group_path):
            tree_data[group] = inventory_directory(group_path)

    with open(ad.sp_tree_file_path, "w") as file:
        yaml.dump(tree_data, file, default_flow_style=False)


def create_file_if_missing(directory: str, filename: str):
    try:
        with open(path.join(directory, filename), "w") as file:
            file.write("")
    except:
        pass


def create_directory_if_missing(directory: list[str]):
    """
    directory (list[str]): list for path.join
    """
    folder_path = path.join(*directory)
    try:
        makedirs(path.join(folder_path))
    except:
        pass


def cprint(input_str: str, color: str):
    """
    input_str (str): string to be printed
    color (str): color to be used

    red, green, yellow, purple, cyan, gray, black
    """
    match color:
        case "red":
            print("\033[91m {}\033[00m".format(input_str))
        case "green":
            print("\033[92m {}\033[00m".format(input_str))
        case "yellow":
            print("\033[93m {}\033[00m".format(input_str))
        case "purple":
            print("\033[95m {}\033[00m".format(input_str))
        case "cyan":
            print("\033[96m {}\033[00m".format(input_str))
        case "gray":
            print("\033[97m {}\033[00m".format(input_str))
        case "black":
            print("\033[98m {}\033[00m".format(input_str))


# if __name__ == "__main__":
#     # extract_info_from_project("repo/Peddle-Configs")
#     # initialize_new_project("Peddle-Configs-2")
