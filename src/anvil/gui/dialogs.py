from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox as QDB
from PySide6.QtWidgets import QVBoxLayout

from anvil.config import ProjectData

from .create_components import (
    create_QComboBox,
    create_QFileDialog,
    create_QGroupBox,
    create_QLabel,
    create_QLineEdit,
    create_QPushButton,
)


class ImportProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anvil")

        self.gb, self.gbl = create_QGroupBox("import_project", "Import Project")

        self.project_name = create_QLineEdit("project_name")
        self.gbl.addRow("Project Name", self.project_name)

        self.filepath_label = create_QLabel("File Path")
        self.gbl.addRow(self.filepath_label)

        directory_btn = create_QPushButton("dir", "Select Directory")
        directory_btn.clicked.connect(self.get_directory)

        self.gbl.addRow(directory_btn)

        QBtn = QDB.StandardButton.Ok | QDB.StandardButton.Cancel
        buttonBox = QDB(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.gbl.addWidget(buttonBox)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.gb)

        self.setLayout(main_layout)

    def get_directory(self) -> None:
        dlg = create_QFileDialog(directory_mode=True)
        data: list[str] = []
        if dlg.exec_():
            data = dlg.selectedFiles()
            self.filepath_label.setText(data[0])


class SelectProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose a Project")
        main_layout = QVBoxLayout()

        groupbox, glayout = create_QGroupBox("select_project", "Make a selection")
        groupbox.setFlat(True)
        groupbox.setMinimumWidth(400)

        QBtn = QDB.StandardButton.Ok | QDB.StandardButton.Cancel
        buttonBox = QDB(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        projects = create_QComboBox("projects", ProjectData.project_list)
        glayout.addRow("Projects", projects)
        main_layout.addWidget(groupbox)
        main_layout.addWidget(buttonBox)
        self.selected_project = projects

        self.setLayout(main_layout)
