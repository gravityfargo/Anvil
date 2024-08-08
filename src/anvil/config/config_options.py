import os
from anvil.helpers.yaml import update_yaml, read_yaml

PWD = os.getcwd()
CONFIG_PATH: str = os.path.join(PWD, "config.yaml")


class Data:
    """Base class for all data classes."""

    @classmethod
    def get_dict(cls) -> dict:
        data = {}
        for key in cls.variables:
            data[key] = getattr(cls, key)
        return data

    @classmethod
    def update_from_dict(cls, data: dict) -> None:
        """Update class attributes from a dictionary."""
        for key, value in data.items():
            setattr(cls, key, value)

    @classmethod
    def update_config_file(cls) -> None:
        """Update the config file with the current class attributes."""
        update_yaml(CONFIG_PATH, cls.config_key, cls.get_dict())

    @classmethod
    def read_config_file(cls) -> dict:
        """Get class attributes from the config file."""
        data = read_yaml(CONFIG_PATH, cls.config_key)
        return data

    @property
    def variables(self) -> list:
        return self.variables

    @property
    def config_key(self) -> list:
        return self.config_key


class AnvilOptions(Data):
    """General Options"""

    config_key = "options"
    variables = ["debug_level", "data_dir", "temp_dir"]

    debug_level = "debug"
    temp_dir = "/tmp/anvil"
    data_dir = PWD + "/instance"
