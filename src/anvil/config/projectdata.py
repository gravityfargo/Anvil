from os import getenv
from typing import Dict

from anvil.config.project import Project
from anvil.helpers import configutils, filemanager, yamlmanager

CONFIG_FILE = getenv("CONFIG_FILE", "config.yaml")
TEMP_DIR = getenv("TEMP_DIR", "/tmp/anvil")
DATA_DIR = getenv("DATA_DIR", "/tmp/anvil/data")


class ProjectData:
    config_file = CONFIG_FILE
    projects: Dict = {}
    project_list = []
    project_objs = {}
    selected_project = ""

    def __init__(self):
        pass

    @classmethod
    def verify_projects(cls):
        project_names = filemanager.get_directories(DATA_DIR)
        for project in project_names:
            cls.import_project(project)

    @classmethod
    def import_project(cls, project_name: str, create=False) -> bool:
        new_project = Project(project_name)
        ret = True

        if not filemanager.check_dir(new_project.root_dir, create):
            ret = False
        if not filemanager.check_file(new_project.tree_file, create):
            ret = False

        if not ret:
            print(f"project '{project_name}' has missing files.")
            return False

        cls.add_project(new_project)
        return True

    @classmethod
    def add_project(cls, project: Project):
        ret = True
        if project.name not in cls.project_list:
            cls.project_list.append(project.name)
            ret = False

        if project.name not in cls.projects:
            cls.projects[project.name] = configutils.class_to_dict(project)

            ret = False

        if not ret:
            cls.update_config()

        project.setup()
        cls.project_objs.update({project.name: project})

    @classmethod
    def get_project(cls, project_name: str) -> Project:
        """Get a project by name.

        If the project does not exist, a new project will be created.

        Arguments:
            project_name -- Name of the project to get.

        Returns:
            Project -- The project object.
        """
        project = cls.project_objs.get(project_name, Project(project_name))
        return project

    @classmethod
    def update_config(cls):
        data = configutils.class_to_dict(cls)
        del data["project_objs"]
        yamlmanager.update(cls.config_file, cls.__name__, data)

    @classmethod
    def __str__(cls):
        return cls.__name__

    @classmethod
    def __repr__(cls):
        return cls.__name__
