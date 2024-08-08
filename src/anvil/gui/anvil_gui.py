import click
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QMainWindow, QWidget, QApplication
import qdarktheme
from .create_components import *
from .gui_sections import *
from anvil.config import AnvilOptions


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        qdarktheme.setup_theme("light")
        self.thread_pool = QThreadPool()
        self.setWindowTitle("Anvil")

        top_layout = create_QHBoxLayout("top_layout")
        bottom_layout = create_QVBoxLayout("bottom_layout")

        section_one = create_QVBoxLayout("section_one")
        section_two = create_QVBoxLayout("section_two")

        self.setup_section_one(section_one)
        self.setup_section_two(section_two)
        self.setup_quick_actions_tab()
        self.setup_file_tab()
        self.setup_shell_tab()
        self.setup_systemd_tab()
        self.setup_ufw_tab()

        section_three = create_QVBoxLayout("section_three")
        self.setup_section_three(section_three)

        self.setup_menubar()

        top_layout.addLayout(section_one)
        top_layout.addLayout(section_two)
        top_layout.addLayout(section_three)

        main_container = QWidget()
        main_container.setMinimumWidth(900)
        window_layout = QVBoxLayout(main_container)
        window_layout.addLayout(top_layout)

        self.setCentralWidget(main_container)
        # self.showMaximized()

        # combobox.currentIndexChanged.connect(
        #     self.parent_obj.signal_combobox_index_changed
        # )

    def setup_section_one(self, target_layout: QLayout):
        groupbox, layout = create_QGroupBox("invtarget", "Inventory Target")
        # self.ad.s_project["groups_list"]
        # self.ad.s_project["hosts_list"]
        hosts = create_QComboBox("hosts")
        groups = create_QComboBox("groups")
        items = [("Groups", groups), ("Hosts", hosts)]
        add_Rows(layout, items)
        target_layout.addWidget(groupbox)

        tree, model = create_QTreeView("file_tree")
        # tree.clicked.connect(self.on_file_selected)
        target_layout.addWidget(tree)

        self.invtarget_groupbox = groupbox
        self.invtarget_groupbox_layout = layout
        self.invtarget_hosts = hosts
        self.invtarget_groups = groups
        self.file_tree = tree
        self.file_tree_model = model

    def setup_section_two(self, target_layout: QLayout):
        section_two_tabs = create_QTabWidget("section_two_tabs")
        section_two_tabs.setMinimumWidth(450)
        target_layout.addWidget(section_two_tabs)
        self.section_two_tabs = section_two_tabs

        widget, layout = create_QWidget("quick_actions_tab", QVBoxLayout)
        section_two_tabs.addTab(widget, "Quick Actions")
        self.quick_actions_tab = widget
        self.quick_actions_tab_layout = layout

        groupbox, layout = create_QWidget("file_tab", QVBoxLayout)
        section_two_tabs.addTab(groupbox, "File")
        self.file_tab_groupbox = groupbox
        self.file_tab_layout = layout

        groupbox, layout = create_QWidget("shell_tab", QVBoxLayout)
        section_two_tabs.addTab(groupbox, "Shell")
        self.shell_tab_groupbox = groupbox
        self.shell_tab_layout = layout

        groupbox, layout = create_QWidget("systemd_tab", QVBoxLayout)
        section_two_tabs.addTab(groupbox, "Systemd")
        self.systemd_tab_groupbox = groupbox
        self.systemd_tab_layout = layout

        groupbox, layout = create_QWidget("ufw_tab", QVBoxLayout)
        section_two_tabs.addTab(groupbox, "UFW")
        self.ufw_tab_groupbox = groupbox
        self.ufw_tab_layout = layout

    def setup_section_three(self, target_layout: QLayout):
        self.console_textedit = QTextEdit()
        self.console_textedit.setMinimumWidth(400)
        self.console_textedit.setReadOnly(True)
        target_layout.addWidget(self.console_textedit)

    def setup_quick_actions_tab(self):
        target_layout = self.quick_actions_tab_layout
        # Send / Fetch Files
        self.quick_files_groupbox = setup_quick_files_groupbox()
        target_layout.addWidget(self.quick_files_groupbox)

        # Send Commands
        self.quick_shell_groupbox = setup_quick_shell_groupbox()
        target_layout.addWidget(self.quick_shell_groupbox)

        # Systemd
        self.quick_systemd_groupbox = setup_quick_systemd_groupbox()
        target_layout.addWidget(self.quick_systemd_groupbox)

    def setup_file_tab(self):
        target_layout = self.file_tab_layout
        pass

    def setup_shell_tab(self):
        target_layout = self.shell_tab_layout
        pass

    def setup_systemd_tab(self):
        target_layout = self.systemd_tab_layout
        pass

    def setup_ufw_tab(self):
        target_layout = self.ufw_tab_layout
        pass

    def setup_menubar(self):
        menu = self.menuBar()
        prj_menu = menu.addMenu("Project Settings")
        dbg_menu = menu.addMenu("Debug")

        # create_QAction(prj_menu, "Import a Project", self.import_project_dialog)
        # create_QAction(prj_menu, "Change Project", self.change_project_dialog)


@click.command(name="gui", help="Launch the Anvil GUI.")
def gui_main():
    # app = QApplication()
    # window = MainWindow()
    # window.show()
    # app.exec_()
    from anvil.helpers.data_helper import import_project

    import_project("Peddle", "/home/nathan/Development/trash/Peddle")
