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


def delete(file_path: str, key: str):
    """Delete a key from a yaml file."""
    read_data = read(file_path)

    if key in read_data:
        del read_data[key]

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(read_data, file)

    except RepresenterError as e:
        print(e)
        print("Error deleting key from yaml file, RepresenterError")
        sys.exit(1)

    except Exception as e:
        # Catch any other exception that wasn't caught by the specific handlers
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
