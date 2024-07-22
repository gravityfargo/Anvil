from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
)
from core.classes import AnvilData


class ImportProjectDialog(QDialog):
    def __init__(self, ad: AnvilData, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anvil")
        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        formGroupBox = QGroupBox()
        formlayout = QFormLayout()

        self.project_name_lineedit = QLineEdit()
        self.project_name_lineedit.setPlaceholderText("Enter Name")

        self.button_dir = QPushButton("Select Directory")
        self.button_dir.clicked.connect(self.file_dialog)

        self.file_path_label = QLabel("")

        formlayout.addRow(QLabel("Projectr Name Projects"), self.project_name_lineedit)
        formlayout.addRow(QLabel("Project Directory"), self.button_dir)
        formGroupBox.setLayout(formlayout)

        layout = QVBoxLayout()
        layout.addWidget(formGroupBox)
        layout.addWidget(self.file_path_label)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def file_dialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        fileNames = ""
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            self.file_path_label.setText(fileNames[0])
        return fileNames


class SelectProjectDialog(QDialog):
    def __init__(self, ad: AnvilData, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anvil")
        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        formGroupBox = QGroupBox()
        formlayout = QFormLayout()

        known_projects = ad.projects
        self.projects_combo = QComboBox()
        self.projects_combo.addItems(known_projects)

        formlayout.addRow(QLabel("Imported Projects"), self.projects_combo)
        formGroupBox.setLayout(formlayout)

        layout = QVBoxLayout()
        layout.addWidget(formGroupBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
