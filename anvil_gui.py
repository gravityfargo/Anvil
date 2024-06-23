import sys, os, json
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QProgressBar,
    QTextEdit,
    QTreeView,
    QFileSystemModel,
    QFileDialog,
    QDialog,
    QLabel,
    QDialogButtonBox,
    QListWidget,
    QHBoxLayout,
    QMessageBox,
    QMainWindow,
    QWidget,
    QSpacerItem,
    QApplication,
    QSizePolicy,
)
from PySide6.QtGui import QTextCharFormat, QTextCursor, QColor, QAction
from config.vars import AnvilData
from dialogs import ImportProjectDialog, SelectProjectDialog
from core.ansible import playbook
from core.worker import Worker
from core.file_utils import (
    sync_project_with_file_system,
    import_existing_project,
    set_s_project,
    sync_tree_with_file_system,
)
from core.helpers import YamlManager


element_names = [
    "target_combobox_groups",
    "target_combobox_hosts",
    "playbookctl_button_run_playbook",
    "file_lineedit_target",
    "file_button_fetch",
    "file_button_send",
    "file_button_link_service",
    "service_lineedit_service_name",
    "service_button_restart",
    "service_button_stop",
    "service_button_start",
]


class MainWindow(QMainWindow):
    def __init__(self, ad: AnvilData):
        super().__init__()
        # region Setup

        # for element in element_names:
        #     setattr(self, element, None)
        self.ad = ad
        self.manual_change = True
        self.thread_pool = QThreadPool()
        self.setWindowTitle("Anvil")
        # endregion

        # region Plays and Browser
        action_buttons_layout = QVBoxLayout()
        self.action_buttons_groupbox = QGroupBox("Bulk Actions")
        self.action_buttons_setup()
        action_buttons_layout.addWidget(self.action_buttons_groupbox)

        browser_layout = QVBoxLayout()
        self.browser_container = QWidget()
        self.widget_setup(self.browser_container, "filetree")
        browser_layout.addWidget(self.browser_container)
        # endregion

        # region Primary Controls
        control_layout = QVBoxLayout()
        self.target_groupbox = QGroupBox("Target")
        self.playbookctl_groupbox = QGroupBox("Playbook Control")
        self.file_groupbox = QGroupBox("File")
        self.service_groupbox = QGroupBox("Service")

        self.form_setup(self.target_groupbox, "target")
        self.form_setup(self.playbookctl_groupbox, "playbookctl")
        self.form_setup(self.file_groupbox, "file")
        self.form_setup(self.service_groupbox, "service")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumHeight(20)

        control_layout.addWidget(self.target_groupbox)
        self.playbookctl_groupbox.setHidden(True)
        control_layout.addWidget(self.playbookctl_groupbox)
        self.create_v_spacer(control_layout)
        control_layout.addWidget(self.file_groupbox)
        control_layout.addWidget(self.service_groupbox)
        control_layout.addWidget(self.progress_bar)
        # endregion

        # region Actions Section
        self.actions_layout = QVBoxLayout()
        self.actions_groupbox = QGroupBox()
        self.actions_layout.addWidget(self.actions_groupbox)

        self.console_textedit = QTextEdit()
        self.actions_layout.addWidget(self.console_textedit)
        self.console_textedit.setMinimumWidth(350)
        self.console_textedit.setReadOnly(True)
        # endregion

        # region Populate Main Layout
        plays_container = QWidget()  # play buttons
        browser_container = QWidget()  # file browser / tree
        self.control_container = QWidget()
        actions_container = QWidget()

        plays_container.setLayout(action_buttons_layout)
        browser_container.setLayout(browser_layout)
        self.control_container.setLayout(control_layout)
        actions_container.setLayout(self.actions_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(plays_container)
        main_layout.addWidget(browser_container)
        main_layout.addWidget(self.control_container)
        main_layout.addWidget(actions_container)

        plays_container.setMaximumWidth(150)
        browser_container.setMaximumWidth(300)
        self.control_container.setMaximumWidth(300)

        main_container = QWidget()
        main_container.setMinimumSize(800, 600)
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        if self.ad.s_project is None:
            self.disable_elements(True)

        self.createMenuBar()
        # endregion

    # region GUI Definitions
    def createMenuBar(self):
        menuBar = self.menuBar()

        project_menu = menuBar.addMenu("Project")

        import_project = QAction("Import a Project", self)
        select_project = QAction("Select a Project", self)
        select_playbook_directory = QAction("Select Playbook Directory", self)
        import_project.triggered.connect(self.import_project_dialog)
        select_project.triggered.connect(self.select_project_dialog)
        select_playbook_directory.triggered.connect(self.select_playbook_directory)
        project_menu.addAction(import_project)
        project_menu.addAction(select_project)
        project_menu.addAction(select_playbook_directory)

        sync_tree = QAction("Sync Tree", self)
        sync_tree.triggered.connect(self.sync_tree)
        menuBar.addAction(sync_tree)

        debug_menu = menuBar.addMenu("Debug")

        debug_file_send = QAction("File Send", self)
        debug_file_fetch = QAction("File Fetch", self)
        debug_service_restart = QAction("Service Restart", self)
        debug_service_start = QAction("Service Start", self)
        debug_service_stop = QAction("Service Stop", self)
        debug_files = QAction("Files", self)
        debug_apt = QAction("Apt", self)
        debug_ufw = QAction("UFW", self)
        debug_shell_run = QAction("Shell", self)
        debug_link_service = QAction("Link Service", self)

        debug_file_send.setObjectName("file_button_send")
        debug_file_fetch.setObjectName("file_button_fetch")
        debug_service_restart.setObjectName("service_button_restart")
        debug_service_start.setObjectName("service_button_start")
        debug_service_stop.setObjectName("service_button_stop")
        debug_files.setObjectName("playfile_button_create")
        debug_apt.setObjectName("playapt_button_install")
        debug_ufw.setObjectName("playufw_button_allow")
        debug_shell_run.setObjectName("playshell_button_run")
        debug_link_service.setObjectName("file_button_link_service")

        debug_file_send.triggered.connect(self.debug_button)
        debug_file_fetch.triggered.connect(self.debug_button)
        debug_service_restart.triggered.connect(self.debug_button)
        debug_service_start.triggered.connect(self.debug_button)
        debug_service_stop.triggered.connect(self.debug_button)
        debug_files.triggered.connect(self.debug_button)
        debug_apt.triggered.connect(self.debug_button)
        debug_ufw.triggered.connect(self.debug_button)
        debug_shell_run.triggered.connect(self.debug_button)
        debug_link_service.triggered.connect(self.debug_button)

        debug_menu.addAction(debug_file_send)
        debug_menu.addAction(debug_file_fetch)
        debug_menu.addAction(debug_service_restart)
        debug_menu.addAction(debug_service_start)
        debug_menu.addAction(debug_service_stop)
        debug_menu.addAction(debug_files)
        debug_menu.addAction(debug_apt)
        debug_menu.addAction(debug_ufw)
        debug_menu.addAction(debug_shell_run)
        menuBar.addAction(debug_link_service)

    def action_buttons_setup(self):
        layout = QVBoxLayout()
        self.action_button_file = QPushButton("File")
        self.action_button_file.setObjectName("action_button_file")
        self.action_button_file.clicked.connect(self.action_buttons_intermediate)

        self.action_button_copy = QPushButton("Copy")
        self.action_button_copy.setObjectName("action_button_copy")
        self.action_button_copy.clicked.connect(self.action_buttons_intermediate)

        self.action_button_apt = QPushButton("Apt")
        self.action_button_apt.setObjectName("action_button_apt")
        self.action_button_apt.clicked.connect(self.action_buttons_intermediate)

        self.action_button_ufw = QPushButton("UFW")
        self.action_button_ufw.setObjectName("action_button_ufw")
        self.action_button_ufw.clicked.connect(self.action_buttons_intermediate)

        self.action_button_shell = QPushButton("Shell")
        self.action_button_shell.setObjectName("action_button_shell")
        self.action_button_shell.clicked.connect(self.action_buttons_intermediate)

        self.action_button_variables = QPushButton("Variables")
        self.action_button_variables.setObjectName("action_button_variables")
        self.action_button_variables.clicked.connect(self.action_buttons_intermediate)

        self.action_button_playbooks = QPushButton("Playbooks")
        self.action_button_playbooks.setObjectName("action_button_playbooks")
        self.action_button_playbooks.clicked.connect(self.action_buttons_intermediate)

        self.action_button_configs = QPushButton("Config Files")
        self.action_button_configs.setObjectName("action_button_configs")
        self.action_button_configs.clicked.connect(self.action_buttons_intermediate)

        layout.addWidget(self.action_button_file)
        layout.addWidget(self.action_button_copy)
        layout.addWidget(self.action_button_apt)
        layout.addWidget(self.action_button_ufw)
        layout.addWidget(self.action_button_shell)
        self.create_v_spacer(layout)
        layout.addWidget(self.action_button_configs)
        layout.addWidget(self.action_button_variables)
        layout.addWidget(self.action_button_playbooks)

        self.action_buttons_groupbox.setLayout(layout)

    def form_setup(self, parent: QGroupBox, name: str):
        layout = QVBoxLayout()
        layout.setObjectName(f"{name}_layout")

        form_container = QWidget()
        form_layout = QFormLayout()
        form_container.setLayout(form_layout)

        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)

        if parent.layout() is not None:
            layout = parent.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        if name == "target":
            self.create_combobox(form_layout, name, "Groups")
            self.create_combobox(form_layout, name, "Hosts")
        elif name == "file":
            self.create_lineedit(form_layout, name, "Target", "/etc/hosts")
            self.create_button(button_layout, name, "Fetch")
            self.create_button(button_layout, name, "Send")
            self.create_button(button_layout, name, "Link Service")
        elif name == "service":
            self.create_lineedit(form_layout, name, "Service Name", "rsyslog")
            self.create_button(button_layout, name, "Restart")
            self.create_button(button_layout, name, "Stop")
            self.create_button(button_layout, name, "Start")
        elif name == "playfile":
            parent.setTitle("ansible.builtin.file")
            self.create_combobox(form_layout, name, "Directory Vars", [])
            self.create_combobox(form_layout, name, "File Vars", [])
            self.create_combobox(form_layout, name, "State", [])
            self.create_lineedit(form_layout, name, "Path", "/etc/hosts")
            self.create_lineedit(form_layout, name, "Owner", "root")
            self.create_lineedit(form_layout, name, "Group", "root")
            self.create_lineedit(form_layout, name, "Mode", "0744")
            self.create_button(button_layout, name, "Create")
            self.create_button(button_layout, name, "Delete")
            self.create_button(button_layout, name, "Change Permissions")
        elif name == "playapt":
            parent.setTitle("ansible.builtin.apt")
            package_vars = []
            for i in self.ad.vars.keys():
                if i.endswith("_packages"):
                    package_vars.append(i)
            self.create_combobox(form_layout, name, "Apt Vars", package_vars)
            self.create_lineedit(form_layout, name, "Package", "nginx")
            self.create_checkbox(form_layout, name, "Update")

            self.create_button(button_layout, name, "Install")
            self.create_button(button_layout, name, "Remove")
        elif name == "playufw":
            parent.setTitle("ansible.builtin.ufw")
            rule_vars = []
            for i in self.ad.vars.keys():
                if i.endswith("_firewall_rules"):
                    rule_vars.append(i)
            self.create_combobox(form_layout, name, "Rule Vars", rule_vars)
            self.create_lineedit(form_layout, name, "Port", "22")
            self.create_lineedit(form_layout, name, "Comment", "OpenSSH")

            self.create_button(button_layout, name, "Allow")
            self.create_button(button_layout, name, "Deny")
        elif name == "playshell":
            parent.setTitle("ansible.builtin.shell")
            self.create_lineedit(form_layout, name, "Command1", "echo 'Hello World'")
            self.create_lineedit(form_layout, name, "Command2", "")
            self.create_lineedit(form_layout, name, "Command3", "")

            self.create_button(button_layout, name, "Run")
        elif name == "variables":
            parent.setTitle("Variables")
            varlist = self.ad.vars.keys()
            self.create_combobox(form_layout, name, "Variables", varlist)
        elif name == "varedit":
            parent.setTitle("Variable Editor")
            self.create_button(button_layout, name, "Save")
            self.create_button(button_layout, name, "Reset")
        elif name == "playbookctl":
            self.create_button(button_layout, name, "Run Playbook")
        elif name == "linkservice":
            self.create_lineedit(form_layout, name, "Service Name", "rsyslog")
            self.create_button(button_layout, name, "Link")
        elif name == "playcopy":
            parent.setTitle("ansible.builtin.copy")
            copy_vars = []
            for i in self.ad.vars.keys():
                if i.endswith("_config_files"):
                    copy_vars.append(i)
            self.create_combobox(form_layout, name, "File Vars", copy_vars)
            self.create_lineedit(form_layout, name, "Source", "/etc/hosts")
            self.create_lineedit(form_layout, name, "Destination", "/etc/hosts")
            self.create_lineedit(form_layout, name, "Owner", "root")
            self.create_lineedit(form_layout, name, "Group", "root")
            self.create_lineedit(form_layout, name, "Mode", "0744")

            self.create_button(button_layout, name, "Copy")
        if len(form_container.children()) > 1:
            layout.addWidget(form_container)
            self.children_to_attr(form_container)
        if len(button_container.children()) > 1:
            layout.addWidget(button_container)
            self.children_to_attr(button_container)
        parent.setLayout(layout)

    def widget_setup(self, parent: QWidget, name: str):
        layout = QVBoxLayout()
        layout.setObjectName(f"{name}_layout")

        if parent.layout() is not None:
            layout = parent.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        if name == "filetree":
            self.model = QFileSystemModel()
            self.model.setRootPath(self.ad.s_project["path"])

            self.tree = QTreeView()
            self.tree.setModel(self.model)
            self.tree.setRootIndex(self.model.index(self.ad.s_project["path"]))
            self.tree.setColumnWidth(0, 300)

            self.tree.clicked.connect(self.on_file_selected)
            self.tree.hideColumn(1)
            self.tree.hideColumn(2)
            self.tree.hideColumn(3)
            layout.addWidget(self.tree)
        elif name == "variables":
            self.varlist = QListWidget()
            self.varlist.addItems(self.ad.vars.keys())
            self.varlist.sortItems()
            self.varlist.clicked.connect(self.on_config_selected)
            layout.addWidget(self.varlist)
        elif name == "playbooks":
            self.playbooklist = QListWidget()
            for i in os.listdir(self.ad.sp_playbooks_directory):
                if i.endswith(".yml"):
                    self.playbooklist.addItem(i[:-4])
            self.playbooklist.sortItems()
            layout.addWidget(self.playbooklist)

        parent.setLayout(layout)

    # endregion

    # region GUI Creation
    def create_checkbox(self, layout: QVBoxLayout, name: str, desciption: str):
        checkbox = QCheckBox(desciption)
        suffix = desciption.lower().replace(" ", "_")
        checkbox.setObjectName(f"{name}_checkbox_{suffix}")
        layout.addWidget(checkbox)

    def create_v_spacer(self, layout: QVBoxLayout):
        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        layout.addSpacerItem(spacer)

    def create_button(
        self, layout: QHBoxLayout | QVBoxLayout, name: str, desciption: str
    ):
        button = QPushButton(desciption)
        suffix = desciption.lower().replace(" ", "_")
        button.setObjectName(f"{name}_button_{suffix}")
        button.clicked.connect(self.ansible_execute)
        layout.addWidget(button)

    def create_lineedit(self, layout: QFormLayout, name: str, desciption: str, ph: str):
        lineedit = QLineEdit()
        suffix = desciption.lower().replace(" ", "_")
        lineedit.setObjectName(f"{name}_lineedit_{suffix}")
        lineedit.setPlaceholderText(ph)
        layout.addRow(QLabel(desciption), lineedit)

    def create_combobox(
        self, layout: QFormLayout, name: str, desciption: str, options=[]
    ):
        combobox = QComboBox()
        suffix = desciption.lower().replace(" ", "_")
        combobox.setObjectName(f"{name}_combobox_{suffix}")
        if len(options) > 0:
            combobox.addItems(options)
        elif desciption == "Hosts":
            if self.ad.s_project["hosts_list"] is not None:
                combobox.addItems(self.ad.s_project["hosts_list"])
        elif desciption == "Groups":
            if self.ad.s_project["groups_list"] is not None:
                combobox.addItems(self.ad.s_project["groups_list"])
        combobox.addItem("")
        combobox.setCurrentIndex(-1)
        combobox.currentIndexChanged.connect(self.comboboxes_changed)
        layout.addRow(QLabel(desciption), combobox)

    # endregion

    # region Signal Handling
    def action_buttons_intermediate(self):
        sender = self.sender().objectName()
        self.control_container.setHidden(False)
        self.console_textedit.setReadOnly(True)
        self.playbookctl_groupbox.setHidden(True)
        self.console_textedit.clear()
        if sender == "action_button_file":
            self.form_setup(self.actions_groupbox, "playfile")
        elif sender == "action_button_copy":
            self.form_setup(self.actions_groupbox, "playcopy")
        elif sender == "action_button_apt":
            self.form_setup(self.actions_groupbox, "playapt")
        elif sender == "action_button_ufw":
            self.form_setup(self.actions_groupbox, "playufw")
        elif sender == "action_button_shell":
            self.form_setup(self.actions_groupbox, "playshell")
        elif sender == "action_button_variables":
            self.control_container.setHidden(True)
            self.form_setup(self.actions_groupbox, "varedit")
            self.console_textedit.setReadOnly(False)
            self.widget_setup(self.browser_container, "variables")
        elif sender == "action_button_configs":
            self.widget_setup(self.browser_container, "filetree")
        elif sender == "action_button_playbooks":
            self.playbookctl_groupbox.setHidden(False)
            self.widget_setup(self.browser_container, "playbooks")

        # self.get_children(self.actions_layout)

    def on_file_selected(self, index):
        self.selected_file_path = self.model.filePath(index)
        exception_list = [
            f"{self.ad.s_project['path']}/ansible.cfg",
            f"{self.ad.s_project['path']}/inventory.yml",
            f"{self.ad.s_project['path']}/tree.yaml",
        ]
        if os.path.isfile(self.selected_file_path):
            if self.selected_file_path in exception_list:
                return
            file_info = self.parse_full_file_path(
                self.ad.s_project["path"], self.selected_file_path
            )
            if file_info is None:
                return
            hostcombo = self.target_combobox_hosts
            groupcombo = self.target_combobox_groups
            self.manual_change = False
            groupcombo.setCurrentIndex(groupcombo.findText(file_info["group"]))

            relative_path = self.selected_file_path.replace(
                self.ad.s_project["path"], ""
            )[1:]
            file_attributes = YamlManager(self.ad.s_project["tree_file"]).get_item(
                relative_path
            )

            if file_attributes.get("service") is not None:
                self.service_lineedit_service_name.setText(file_attributes["service"])
            else:
                self.service_lineedit_service_name.setText("")

            if "all" in file_info["group"]:
                hostcombo.setCurrentIndex(-1)
            else:
                hostcombo.setCurrentIndex(hostcombo.findText(file_info["host"]))
            self.file_lineedit_target.setText(file_info["real_target"])
            self.manual_change = True

    def on_config_selected(self, index):
        self.console_textedit.clear()
        self.console_textedit.setTabStopDistance(24)
        var_data = json.dumps(self.ad.vars[index.data()], indent=8)
        self.console_text(var_data, "black")

    def comboboxes_changed(self):
        sender_name = self.sender().objectName()

        if self.manual_change:
            self.manual_change = False
            choice = self.sender().currentText()

            match sender_name:
                case "target_combobox_groups":
                    self.target_combobox_hosts.setCurrentIndex(-1)
                    self.tree.collapseAll()
                    self.expand_tree(choice)

                    childrenlist = self.get_children(self.actions_layout)
                    if len(childrenlist) > 0:
                        prefix = childrenlist[0].split("_")[0]
                        self.populate_play_fields_comboboxs(prefix)

                case "target_combobox_hosts":
                    if choice != "":
                        group = self.ad.s_project["hosts"][choice]["group"]
                    else:
                        group = None
                    self.tree.collapseAll()
                    if group is None:
                        self.target_combobox_hosts.setCurrentIndex(-1)
                        self.target_combobox_groups.setCurrentIndex(-1)
                    else:
                        gi = self.target_combobox_groups.findText(group)
                        self.target_combobox_groups.setCurrentIndex(gi)
                        self.expand_tree(self.target_combobox_groups.currentText())
                        self.expand_tree(self.target_combobox_hosts.currentText())
                case "playfile_combobox_file_vars":
                    self.modify_child(
                        "playfile_combobox_state", QComboBox, "setindex", -1
                    )
                    self.modify_child(
                        "playfile_combobox_directory_vars", QComboBox, "setindex", -1
                    )
                    self.playfile_lineedit_path.setDisabled(True)
                    self.modify_child("playfile_lineedit_owner", QLineEdit, "disable")
                    self.modify_child("playfile_lineedit_group", QLineEdit, "disable")
                    self.modify_child("playfile_lineedit_mode", QLineEdit, "disable")
                case "playfile_combobox_directory_vars":
                    self.modify_child(
                        "playfile_combobox_file_vars", QComboBox, "setindex", -1
                    )
                    self.modify_child(
                        "playfile_combobox_state", QComboBox, "setindex", -1
                    )
                    self.playfile_lineedit_path.setDisabled(True)
                    self.modify_child("playfile_lineedit_owner", QLineEdit, "disable")
                    self.modify_child("playfile_lineedit_group", QLineEdit, "disable")
                    self.modify_child("playfile_lineedit_mode", QLineEdit, "disable")
                case "playfile_combobox_state":
                    self.modify_child(
                        "playfile_combobox_file_vars", QComboBox, "setindex", -1
                    )
                    self.modify_child(
                        "playfile_combobox_directory_vars", QComboBox, "setindex", -1
                    )
                    self.playfile_lineedit_path.setDisabled(False)
                    self.modify_child("playfile_lineedit_owner", QLineEdit, "enable")
                    self.modify_child("playfile_lineedit_group", QLineEdit, "enable")
                    self.modify_child("playfile_lineedit_mode", QLineEdit, "enable")
            self.manual_change = True

    # endregion

    # region Dialogs
    def import_project_dialog(self):
        dlg = ImportProjectDialog(self.ad, self)
        if dlg.exec():
            projectname = dlg.project_name_lineedit.text()
            projectdir = dlg.file_path_label.text()
            msgBox = QMessageBox()
            if len(projectname) == 0:
                msgBox.setText("You neet to input a project name")
                msgBox.exec()
                return
            elif len(projectdir) == 0:
                msgBox.setText("You need to select a project directory")
                msgBox.exec()
                return
            import_existing_project(self.ad, projectname, projectdir)
        else:
            pass

    def select_project_dialog(self):
        dlg = SelectProjectDialog(self.ad, self)
        if dlg.exec():
            selection = dlg.projects_combo.currentText()
            self.ad = set_s_project(self.ad, selection)
            self.update_gui()

    def sync_tree(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Syncing")
        layout = QVBoxLayout()
        label = QLabel("Really sync?")
        layout.addWidget(label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        if dlg.exec():
            sync_tree_with_file_system(self.ad)
            self.model.setRootPath(self.ad.s_project["path"])
            self.tree.setRootIndex(self.model.index(self.ad.s_project["path"]))

    def select_playbook_directory(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        if dlg.exec():
            self.ad.sp_playbooks_directory = dlg.selectedFiles()[0]
            sync_project_with_file_system(self.ad)

    def simplge_message(self, message):
        msgBox = QMessageBox()
        msgBox.setText(message)
        msgBox.exec()

    def link_service(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Link Service")
        layout = QVBoxLayout()
        linkservice_groupbox = QGroupBox()
        self.form_setup(linkservice_groupbox, "linkservice")
        button = self.linkservice_button_link
        servicename = self.service_lineedit_service_name.text()
        button.clicked.connect(dlg.accept)

        file_path = self.file_lineedit_target.text()

        self.console_text(f"Linking {servicename} to {file_path}", "black")
        if servicename == "":

            layout.addWidget(linkservice_groupbox)
            dlg.setLayout(layout)
            if dlg.exec():
                servicename = dlg.findChild(
                    QLineEdit, "linkservice_lineedit_service_name"
                ).text()
        else:
            servicename = self.service_lineedit_service_name.text()

        host = self.target_combobox_hosts.currentText()
        group = self.target_combobox_groups.currentText()
        tree_item = f"{group}{file_path}"
        if self.target_combobox_hosts.currentText() != "":
            tree_item = f"{group}/{host}{file_path}"

        item_data = {"service": servicename}

        YamlManager(self.ad.s_project["tree_file"]).create_or_update_item(
            tree_item, item_data
        )

    # endregion

    # region Helpers
    def parse_full_file_path(self, project_path, file_path):
        cleaned_path = file_path.replace(project_path, "")
        parts = cleaned_path.split("/")
        if len(parts) == 2:
            return None
        parts = parts[1:]
        if len(parts) < 3:
            return None

        file_name = parts[-1]
        if parts[0].startswith("all"):
            real_target = str(os.path.join("/", *parts[1:]))
            file_info = {
                "group": parts[0],
                "host": None,
                "real_target": real_target,
                "file_name": file_name,
            }
        else:
            real_target = str(os.path.join("/", *parts[2:]))
            file_info = {
                "group": parts[0],
                "host": parts[1],
                "real_target": real_target,
                "file_name": file_name,
            }

        return file_info

    def disable_elements(self, state):
        pass
        # self.import_project_toolbar_option.setDisabled(state)
        # self.select_project_toolbar_option.setDisabled(state)
        # self.sync_tree_toolbar_option.setDisabled(state)
        # self.file_button_fetch.setDisabled(state)
        # self.file_button_send.setDisabled(state)
        # self.service_button_container.setDisabled(state)
        # self.action_buttons_groupbox.setDisabled(state)

    def debug_button(self):
        sender_name = self.sender().objectName()
        self.console_text(f"DEBUG {sender_name}", "red")

        group = self.target_combobox_groups
        host = self.target_combobox_hosts
        file_target = self.file_lineedit_target
        service_target = self.service_lineedit_service_name

        i = host.findText("peddle-cluster-login")
        host.setCurrentIndex(i)
        i = group.findText("login")
        group.setCurrentIndex(i)

        match sender_name:
            case "file_button_send":
                file_target.setText("/etc/anviltest.txt")
            case "file_button_fetch":
                file_target.setText("/etc/anviltest.txt")
            case s if s.startswith("service"):
                service_target.setText("rsyslog")
            case s if s.startswith("playshell"):
                self.form_setup(self.actions_groupbox, "playshell", True)
                com1 = self.findChild(QLineEdit, "playshell_lineedit_command1")
                com1.setText("echo 'Hello World'")
                com2 = self.findChild(QLineEdit, "playshell_lineedit_command2")
                com2.setText("echo 'Hello World'")
                com3 = self.findChild(QLineEdit, "playshell_lineedit_command3")
                com3.setText("echo 'Hello World'")
            # case s if s.startswith("playfile"):
            #     self.form_setup(self.actions_groupbox, "playfile", True)
            case s if s.startswith("playapt"):
                self.form_setup(self.actions_groupbox, "playapt", True)
                self.findChild(QLineEdit, "playapt_lineedit_package").setText("btop")
                self.findChild(QCheckBox, "playapt_checkbox_update").setChecked(True)
            case s if s.startswith("playufw"):
                self.form_setup(self.actions_groupbox, "playufw", True)
                self.findChild(QLineEdit, "playufw_lineedit_port").setText("420")
                self.findChild(QLineEdit, "playufw_lineedit_comment").setText("Test")
            case s if s.startswith("file_button_link_service"):
                self.console_text("Linking service", "cyan")
                i = host.findText("peddle-cluster-mgmt")
                host.setCurrentIndex(i)
                i = group.findText("management")
                group.setCurrentIndex(i)
                service_target.setText("munge")
                file_target.setText("/etc/munge/munge.key")

        self.ansible_execute()

    def console_text(self, text, color_name):
        color_map = {
            "red": QColor(192, 57, 43),
            "green": QColor(39, 174, 96),
            "yellow": QColor(241, 196, 15),
            "purple": QColor(155, 89, 182),
            "cyan": QColor(93, 173, 226),
            "gray": QColor(149, 165, 166),
            "black": QColor(23, 32, 42),
        }
        color = color_map.get(color_name, QColor(0, 0, 0))

        format = QTextCharFormat()
        format.setForeground(color)
        cursor = self.console_textedit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        cursor.insertText(text, format)
        cursor.insertText("\n")

        self.console_textedit.ensureCursorVisible()

    def modify_child(self, name: str, child_type=None, purpose=None, value=None):
        """
        name (str): objectname
        child_type: type of child
        purpose: setindex, settext, disable, enable, clear
        value: value to set
        """
        child = self.findChild(child_type, name)
        if child_type == QComboBox:
            if purpose == "setindex":
                child.setCurrentIndex(value)
        if child_type == QLineEdit:
            if purpose == "settext":
                child.setText(value)
            elif purpose == "disable":
                child.setDisabled(True)
                child.setPlaceholderText("")
                child.clear()
            elif purpose == "enable":
                child.setDisabled(False)
        if child_type == QPushButton:
            if purpose == "disable":
                child.setDisabled(True)
            elif purpose == "enable":
                child.setDisabled(False)
            elif purpose == "connect":
                child.clicked.connect(value)

    def expand_tree(self, search_term, root_index=None):
        if root_index is None:
            root_index = self.tree.rootIndex()

        def recursive_expand(search_term, root_index):
            for row in range(self.model.rowCount(root_index)):
                index = self.model.index(row, 0, root_index)
                if self.model.data(index).lower() == search_term.lower():
                    self.tree.expand(index)
                    parent = index.parent()
                    while parent.isValid():
                        self.tree.expand(parent)
                        parent = parent.parent()
                if self.model.hasChildren(index):
                    recursive_expand(search_term, index)

        # Collapse all to ensure a consistent state before expanding
        self.tree.collapseAll()
        recursive_expand(search_term, root_index)

    def get_desired_class_attributes(
        self,
        prefix: str = None,
        obj_name: str = None,
        ret_type: type = list[str],
    ) -> str | object | list[str] | list[object]:
        """
        __Return desired class attributes__\n
        Usage: \n
        `ret_type=` -> return all attributes \n
        `prefix=, ret_type=` -> return all attributes with prefix \n
        `obj_name=, ret_type=` -> return single attribute with obj_name. ret_type is `str | object`.

        """
        types = [QComboBox, QLineEdit, QCheckBox, QPushButton, QWidget]
        atribs = []
        select_attribs = []
        if obj_name is not None:
            if ret_type is list[str]:
                ret_type = str

        for i in dir(self):
            if type(getattr(self, i)) in types:
                atribs.append(i)

        if prefix is None and obj_name is None:
            ret_val = atribs
        elif prefix is not None:
            for i in atribs:
                parts = i.split("_")
                if parts[0] == prefix:
                    select_attribs.append(i)
            ret_val = select_attribs

        if obj_name is not None:
            for i in atribs:
                if i == obj_name:
                    ret_val = i

        if ret_type == list[str]:
            return ret_val
        elif ret_type == list[object]:
            return [getattr(self, i) for i in ret_val]
        elif ret_type == object:
            return getattr(self, ret_val)
        elif ret_type == str:
            return ret_val

    def children_to_attr(self, parent):
        # pdebug("children_to_attr()", "purple")
        for child in parent.children():
            child_name = child.objectName()
            if child_name:
                setattr(self, child_name, child)

            if isinstance(child, (QHBoxLayout, QVBoxLayout, QFormLayout)):
                self.children_to_attr(child)
                for i in range(child.count()):
                    item = child.itemAt(i)

            if isinstance(parent, QFormLayout):
                for i in range(parent.rowCount()):
                    item1 = parent.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    item2 = parent.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if item1 and item1.widget():
                        widget = item1.widget()
                        widget_name = widget.objectName()
                        if widget_name:
                            setattr(self, widget_name, widget)
                        if isinstance(
                            widget.layout(), (QHBoxLayout, QVBoxLayout, QFormLayout)
                        ):
                            self.children_to_attr(widget.layout())
                    if item2 and item2.widget():
                        widget = item2.widget()
                        widget_name = widget.objectName()
                        if widget_name:
                            setattr(self, widget_name, widget)
                        if isinstance(
                            widget.layout(), (QHBoxLayout, QVBoxLayout, QFormLayout)
                        ):
                            self.children_to_attr(widget.layout())

    def get_children(self, parent) -> list[str]:
        # pdebug("Entering print_children()", "purple")
        children = []

        def print_widget_names(widget):
            """Recursively print the object names of child widgets if they have a set objectName"""
            nonlocal children
            for child in widget.children():
                if isinstance(child, QWidget):  # Check if it is a QWidget
                    if child.objectName() and not child.objectName().startswith("qt_"):
                        children.append(child.objectName())
                    print_widget_names(child)  # Recursive call to handle all children

        for index in range(parent.count()):
            layout_item = parent.itemAt(index)
            widget = layout_item.widget()
            if isinstance(widget, QGroupBox):
                print_widget_names(widget)

        return children

    def populate_play_fields_comboboxs(self, prefix: str):
        group = self.target_combobox_groups.currentText()
        var_file_path = self.ad.s_project["groups"][group]["var_file_path"]
        vars_content = YamlManager(var_file_path).get_all()
        print(vars_content)
        if vars_content is None:
            return

        match prefix:
            case "playfile":
                self.playfile_combobox_file_vars.clear()
                self.playfile_combobox_directory_vars.clear()
                self.playfile_combobox_file_vars.addItem("")
                self.playfile_combobox_directory_vars.addItem("")
                for i in vars_content.keys():
                    if i.endswith("_config_files"):
                        self.playfile_combobox_file_vars.addItem(i)
                    elif i.endswith("_directories"):
                        self.playfile_combobox_directory_vars.addItem(i)

                self.playfile_combobox_state.setCurrentIndex(-1)
                self.playfile_combobox_file_vars.setCurrentIndex(-1)
                self.playfile_combobox_directory_vars.setCurrentIndex(-1)
            case "playapt":
                apt_vars = []
                for i in self.ad.vars.keys():
                    if i.endswith("_packages"):
                        apt_vars.append(i)
                self.populate_combobox("playapt", "Apt Vars", apt_vars)
            case "playufw":
                rule_vars = []
                for i in self.ad.vars.keys():
                    if i.endswith("_firewall_rules"):
                        rule_vars.append(i)
                self.populate_combobox("playufw", "Rule Vars", rule_vars)

    # endregion

    # region Ansible
    def ansible_execute(self):
        flag = None
        target = None
        pgroup = None
        phost = None
        sender_name = self.sender().objectName()

        pgroup = self.target_combobox_groups.currentText()
        phost = self.target_combobox_hosts.currentText()
        if phost == "":
            phost = None

        match sender_name:
            case "file_button_fetch":
                flag = "-r-fetch"
                target = self.findChild(QLineEdit, "file_lineedit_target").text()
            case "file_button_send":
                flag = "-r-send"
                target = self.findChild(QLineEdit, "file_lineedit_target").text()
            case s if s.startswith("service"):

                target = self.findChild(
                    QLineEdit, "service_lineedit_service_name"
                ).text()
                if sender_name == "service_button_restart":
                    flag = "-r-service-r"
                elif sender_name == "service_button_start":
                    flag = "-r-service-s"
                elif sender_name == "service_button_stop":
                    flag = "-r-service-q"
            case "playshell_button_run":
                commands = []
                flag = "-r-shell"
                com = [
                    self.findChild(QLineEdit, "playshell_lineedit_command1"),
                    self.findChild(QLineEdit, "playshell_lineedit_command2"),
                    self.findChild(QLineEdit, "playshell_lineedit_command3"),
                ]

                for c in com:
                    if c.text() != "":
                        commands.append(c.text())
                if len(commands) == 0:
                    self.console_text("No commands to run", "red")
                else:
                    target = commands
            case "varedit_button_save":
                raw = self.console_textedit.toPlainText()
                removed_newline = raw.replace("\n", "")
                try:
                    now_json = json.loads(removed_newline)
                    keyv = self.varlist.currentItem().text()
                    YamlManager(self.ad.sp_variables_file_path).create_or_update_item(
                        keyv, now_json
                    )
                except json.JSONDecodeError:
                    self.simplge_message("Invalid JSON")
            case "varedit_button_reset":
                self.console_textedit.clear()
                keyv = self.varlist.currentItem().text()
                self.console_text(json.dumps(self.ad.vars[keyv], indent=8), "black")
            case "playbookctl_button_run_playbook":
                flag = "-r-playbook"
                target = self.playbooklist.currentItem().text()
            case s if s.startswith("playfile_"):
                target = {}
                if s.endswith("create"):
                    flag = "-r-file-create"
                    target["state"] = "create"
                elif s.endswith("change_permissions"):
                    flag = "-r-file-permissions"
                    target["state"] = "permissions"
                else:
                    flag = "-r-file-delete"
                    target["state"] = "absent"

                dirvars = self.playfile_combobox_directory_vars.currentText()
                filevars = self.playfile_combobox_file_vars.currentText()

                if dirvars != "":
                    target["dirvar"] = {}
                    target["dirvar"] = self.ad.vars[dirvars]
                    target["varname"] = dirvars
                elif filevars != "":
                    target["filevar"] = {}
                    target["filevar"] = self.ad.vars[filevars]
                    target["varname"] = filevars
                else:
                    target["manual"] = {}
                    target["manual"]["path"] = self.playfile_lineedit_path.text()
                    target["manual"]["owner"] = self.playfile_lineedit_owner.text()
                    target["manual"]["group"] = self.playfile_lineedit_group.text()
                    target["manual"]["mode"] = self.playfile_lineedit_mode.text()
                    target["manual"][
                        "state"
                    ] = self.playfile_combobox_state.currentText()
            case "file_button_link_service":
                self.link_service()
            case "playcopy_button_copy":
                flag = "-r-file-copy"
                target = {}

                if self.playcopy_combobox_file_vars.currentText() != "":
                    target["var"] = self.playcopy_combobox_file_vars.currentText()
                else:
                    target["manual"] = {}
                    target["manual"]["localpath"] = self.playcopy_lineedit_source.text()
                    target["manual"][
                        "remotepath"
                    ] = self.playcopy_lineedit_destination.text()
                    target["manual"]["owner"] = self.playcopy_lineedit_owner.text()
                    target["manual"]["group"] = self.playcopy_lineedit_group.text()
                    target["manual"]["mode"] = self.playcopy_lineedit_mode.text()
        # self.disable_elements(True)

        if flag is not None and target is not None and pgroup is not None:
            worker = Worker(
                self.ansible_run,
                self.ad,
                flag,
                target,
                pgroup,
                phost,
            )
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.worker_progress)
            self.thread_pool.start(worker)

    def ansible_run(self, ad, flag, target, pgroup, phost, progress_callback=None):
        self.progress_bar.setRange(0, 0)
        playbook(
            ad,
            flag,
            target,
            pgroup,
            phost,
            progress_callback=progress_callback,
        )

    def worker_progress(self, data):
        text = data[0]
        color = data[1]
        self.console_text(text, color)

    def thread_complete(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.reset()
        # self.disable_elements(False)

    # endregion


def anvil_gui(ad: AnvilData):
    app = QApplication(sys.argv)
    window = MainWindow(ad)
    window.show()
    app.exec()
