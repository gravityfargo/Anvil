from .config_options import AnvilOptions, CONFIG_PATH
from .project import Project
from .cli import DEFAULT_CLI_ARGS


def init():
    """Initialize variable classes."""
    from anvil.helpers.files import check_dir, check_file
    from anvil.helpers.yaml import overwrite_yaml
    from anvil.helpers.data_helper import fix_dict
    from anvil.helpers.yaml import read_yaml

    print("Initialization of AnvilData")

    check_dir(AnvilOptions.temp_dir, create=True)
    check_dir(AnvilOptions.data_dir, create=True)
    check_file(CONFIG_PATH, create=True)

    # read config file
    config_file_data = read_yaml(CONFIG_PATH)

    default_options = AnvilOptions.read_config_file()
    if isinstance(config_file_data, dict) is False:
        # create config file with default options
        overwrite_yaml(CONFIG_PATH, default_options)
        config_file_data = default_options

    # config was read, check if all options are present
    fix_dict(config_file_data["options"], AnvilOptions.get_dict())

    # update config object
    AnvilOptions.update_from_dict(config_file_data["options"])

    # write config file
    AnvilOptions.update_config_file()
