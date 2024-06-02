import sys, subprocess, os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from cli.file_utils import YamlManager
from config.vars import AnvilData


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

        known_projects = ad.all_projects
        self.projects_combo = QComboBox()
        self.projects_combo.addItems(known_projects)

        formlayout.addRow(QLabel("Imported Projects"), self.projects_combo)
        formGroupBox.setLayout(formlayout)

        layout = QVBoxLayout()
        layout.addWidget(formGroupBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
