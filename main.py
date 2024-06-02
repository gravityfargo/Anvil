import sys, os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from cli.file_utils import YamlManager
from config.vars import AnvilData
from dialogs import SelectProjectDialog
from ansible_utils import playbook

from cli.file_utils import (
    YamlManager,
    initialize_new_project,
    import_existing_project,
    cprint,
    set_s_project,
    set_s_host,
    initial_setup,
    sync_configs_with_project_files,
)


class MainWindow(QMainWindow):
    def __init__(self, ad: AnvilData):
        super().__init__()
        self.ad = ad
        self.setWindowTitle("Directory Selector")

        # region Menu
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        open_action = QAction("Select a Project", self)
        open_action.triggered.connect(self.select_project_dialog)
        toolbar.addAction(open_action)
        # endregion

        main_layout = QHBoxLayout()

        # region LEFT SIDE
        left_layout = QVBoxLayout()
        self.project_label = QLabel("Current Project: ")
        self.project_name_label = QLabel(self.ad.s_project)
        left_layout.addWidget(self.project_label)
        left_layout.addWidget(self.project_name_label)

        self.model = QFileSystemModel()
        self.model.setRootPath(self.ad.sp_project_dir)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.ad.sp_project_dir))
        self.tree.setColumnWidth(0, 300)
        self.tree.clicked.connect(self.on_file_selected)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        left_layout.addWidget(self.tree)
        # endregion

        # region RIGHT SIDE
        right_layout = QVBoxLayout()
        self.form_groupbox_fetch = QGroupBox("Fetch from Server")
        self.fetch_form_setup()

        self.form_groupbox_send = QGroupBox("Send to Server")
        self.send_form_setup()

        right_layout.addWidget(self.form_groupbox_fetch)
        right_layout.addWidget(self.form_groupbox_send)
        # endregion

        # MAIN LAYOUT
        left_container = QWidget()
        left_container.setLayout(left_layout)
        right_container = QWidget()
        right_container.setLayout(right_layout)

        main_layout.addWidget(left_container)
        main_layout.addWidget(right_container)

        container = QWidget()
        container.setMinimumSize(800, 600)
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def ansible_fetch(self):
        set_s_host(self.ad, self.hosts_combobox_fetch.currentText())
        playbook(
            self.ad,
            "-rf",
            self.target_file_lineddit_fetch.text(),
            self.ad.s_group,
            self.ad.s_host,
        )

    def ansible_send(self):
        set_s_host(self.ad, self.hosts_combobox_fetch.currentText())
        playbook(
            self.ad,
            "-rs",
            self.target_file_lineddit_fetch.text(),
            self.ad.s_group,
            self.ad.s_host,
        )

    def fetch_form_setup(self):

        layout = QFormLayout()

        self.hosts_combobox_fetch = QComboBox()
        self.hosts_combobox_fetch.addItems(self.ad.sp_hosts)

        self.target_file_lineddit_fetch = QLineEdit()
        self.target_file_lineddit_fetch.setPlaceholderText("Target file path")

        layout.addRow(QLabel("Target File"), self.target_file_lineddit_fetch)
        layout.addRow(QLabel("Target Host"), self.hosts_combobox_fetch)

        go_button_fetch = QPushButton("Go")
        go_button_fetch.clicked.connect(self.ansible_fetch)
        layout.addWidget(go_button_fetch)

        self.form_groupbox_fetch.setLayout(layout)

    def send_form_setup(self):

        layout = QFormLayout()

        self.hosts_combobox_send = QComboBox()
        self.hosts_combobox_send.addItems(self.ad.sp_hosts)

        self.target_file_lineddit_send = QLineEdit()
        self.target_file_lineddit_send.setPlaceholderText("Target file path")

        layout.addRow(QLabel("Target File"), self.target_file_lineddit_send)
        layout.addRow(QLabel("Target Host"), self.hosts_combobox_send)

        go_button_send = QPushButton("Go")
        go_button_send.clicked.connect(self.ansible_send)
        layout.addWidget(go_button_send)

        self.form_groupbox_send.setLayout(layout)

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        exception_list = ["/ansible.cfg", "/inventory.yml", "/tree.yaml"]
        if os.path.isfile(file_path):
            file_info = parse_full_file_path(self.ad.sp_project_dir, file_path)
            print(file_info)
            if file_info is not None:
                index = self.hosts_combobox_send.findText(file_info["host"])

                if index >= 0:  # Make sure the item was found
                    self.hosts_combobox_send.setCurrentIndex(index)
                    self.hosts_combobox_fetch.setCurrentIndex(index)

                self.target_file_lineddit_fetch.setText(file_info["real_target"])
                self.target_file_lineddit_send.setText(file_info["real_target"])

    def select_project_dialog(self):
        dlg = SelectProjectDialog(self.ad, self)
        if dlg.exec():
            selection = dlg.projects_combo.currentText()
            self.ad = set_s_project(self.ad, selection)
            print(self.ad.sp_project_dir)
            self.update_directory_view()
        else:
            print("Cancel!")

    def update_directory_view(self):
        self.project_name_label.setText(self.ad.s_project)
        self.model.setRootPath(self.ad.sp_project_dir)
        self.tree.setRootIndex(self.model.index(self.ad.sp_project_dir))


def parse_full_file_path(project_path, file_path):
    cleaned_path = file_path.replace(project_path, "")
    parts = cleaned_path.split("/")
    if len(parts) < 3 or len(parts[0]) == 0:
        return None

    real_target = str(os.path.join("/", *parts[2:]))

    file_info = {
        "group": parts[0],
        "host": parts[1],
        "real_target": real_target,
    }
    return file_info


def gui_main(ad: AnvilData):
    app = QApplication(sys.argv)
    window = MainWindow(ad)
    window.show()
    sys.exit(app.exec())


# Run the application
if __name__ == "__main__":
    ad = AnvilData()
    gui_main(ad)
