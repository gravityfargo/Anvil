from os import getenv

from anvil.helpers import datautils, yamlmanager


def class_to_dict(obj) -> dict:
    data = {}
    key: str
    for key, val in obj.__dict__.items():
        if isinstance(val, (str, int, float, bool, list, dict)):
            if key.startswith("__"):
                continue
            data[key] = val
    return data


def update_attr(obj, data: dict):
    for key, value in data.items():
        setattr(obj, key, value)


def validate_config(obj):
    read_configdata = yamlmanager.read(getenv("CONFIG_FILE"), obj.__name__)
    if isinstance(read_configdata, dict) is False:
        read_configdata = {obj.__name__: {}}

    default_configdata = class_to_dict(obj)
    fixed_configdata, _ = datautils.fix_dict(default_configdata, read_configdata, True)

    update_attr(obj, fixed_configdata)
