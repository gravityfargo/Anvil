from os import getenv

from dotenv import load_dotenv

from anvil.config import CONFIG_FILE, DATA_DIR, TEMP_DIR, ProjectData
from anvil.gui import gui_main
from anvil.helpers import configutils, filemanager


def anvil():
    load_dotenv()
    filemanager.check_dir(TEMP_DIR, create=True)
    filemanager.check_dir(DATA_DIR, create=True)
    filemanager.check_file(CONFIG_FILE, create=True)
    configutils.validate_config(ProjectData)
    ProjectData.verify_projects()
    gui_main()
