import qdarktheme
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QLayout, QMainWindow, QMessageBox

from anvil.config import ProjectData

from .create_components import (
    create_QAction,
    create_QComboBox,
    create_QGroupBox,
    create_QHBoxLayout,
    create_QTabWidget,
    create_QTreeView,
    create_QVBoxLayout,
)
from .dialogs import ImportProjectDialog, SelectProjectDialog
from .inventorywindow import InventoryWindow
from .mainwindow_gui import setup_quickactions_tab


class MainWindow(QMainWindow):
    invwindow: InventoryWindow

    def __init__(self):
        super().__init__()
        qdarktheme.setup_theme("light")
        self.thread_pool = QThreadPool()
        self.setWindowTitle("Anvil")

        mainlayout = create_QHBoxLayout("mainlayout")
        self.setMinimumWidth(900)
        self.setLayout(mainlayout)

        sectionone_layout = create_QVBoxLayout("section_one")
        sectiontwo_layout = create_QVBoxLayout("section_two")
        mainlayout.addLayout(sectionone_layout)
        mainlayout.addLayout(sectiontwo_layout)

        self.setup_section_one(sectionone_layout)
        self.setup_section_two(sectiontwo_layout)
        self.setup_menubar()

        self.project = None
        if ProjectData.selected_project:
            self.project = ProjectData.get_project(ProjectData.selected_project)

    def setup_section_one(self, parent_layout: QLayout):

        groupbox, layout = create_QGroupBox("invtarget", "Inventory Target")
        parent_layout.addWidget(groupbox)

        hosts = create_QComboBox("hosts", [])
        groups = create_QComboBox("groups", [])
        layout.addRow("Hosts", hosts)
        layout.addRow("Groups", groups)

        tree, model = create_QTreeView("file_tree")
        # tree.clicked.connect(self.on_file_selected)
        parent_layout.addWidget(tree)

        self.invtarget_groupbox = groupbox
        self.invtarget_groupbox_layout = layout
        self.hosts_combo = hosts
        self.groups_combo = groups
        self.file_tree = tree
        self.file_tree_model = model

    def setup_section_two(self, target_layout: QLayout):
        section_two_tabs = create_QTabWidget("section_two_tabs", 450)
        target_layout.addWidget(section_two_tabs)

        setup_quickactions_tab(section_two_tabs)
        # setup_files_tab(section_two_tabs)

    def setup_menubar(self):
        menu = self.menuBar()
        create_QAction(self, menu, "Import Project", self.importproject_dialog)
        create_QAction(self, menu, "Select Project", self.selectproject_dialog)
        create_QAction(self, menu, "Inventory", self.inventory_window)

    def importproject_dialog(self):
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

    def selectproject_dialog(self):
        dlg = SelectProjectDialog(self)

        if dlg.exec():
            selected_project = dlg.selected_project.currentText()
            if selected_project:
                ProjectData.selected_project = selected_project
                ProjectData.update_config()

    def inventory_window(self):
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
    # window.show()
    window.inventory_window()
    app.exec()
