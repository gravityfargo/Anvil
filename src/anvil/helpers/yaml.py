import yaml
from yaml.representer import RepresenterError
import os
from anvil.helpers.files import check_file


def read_yaml(item_path, key: str = None) -> dict | None:
    """Get data from the yaml file.
    If key is provided, return the value of that key.
    """
    if os.path.exists(item_path):
        with open(os.path.join(item_path), "r") as file:
            data = yaml.safe_load(file)
        if key is not None:
            return data.get(key, None)
        return data
    else:
        return None


def overwrite_yaml(file_path: str, data: dict):
    """Overwrite a yaml file with the provided data."""
    with open(file_path, "w") as file:
        yaml.safe_dump(data, file)


def update_yaml(file_path: str, key: dict, value: dict) -> None:
    """Update a yaml file with the provided key and value."""
    with open(file_path, "r") as file:
        data = yaml.safe_load(file) or {}

    if key in data and isinstance(data[key], dict) and isinstance(value, dict):
        data[key].update(value)
    else:
        data[key] = value
    try:
        with open(file_path, "w") as file:
            yaml.safe_dump(data, file)
    except RepresenterError:
        print(f"A class property is missing.")
    except Exception as e:
        print(f"An error occurred: {e}")


class YamlManager:
    def __init__(self, item_path: str):
        """Initialize the YamlManager with the path to the yaml file."""
        self.item_path = item_path

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

    def get_item(self, key) -> dict | str | int | None:
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return None
            return self._recursive_search(data, key)

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
        with open(self.item_path, "r") as file:
            data = yaml.safe_load(file)
            if not data:
                return False

        if self._recursive_delete(data, key):
            with open(self.item_path, "w") as file:
                yaml.safe_dump(data, file)
            return True
        return False

    def validate_yaml_file(self, defaults_dict: dict, create: bool = True) -> dict:
        """
        Validates a yaml file against a dictionary of defaults. \n
        - If file missing, optionally create it. \n
        - If missing keys, they will be added. \n
        - If extra keys, they will be removed. \n
        - If is empty, it will be populated with defaults. \n
        returns the validated data.
        """
        if not isinstance(defaults_dict, dict):
            raise ValueError("defaults must be a dictionary")

        check_file(self.item_path, create=create)
        file_name = self.item_path.split("/")[-1]
        file_contents = self.get_all()
        if isinstance(file_contents, dict):
            data, ret_val = self.align_dicts(file_contents, defaults_dict)
            if not ret_val:
                self.save_all(data)

        else:
            data = defaults_dict
            self.save_all(data)
        return data
