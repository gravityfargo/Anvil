import sys, subprocess, os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from cli.file_utils import YamlManager
from custom_textedit import CustomTextEdit

# subprocess.Popen('echo "Geeks 4 Geeks"', shell=True)
repo_path = os.path.dirname(__file__) + "/repo/"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Directory Selector")

        layout = QHBoxLayout()

        # self.button = QPushButton("Select Directory")
        # self.button.clicked.connect(self.select_directory)
        # layout.addWidget(self.button)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnWidth(0, 300)
        self.tree.clicked.connect(self.on_file_selected)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        layout.addWidget(self.tree)

        self.edit_area = CustomTextEdit()
        layout.addWidget(self.edit_area)

        container = QWidget()
        container.setMinimumSize(800, 600)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.edit_area.setText(content)
        else:
            self.edit_area.clear()

    def select_directory(self):
        initial_path = "/path/to/initial/directory"  # Replace with your preferred starting directory path

        # Opens a dialog to select a directory, starting from the initial path
        directory = QFileDialog.getExistingDirectory(
            self, "Select a Directory", initial_path
        )
        if directory:
            print(f"Selected directory: {directory}")
            # You can add additional code here to handle the selected directory


app = QApplication(sys.argv)
window = MainWindow()


menu = window.menuBar().addMenu("&File")


def syncTree():
    treetext = YamlManager("repo/tree.yaml").get_all()


sync_tree = QAction("&Sync Tree")
sync_tree.triggered.connect(syncTree)
menu.addAction(sync_tree)


window.show()
app.exec()
