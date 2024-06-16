import yaml, re, git, json
from os import makedirs, path, listdir, getcwd
from config.vars import AnvilData
from core.helpers import pcolor, pdebug


def init_anvil(ad: AnvilData) -> AnvilData:
    ad = initial_setup(ad)

    anvil_data = YamlManager(ad.anvil_data_file).get_all()
    if anvil_data["projects"] is None:
        pcolor("No projects found. Create or import a new project.", "red")
        return ad

    ad.all_projects = list(anvil_data["projects"].keys())
    if anvil_data["s_project"] is None:
        return ad

    ad.s_project = anvil_data["s_project"]
    if ad.s_project:
        projectdata = anvil_data["projects"][ad.s_project]
        ad.sp_groups_list = projectdata["groups_list"]
        ad.sp_groups = projectdata["groups"]
        ad.sp_ansible_config_file_path = projectdata["ansible_config_file_path"]
        ad.sp_inventory_file_path = path.join(
            ad.root_path, projectdata["inventory_file_path"]
        )
        ad.sp_tree_file_path = projectdata["tree_file_path"]
        ad.sp_hosts = projectdata["hosts"]
        ad.sp_repo_url = projectdata["repo_url"]
        ad.sp_project_dir = projectdata["project_dir"]
        ad.sp_variables_file_path = projectdata["variables_file_path"]
        ad.sp_playbooks_directory = projectdata["playbooks_directory"]

        s_group = anvil_data.get("s_group")
        s_host = anvil_data.get("s_host")

        # No s_group or "all" s_group = no s_host
        if not s_group or s_group.startswith("all"):
            ad.s_host = None
            ad.sh_path = None
            ad.sh_group = None
            set_s_host(ad, None if not s_group else s_host)

        # No s_group = no sg_*
        if not s_group:
            ad.s_group = None
            ad.sg_path = None
            ad.sg_hosts = None
        # "all" s_group = no sg_hosts
        elif s_group.startswith("all"):
            ad.s_group = s_group
            ad.sg_path = build_group_path(ad, s_group)
            ad.sg_hosts = []
        else:
            ad.s_group = s_group
            ad.sg_path = build_group_path(ad, s_group)
            ad.sg_hosts = get_hosts_from_group(ad, s_group)

        # Check if host belongs to group
        if ad.s_group and s_host:
            if s_host not in ad.sg_hosts:
                ad.s_host = None
                ad.sh_path = None
                ad.sh_group = None
                set_s_host(ad, None)
            else:
                ad.s_host = s_host
                ad.sh_path = build_host_path(ad, s_group, s_host)
                ad.sh_group = s_group
    return ad


class YamlManager:
    def __init__(self, filename: str):
        self.filename = filename

        if not path.exists(self.filename):
            with open(self.filename, "w") as f:
                yaml.safe_dump({}, f)

    def _recursive_search(self, data, key):
        """Recursively search for a key in a nested dictionary."""
        if isinstance(data, dict):
            if key in data:
                return data[key]
            for sub_key, sub_value in data.items():
                result = self._recursive_search(sub_value, key)
                if result is not None:
                    return result
        return None

    def get_item(self, key):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return None
            return self._recursive_search(data, key)

    def get_all(self):
        with open(path.normpath(self.filename), "r") as file:
            data = yaml.safe_load(file)
            return data if data else None

    def create_or_update_item(self, key, value):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file) or {}

        if key in data and isinstance(data[key], dict) and isinstance(value, dict):
            data[key].update(value)
        else:
            data[key] = value

        with open(self.filename, "w") as file:
            yaml.safe_dump(data, file)

    def _recursive_delete(self, data, key):
        """Recursively delete a key in a nested dictionary."""
        if isinstance(data, dict):
            if key in data:
                del data[key]
                return True
            for sub_key, sub_value in data.items():
                if self._recursive_delete(sub_value, key):
                    if isinstance(sub_value, dict) and not sub_value:
                        del data[sub_key]
                    return True
        return False

    def delete_item(self, key):
        with open(self.filename, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return False

        if self._recursive_delete(data, key):
            with open(self.filename, "w") as file:
                yaml.safe_dump(data, file)
            return True
        return False

    def save_all(self, data):
        with open(self.filename, "w") as file:
            yaml.safe_dump(data, file)


def build_host_path(ad: AnvilData, group_name: str, host_name: str) -> str:
    return path.join(ad.sp_project_dir, group_name, host_name)


def build_group_path(ad: AnvilData, group_name: str) -> str:
    return path.join(ad.sp_project_dir, group_name)


def set_s_project(ad: AnvilData, project_name: str) -> AnvilData:
    if project_name in ad.all_projects:
        YamlManager(ad.anvil_data_file).create_or_update_item("s_project", project_name)
        ad = init_anvil(ad)
        pcolor(f"Current Project is now: {project_name}", "green")
    else:
        pcolor("Not a valid project.", "red")
    return ad


def set_s_host(ad: AnvilData, host_name: str) -> AnvilData:
    if host_name in ad.sp_hosts:
        YamlManager(ad.anvil_data_file).create_or_update_item("s_host", host_name)
        host_group = get_group_from_host(ad, host_name)
        YamlManager(ad.anvil_data_file).create_or_update_item("s_group", host_group)
        ad = init_anvil(ad)
        pcolor(f"Current Host is now: {host_name}", "green")
        pcolor(f"Current Group is now: {host_group}", "green")
    elif host_name is None:
        YamlManager(ad.anvil_data_file).create_or_update_item("s_host", None)
    else:
        pcolor("Not a valid host.", "red")
    return ad


def set_s_group(ad: AnvilData, group_name: str) -> AnvilData:
    if group_name in ad.sp_groups_list:
        YamlManager(ad.anvil_data_file).create_or_update_item("s_group", group_name)
        if ad.s_host not in get_hosts_from_group(ad, group_name):
            YamlManager(ad.anvil_data_file).create_or_update_item("s_host", None)
        ad = init_anvil(ad)
        pcolor(f"Current Group is now: {group_name}", "green")
    else:
        pcolor("Not a valid group.", "red")
    return ad


def get_group_from_host(ad: AnvilData, host_name: str) -> str:
    for group in ad.sp_groups_list:
        if group.startswith("all"):
            continue
        if host_name in list(ad.sp_groups[group]["hosts"].keys()):
            return group
    return None


def get_hosts_from_group(ad: AnvilData, group_name: str) -> list:
    if group_name.startswith("all"):
        return []
    return list(ad.sp_groups[group_name]["hosts"].keys())


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


def import_existing_project(ad: AnvilData, project_name: str, alt_dir=None) -> bool:
    nad = AnvilData()
    nad.s_project = project_name
    if alt_dir is not None:
        nad.sp_project_dir = alt_dir
    else:
        nad.sp_project_dir = path.join(ad.root_path, "repo/", project_name)

    nad.sp_inventory_file_path = path.join(nad.sp_project_dir, "inventory.yml")
    nad.sp_ansible_config_file_path = path.join(nad.sp_project_dir, "ansible.cfg")
    nad.sp_tree_file_path = path.join(nad.sp_project_dir, "tree.yaml")
    # are there any projects?
    if ad.all_projects != None:
        # does it already exist?
        if project_name in ad.all_projects:
            pcolor(f"Project {project_name} already exists.", "red")
            return False

    i = 1
    # check for project directory
    if not path.exists(nad.sp_project_dir):
        pcolor(f"[{str(i)}] Project directory not found. Quitting.", "red")
        return False
    pcolor(f"[{str(i)}] Project directory found.", "green")

    i += 1
    pcolor(f"[{str(i)}] Now Syncing project fileswith Anvil.", "yellow")
    new_ad = sync_configs_with_project_files(nad, i)

    if type(new_ad) is bool:
        return False

    YamlManager(ad.anvil_data_file).create_or_update_item(
        "projects", {project_name: new_ad.export_project_dict()}
    )
    # add new project to all_projects
    if ad.all_projects is None:
        ad.all_projects = []
    ad.all_projects.append(project_name)
    pcolor(f"[{str(i)}] Import Successful.", "green")
    return True


def sync_configs_with_project_files(ad: AnvilData, i=0) -> AnvilData:
    found_folders = []
    found_items = []
    git_config = path.join(ad.sp_project_dir, ".git", "config")
    ad.sp_groups_list = []
    ad.sp_groups = {}
    ad.sp_hosts = []

    i += 1
    pcolor(f"[{str(i)}] Searching Project Directory.", "green")
    for proj_root_item in listdir(ad.sp_project_dir):
        if path.isdir(path.join(ad.sp_project_dir, proj_root_item)):
            found_folders.append(proj_root_item)
        else:
            found_items.append(proj_root_item)

    # print found folders and files in order
    pcolor(f"Found folders:", "cyan")
    for item in found_folders:
        pcolor(f"- {item}", "yellow")

    pcolor(f"Found files:", "cyan")
    for item in found_items:
        pcolor(f"- {item}", "yellow")

    # check for .git folder
    if ".git" not in found_folders:
        i += 1
        pcolor(f"[{str(i)}] .git folder not found.", "red")
        ad.sp_repo_url = ""
    else:
        # check for git config
        if not path.exists(git_config):
            i += 1
            pcolor(f"[{str(i)}] .git/config not found.", "red")
            ad.sp_repo_url = ""
        else:
            # check git config for url
            with open(git_config, "r") as file:
                content = file.read()
                url = re.search(r"url\s*=\s*(.*)", content)
                if url is not None:
                    ad.sp_repo_url = url.group(1)
                else:
                    i += 1
                    print(
                        pcolor(
                            f"[{str(i)}] .git/config is missing its url. Fix that.",
                            "red",
                        )
                    )
                    return ad

    # check for ansible.cfg
    if "ansible.cfg" not in found_items:
        i += 1
        pcolor(f"[{str(i)}] ansible.cfg is missing. Creating Now.", "yellow")
        create_file_if_missing(ad.sp_project_dir, "ansible.cfg")
        ad.sp_ansible_config_file_path = path.join(ad.sp_project_dir, "ansible.cfg")
    else:
        ad.sp_ansible_config_file_path = path.join(ad.sp_project_dir, "ansible.cfg")

    # check for inventory.yml
    if "inventory.yml" not in found_items:
        i += 1
        pcolor(f"[{str(i)}] inventory.yml is missing. Fix that.", "red")
        return ad

    # check for tree.yaml
    if "tree.yaml" not in found_items:
        i += 1
        pcolor(f"[{str(i)}] tree.yaml is missing. Creating Now.", "yellow")
        create_file_if_missing(ad.sp_project_dir, "tree.yaml")
        ad.sp_tree_file_path = path.join(ad.sp_project_dir, "tree.yaml")

    # extract from inventory
    i += 1
    pcolor(f"[{str(i)}] Parsing inventory.yaml.", "green")
    with open(ad.sp_inventory_file_path, "r") as file:
        content = yaml.safe_load(file)
        group_data = {}
        for group, value in content.items():
            if group == "all":
                # key checks
                if content["all"].get("vars") is None:
                    continue
                else:
                    if content["all"]["vars"].get("anvil_all_groups") is None:
                        pass
                    elif len(content["all"]["vars"]["anvil_all_groups"]) == 0:
                        pass
                    else:
                        pcolor("All Host Groups", "cyan")
                        for allgroup in content["all"]["vars"]["anvil_all_groups"]:
                            pcolor(f"- {allgroup}", "yellow")
                            ad.sp_groups_list.append(allgroup)
                            ad.sp_groups[allgroup] = None

                    pcolor("Vars", "cyan")
                    if content["all"]["vars"].get("anvil_variables_file") is None:
                        pass
                    elif content["all"]["vars"]["anvil_variables_file"] == None:
                        pass
                    else:
                        j = content["all"]["vars"]["anvil_variables_file"]
                        if j.startswith(".."):
                            k = path.join(ad.sp_project_dir, j)
                            ad.sp_variables_file_path = path.normpath(k)
                        else:
                            ad.sp_variables_file_path = path.join(ad.sp_project_dir, j)
                        pcolor(f"- variables.yml", "yellow")
                continue

            pcolor(f"{group}", "cyan")
            ad.sp_groups_list.append(group)
            group_data = content[group]
            ad.sp_groups[group] = group_data
            for hostname in group_data["hosts"].keys():
                pcolor(f"- {hostname}", "yellow")
                ad.sp_hosts.append(hostname)

    # create directories
    i += 1
    pcolor(f"[{str(i)}] Checking Directories", "green")
    for group in ad.sp_groups:
        pcolor(f"{group}", "yellow")
        create_directory_if_missing([ad.sp_project_dir, group])
        if ad.sp_groups[group] is None:
            pass
        else:
            for hostname in ad.sp_groups[group]["hosts"].keys():
                pcolor(f"{hostname}", "yellow")
                create_directory_if_missing([ad.sp_project_dir, group, hostname])

    i += 1
    YamlManager(ad.anvil_data_file).create_or_update_item(
        "projects", {ad.s_project: ad.export_project_dict()}
    )
    pcolor(f"[{str(i)}] Project data saved to anvil.yaml", "green")

    i += 1
    update_tree_file(ad)
    pcolor(f"[{str(i)}] Updated tree.yaml", "green")

    i += 1
    pcolor(f"[{str(i)}] Sync of {ad.s_project} complete.", "green")

    return ad


def update_tree_file(
    ad, file_path=None, service_name=None, group_name=None, hostname=None
):
    file_data = YamlManager(ad.sp_tree_file_path).get_all()

    project_dir = ad.sp_project_dir

    def inventory_directory(directory, relative_path=""):
        contents = {}
        for item in listdir(directory):
            item_path = path.join(directory, item)
            rel_item_path = path.join(relative_path, item)
            if path.isdir(item_path):
                contents[item] = inventory_directory(item_path, rel_item_path)
            else:
                contents[item] = {"type": "file"}
        return contents

    def merge_data(existing_data, actual_data):
        for key, value in actual_data.items():
            if key in existing_data:
                if isinstance(existing_data[key], dict) and isinstance(value, dict):
                    merge_data(existing_data[key], value)
                else:
                    existing_data[key] = value
            else:
                existing_data[key] = value

    def add_or_update_service(data, config_path, service, group, host):
        keys = config_path.strip("/").split("/")
        if group not in data:
            data[group] = {}
        if host not in data[group]:
            data[group][host] = {}

        sub_data = data[group][host]
        for key in keys[:-1]:
            sub_data = sub_data.setdefault(key, {})
        last_key = keys[-1]
        if last_key in sub_data:
            sub_data[last_key].update({"service": service, "type": "file"})
        else:
            sub_data[last_key] = {"service": service, "type": "file"}

    actual_data = {}
    for group in ad.sp_groups:
        group_path = path.join(project_dir, group)
        if path.isdir(group_path):
            actual_data[group] = inventory_directory(group_path)

    merge_data(file_data, actual_data)

    if file_path and service_name and group_name and hostname:
        add_or_update_service(file_data, file_path, service_name, group_name, hostname)

    YamlManager(ad.sp_tree_file_path).save_all(file_data)


def create_file_if_missing(directory: str, filename: str):
    try:
        with open(path.join(directory, filename), "w") as file:
            file.write("")
    except:
        pass


def create_directory_if_missing(directory: list[str], announce=False):
    """
    directory (list[str]): list for path.join
    """
    folder_path = path.join(*directory)
    try:
        makedirs(path.join(folder_path))
        if announce:
            pcolor("created directory.", "yellow")
    except:
        if announce:
            pcolor("directory exists.", "yellow")
        pass


def list_to_str(input_list: list) -> str:
    return ", ".join(input_list)
