import os
import sys
from typing import List

import qdarktheme
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from anvil.ansible import PlayBuilder, Worker, WorkerSignals
from anvil.config import Inventory, Project, ProjectData

from .dialogs import ImportProjectDialog, SelectProjectDialog
from .inventorywindow import InventoryWindow
from .mainwindow_gui import MainWindow_UI


class MainWindow(QMainWindow):
    invwindow: InventoryWindow

    def __init__(self):
        super().__init__()
        qdarktheme.setup_theme("dark")
        self.thread_pool = QThreadPool()
        self.signals = WorkerSignals()
        self.manual = False
        if not ProjectData.selected_project:
            sys.exit()  # TODO: Select Project Dialog

        self.project: Project = ProjectData.get_project(ProjectData.selected_project)
        self.projectinventory = self.project.inventory
        self.hosts: List[Inventory.Host] = self.projectinventory.hosts
        self.groups: List[Inventory.Group] = self.projectinventory.groups
        PlayBuilder.private_data_dir = self.project.root_dir

        ui = MainWindow_UI()
        ui.init_ui(self)
        self.ui = ui

        self.inv_target = "all"
        self.inv_target_type = "group"

        # Connect signals here for visibility
        # tree
        ui.tree.clicked.connect(self.signal_tree_clicked)
        self.populate_tree()
        # lists
        ui.groups_list.clicked.connect(self.signal_groups_list_changed)
        ui.hosts_list.clicked.connect(self.signal_hosts_list_changed)
        self.populate_lists()
        # qactions
        ui.qaction_importproject.triggered.connect(self.dialog_importproject)
        ui.qaction_selectproject.triggered.connect(self.dialog_selectproject)
        ui.qaction_inventory.triggered.connect(self.window_inventory)
        ui.qaction_ping.triggered.connect(self.signal_ping)
        # buttons
        ui.send_file_button.clicked.connect(self.signal_send_file)
        ui.fetch_file_button.clicked.connect(self.signal_fetch_file)
        ui.button_service_start.clicked.connect(self.signal_quick_systemd)
        ui.button_service_stop.clicked.connect(self.signal_quick_systemd)
        ui.button_service_restart.clicked.connect(self.signal_quick_systemd)
        ui.button_service_status.clicked.connect(self.signal_quick_systemd)
        ui.quickshell_run_button.clicked.connect(self.signal_quick_shell)
        # check boxes
        ui.gather_facts.stateChanged.connect(self.signal_gather_facts)

    def signal_tree_clicked(self):
        ui = self.ui

        selected_file_path = ui.model.filePath(ui.tree.currentIndex())
        target_file_lineedit = ui.target_file_lineedit

        if os.path.isfile(selected_file_path):
            # get relative path
            relative_path = selected_file_path.replace(self.files_path, "")
            relative_path = relative_path.split("/")
            # trim path
            target_path = relative_path[3:]
            target_file_lineedit.setText(f"/{os.path.join(*target_path)}")

            self.target_file_local_path = selected_file_path
            self.target_file_remote_path = target_file_lineedit.text()

            ui.groups_list.clearSelection()
            ui.hosts_list.clearSelection()
            item_path = ui.model.filePath(ui.tree.currentIndex())
            self.helper_expand_tree(item_path)

            target_type = relative_path[1]
            target_name = relative_path[2]
            self.inv_target_type = target_type
            self.inv_target = target_name
            if target_type == "hosts":
                ui.hosts_list.findItems(target_name, Qt.MatchFlag.MatchExactly)[0].setSelected(True)
            elif target_type == "groups":
                ui.groups_list.findItems(target_name, Qt.MatchFlag.MatchExactly)[0].setSelected(True)

    def signal_hosts_list_changed(self):
        ui = self.ui
        if not self.manual:
            choice = ui.hosts_list.currentItem().text()
            host = self.projectinventory.get_host(choice)
            if host is not None:
                ui.groups_list.clearSelection()
                self.helper_expand_tree(host.storage_dir)

            self.inv_target = choice
            self.inv_target_type = "hosts"

    def signal_gather_facts(self):
        ui = self.ui
        PlayBuilder.gather_facts = ui.gather_facts.isChecked()

    def signal_groups_list_changed(self):
        ui = self.ui
        if not self.manual:
            choice = ui.groups_list.currentItem().text()
            group = self.projectinventory.get_group(choice)
            if group is not None:
                ui.hosts_list.clearSelection()
                self.helper_expand_tree(group.storage_dir)

            self.inv_target = choice
            self.inv_target_type = "group"

    def signal_send_file(self):
        """
        Must pick file from the tree view!
        """
        self.helper_input_setEnabled(False)
        dest = self.target_file_remote_path
        src = self.target_file_local_path

        play = PlayBuilder()
        play.hosts.append(self.inv_target)
        play.send(src, dest)
        self.ansible_run(play)

    def signal_fetch_file(self):
        # self.helper_input_setEnabled(False)
        ui = self.ui
        src = ui.target_file_lineedit.text()
        target_type = self.inv_target_type
        if target_type == "group":
            target_type = "groups"

        if self.inv_target == "all":
            return

        play = PlayBuilder()
        play.hosts.append(self.inv_target)
        dest = f"{self.files_path}/{target_type}/{self.inv_target}{src}"
        play.fetch(src, dest)
        self.ansible_run(play)

    def signal_ping(self):
        self.helper_input_setEnabled(False)
        play = PlayBuilder()
        play.host_pattern = self.inv_target
        play.module("ping")
        self.ansible_run(play)

    def signal_quick_systemd(self):
        # self.helper_input_setEnabled(False)
        ui = self.ui
        service_name = ui.quick_systemd_service.text()
        play = PlayBuilder()
        play.hosts.append(self.inv_target)
        match self.sender().objectName():
            case "button_service_start":
                play.service(service_name, "started")
            case "button_service_stop":
                play.service(service_name, "stopped")
            case "button_service_restart":
                play.service(service_name, "restarted", daemon_reload=True)
            case "button_service_status":
                play.shell(["systemctl status " + service_name])
        self.ansible_run(play)

    def signal_quick_shell(self):
        self.helper_input_setEnabled(False)
        ui = self.ui
        play = PlayBuilder()
        play.hosts.append(self.inv_target)
        commands = []
        text = ui.quickshell_1.text()
        if text:
            commands.append(text)
        text = ui.quickshell_2.text()
        if text:
            commands.append(text)
        text = ui.quickshell_3.text()
        if text:
            commands.append(text)
        play.shell(commands)
        self.ansible_run(play)

    def helper_expand_tree(self, item_path: str):
        ui = self.ui
        item_path = item_path.replace(f"{self.project.root_dir}/files", "")
        target_indexes = item_path.split("/")[1:]

        def recursive_expand(parent_index, target_indexes):
            if not target_indexes:
                return None  # No more indexes

            current_target = target_indexes[0]

            for row in range(ui.model.rowCount(parent_index)):
                index = ui.model.index(row, 0, parent_index)
                item_text = ui.model.data(index)

                # If match, expand.
                if item_text == current_target:
                    ui.tree.setExpanded(index, True)
                    if len(target_indexes) == 1:
                        return index  # Return the final index

                    # Recurse if there are more indexes
                    return recursive_expand(index, target_indexes[1:])
            return None

        ui.tree.collapseAll()
        final_index = recursive_expand(self.tree_root_index, target_indexes)

        if final_index:  # Highlight the selected item
            ui.tree.setCurrentIndex(final_index)
            ui.tree.scrollTo(final_index)

    def helper_append_console(self, msg: dict):
        ui = self.ui
        color_map = {
            "red": QColor(192, 57, 43),
            "green": QColor(39, 174, 96),
            "yellow": QColor(241, 196, 15),
            "purple": QColor(155, 89, 182),
            "cyan": QColor(93, 173, 226),
            "gray": QColor(149, 165, 166),
            "black": QColor(23, 32, 42),
        }
        color = color_map.get(msg["color"], QColor(0, 0, 0))

        weight_map = {
            "text": 400,
            "h1": 900,
            "h2": 650,
            "h3": 500,
        }

        charformat = QTextCharFormat()
        charformat.setForeground(color)
        charformat.setFontWeight(weight_map.get(msg["charformat"], 1))

        cursor = ui.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move the cursor to the end

        cursor.insertText(msg["text"], charformat)

        if not msg["skip_newline"]:
            cursor.insertText("\n")

        ui.console.ensureCursorVisible()

    def helper_input_setEnabled(self, toggle: bool):
        ui = self.ui
        ui.quickactions_files_buttons.setEnabled(toggle)
        ui.quickactions_systemd_buttons1.setEnabled(toggle)
        ui.quickactions_systemd_buttons2.setEnabled(toggle)
        ui.quickshell_run_button.setEnabled(toggle)
        ui.qaction_ping.setEnabled(toggle)

    def ansible_run(self, play: PlayBuilder):
        ui = self.ui
        worker = Worker(play, self.signals.message)
        worker.signals.finished.connect(self.ansible_complete)
        worker.signals.message.connect(self.helper_append_console)
        ui.progress_bar.setRange(0, 0)
        self.thread_pool.start(worker)

    def ansible_complete(self, success):
        if success:
            ui = self.ui
            ui.progress_bar.setRange(0, 100)
            ui.progress_bar.reset()
            self.helper_input_setEnabled(True)

    def populate_tree(self):
        ui = self.ui
        files_path = os.path.join(self.project.root_dir, "files")
        ui.model.setRootPath(files_path)
        ui.tree.setRootIndex(ui.model.index(files_path))
        self.tree_root_index = ui.model.index(files_path)
        self.files_path = files_path

    def populate_lists(self):
        ui = self.ui
        for group in self.groups:
            ui.groups_list.addItem(group.name)
        for host in self.hosts:
            ui.hosts_list.addItem(host.name)

    def dialog_importproject(self):
        dlg = ImportProjectDialog(self)
        if dlg.exec():
            projectname = dlg.project_name.text()
            projectdir = dlg.filepath_label.text()
            print(projectname, projectdir)
            msgBox = QMessageBox()
            if len(projectname) == 0:
                msgBox.setText("You neet to input a project name")
                msgBox.exec()
            elif len(projectdir) == 0:
                msgBox.setText("You need to select a project directory")
                msgBox.exec()
            # create_project(projectname, projectdir)
        else:
            pass

    def dialog_selectproject(self):
        dlg = SelectProjectDialog(self)

        if dlg.exec():
            selected_project = dlg.selected_project.currentText()
            if selected_project:
                ProjectData.selected_project = selected_project
                ProjectData.update_config()

    def window_inventory(self):
        if ProjectData.selected_project:
            self.invwindow = InventoryWindow()
            self.invwindow.show()
        else:
            msgBox = QMessageBox()
            msgBox.setText("A project must be selected to view the inventory.")
            msgBox.exec()


def gui_main():
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
