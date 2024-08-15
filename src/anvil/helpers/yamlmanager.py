import sys
from typing import Any, Dict

import yaml
from yaml.representer import RepresenterError


def read(item_path, key: str = "") -> Dict[str, Any]:
    """Get data from the yaml file.
    If key is provided, return the value of that key.
    """

    try:
        with open(item_path, "r", encoding="utf-8") as file:
            data: Dict[str, Any] = yaml.safe_load(file)

        if not data:
            return {}

        if key:
            return data.get(key, {})

        return data

    except FileNotFoundError:
        print(f"File not found: {item_path}")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def write(file_path: str, data: dict, key: str = ""):
    """Overwrite a yaml file with the provided data."""

    data_to_write = read(file_path)
    if key:
        data_to_write[key] = data
    else:
        data_to_write = data

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(data_to_write, file)


def update(file_path: str, key: str, value):
    """Update a yaml file with the provided key and value."""
    read_data = read(file_path)

    if key in read_data and isinstance(read_data[key], dict):
        read_data[key].update(value)
    else:
        read_data[key] = value

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(read_data, file)

    except RepresenterError as e:
        print(e)
        print("Error updating yaml file, RepresenterError")
        sys.exit(1)

    except Exception as e:
        # Catch any other exception that wasn't caught by the specific handlers
        print(f"An unexpected error occurred: {e}")


# class YamlManager:
#     def __init__(self, item_path: str):
#         """Initialize the YamlManager with the path to the yaml file."""
#         self.item_path = item_path

#     def _recursive_search(self, data, key):
#         """Recursively search for a key in a nested dictionary."""
#         if isinstance(data, dict):
#             if key in data:
#                 return data[key]
#             for sub_key, sub_value in data.items():
#                 result = self._recursive_search(sub_value, key)
#                 if result is not None:
#                     return result
#         return None

#     def get_item(self, key) -> dict | str | int | None:
#         with open(self.item_path, "r") as file:
#             data = yaml.safe_load(file)
#             if not data:
#                 return None
#             return self._recursive_search(data, key)

#     def _recursive_delete(self, data, key):
#         """Recursively delete a key in a nested dictionary."""
#         if isinstance(data, dict):
#             if key in data:
#                 del data[key]
#                 return True
#             for sub_key, sub_value in data.items():
#                 if self._recursive_delete(sub_value, key):
#                     if isinstance(sub_value, dict) and not sub_value:
#                         del data[sub_key]
#                     return True
#         return False

#     def delete_item(self, key):
#         with open(self.item_path, "r") as file:
#             data = yaml.safe_load(file)
#             if not data:
#                 return False

#         if self._recursive_delete(data, key):
#             with open(self.item_path, "w") as file:
#                 yaml.safe_dump(data, file)
#             return True
#         return False

#     def validate_yaml_file(self, defaults_dict: dict, create: bool = True) -> dict:
#         """
#         Validates a yaml file against a dictionary of defaults. \n
#         - If file missing, optionally create it. \n
#         - If missing keys, they will be added. \n
#         - If extra keys, they will be removed. \n
#         - If is empty, it will be populated with defaults. \n
#         returns the validated data.
#         """
#         if not isinstance(defaults_dict, dict):
#             raise ValueError("defaults must be a dictionary")

#         check_file(self.item_path, create=create)
#         file_name = self.item_path.split("/")[-1]
#         file_contents = self.get_all()
#         if isinstance(file_contents, dict):
#             data, ret_val = self.align_dicts(file_contents, defaults_dict)
#             if not ret_val:
#                 self.save_all(data)

#         else:
#             data = defaults_dict
#             self.save_all(data)
#         return data
