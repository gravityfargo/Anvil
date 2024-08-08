from os.path import join
from anvil.helpers.files import check_dir, check_file
from anvil.helpers.yaml import update_yaml
from anvil.config import Project, AnvilOptions


def fix_dict(target: dict, default: dict) -> tuple:
    """Fix a dictionary to match a default dictionary.

    Make sure the target dictionary has all the keys of the default dictionary.
    """
    ret_val = True
    # add missing keys
    for key, value in default.items():
        if target.get(key) is None:
            target[key] = value
            ret_val = False
    # remove extra keys
    keys_to_remove = [key for key in target if key not in default]
    for key in keys_to_remove:
        del target[key]
        ret_val = False

    return target, ret_val


def import_project(project_name: str, project_dir: str) -> bool:
    if check_dir(project_dir):
        print("Project directory found.")
    else:
        raise FileNotFoundError(f"Project directory not found: {project_dir}")
    p = Project()
    data_dir = join(AnvilOptions.data_dir, project_name)
    check_dir(data_dir, create=True)
    p.name = project_name
    p.directory = project_dir
    p.tree_file = join(data_dir, "tree.yaml")
    p.inventory_file = join(data_dir, "inventory.yml")
    p.ansible_config_file = join(project_dir, "ansible.cfg")

    check_file(p.tree_file, create=True)
    check_file(p.inventory_file, create=True)
    check_file(p.ansible_config_file, create=True)
