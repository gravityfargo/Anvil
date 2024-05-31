import yaml, re, git
from os import makedirs, path

from config.vars import ANVIL_DATA_FILE


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


def set_selected_project(project_name: str):
    available_projects = YamlManager(ANVIL_DATA_FILE).get_item("projects")
    if project_name in available_projects.keys():
        YamlManager(ANVIL_DATA_FILE).create_or_update_item(
            "current_project", project_name
        )
        return project_name
    else:
        return list(available_projects.keys())


def set_current_host(current_project: str, host_name: str):
    available_hosts = YamlManager(ANVIL_DATA_FILE).get_item(
        "projects", current_project, "hosts"
    )
    if host_name in available_hosts:
        YamlManager(ANVIL_DATA_FILE).create_or_update_item("current_host", host_name)
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


def import_existing_project(project_name: str) -> bool:
    project_directory = path.join("repo/", project_name)
    project_data = {"url": "", "groups": {}}
    anvil_project = {project_name: project_data}
    git_config = path.join(project_directory, ".git", "config")
    inventory = path.join(project_directory, "inventory.yml")
    hosts_list = []

    i = 1
    if not path.exists(project_directory):
        cprint(f"[{str(i)}] Project directory not found", "red")
        return False
    cprint(f"[{str(i)}] Project directory found", "green")

    i += 1
    if not path.exists(git_config):
        cprint(f"[{str(i)}] Git config not found", "red")
        return False
    cprint(f"[{str(i)}] Git config found", "green")

    i += 1
    if not path.exists(inventory):
        cprint(f"[{str(i)}] Ansible hosts file not found", "red")
        return False
    cprint(f"[{str(i)}] Ansible hosts found", "green")
    project_data["inventory_file"] = str(inventory)

    i += 1
    with open(git_config, "r") as file:
        content = file.read()
        url = re.search(r"url\s*=\s*(.*)", content)
        if url is not None:
            project_data["url"] = url.group(1)
        else:
            cprint(f"[{str(i)}] git remote url not found", "red")
            return False
    cprint(f"[{str(i)}] Git remote url exists", "green")

    i += 1
    with open(inventory, "r") as file:
        content = yaml.safe_load(file)
        group_data = {}
        for group, value in content.items():
            if group != "all":
                # create_directory_if_missing([project_directory, group])
                group_data = content[group]
                project_data["groups"][group] = group_data
    for group in project_data["groups"]:
        for hostname in project_data["groups"][group]["hosts"].keys():
            hosts_list.append(hostname)
            create_directory_if_missing([project_directory, group, hostname])
    project_data["hosts"] = hosts_list
    cprint(f"[{str(i)}] Ansible hosts imported", "green")

    i += 1
    YamlManager(ANVIL_DATA_FILE).create_or_update_item("projects", anvil_project)
    cprint(f"[{str(i)}] Project imported successfully", "green")
    return True


def create_file_if_missing(directory: str, filename: str):
    try:
        with open(path.join(directory, filename), "w") as file:
            file.write("")
    except:
        pass


def create_directory_if_missing(directory: list[str]):
    """
    directory (list[str]): list for os.path.join
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
