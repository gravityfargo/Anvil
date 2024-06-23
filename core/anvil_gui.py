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
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QMainWindow,
    QWidget,
    QSpacerItem,
    QApplication,
    QSizePolicy,
)
from PySide6.QtGui import QTextCharFormat, QTextCursor, QColor, QAction
import qdarktheme
from config.vars import AnvilData
from dialogs import ImportProjectDialog, SelectProjectDialog
from core.ansible import playbook
from core.worker import Worker
from core.file_utils import (
    sync_project_with_file_system,
    import_existing_project,
    sync_tree_with_file_system,
)
from core.helpers import YamlManager, pdebug


element_names = [
    "target_combobox_groups",
    "target_combobox_host",
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
        qdarktheme.setup_theme()
        self.ad = ad
        self.manual_change = True
        self.thread_pool = QThreadPool()
        self.setWindowTitle("Anvil")

        top_layout = QHBoxLayout()
        bottom_layout = QVBoxLayout()

        self.setup_groupbox(top_layout, "change_action", "Bulk Actions", 120)
        self.create_widget(top_layout, "filetree", 350)
        self.create_widget(top_layout, "control", 350)
        self.create_groupbox(top_layout, "actions", "Actions", QFormLayout(), 350)
        self.create_widget(top_layout, "varedit")
        self.create_widget(bottom_layout, "console")

        main_container = QWidget()
        window_layout = QVBoxLayout()
        main_container.setLayout(window_layout)
        self.setCentralWidget(main_container)
        window_layout.addLayout(top_layout)
        window_layout.addLayout(bottom_layout)

        self.createMenuBar()

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
        debug_shell_run.setObjectName("shell_button_run")
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

    def setup_groupbox(
        self,
        parent_layout: QHBoxLayout | QVBoxLayout | QFormLayout,
        prefix: str,
        name: str,
        minwidth: int = None,
    ):
        if isinstance(parent_layout, QFormLayout):
            pdebug(f"setup_groupbox() existing {parent_layout.objectName()}")
            layout_prefix = parent_layout.objectName().split("_")[0]
            groupbox = getattr(self, f"{layout_prefix}_groupbox")
            form_layout = getattr(self, parent_layout.objectName())
            exclude = [parent_layout.objectName(), groupbox.objectName()]
            self.modify_children(layout_prefix, "deleteLater", exclude=[exclude])
        else:
            self.create_groupbox(parent_layout, prefix, name, QFormLayout(), minwidth)
            groupbox = getattr(self, f"{prefix}_groupbox")
            form_layout = getattr(self, f"{prefix}_groupbox_layout")

        button_row1_container = QFrame()
        button_row1_layout = QHBoxLayout()
        button_row1_layout.setContentsMargins(0, 0, 0, 0)
        button_row1_container.setLayout(button_row1_layout)

        button_row2_container = QFrame()
        button_row2_layout = QHBoxLayout()
        button_row2_layout.setContentsMargins(0, 0, 0, 0)
        button_row2_container.setLayout(button_row2_layout)
        match prefix:
            case "change_action":
                self.create_button(form_layout, prefix, "File")
                self.create_button(form_layout, prefix, "Copy")
                self.create_button(form_layout, prefix, "Apt")
                self.create_button(form_layout, prefix, "UFW")
            case "target":
                self.create_combobox(form_layout, prefix, "Groups")
                self.create_combobox(form_layout, prefix, "Host")
            case "file":
                self.create_lineedit(form_layout, prefix, "Target", "/etc/hosts")
                self.create_button(button_row1_layout, prefix, "Fetch")
                self.create_button(button_row1_layout, prefix, "Send")
                self.create_button(button_row2_layout, prefix, "Link Service")
                self.create_button(button_row2_layout, prefix, "Link Commands")
            case "shell":
                self.create_lineedit(
                    form_layout, prefix, "Command1", "echo 'Hello World'"
                )
                self.create_lineedit(form_layout, prefix, "Command2", "")
                self.create_lineedit(form_layout, prefix, "Command3", "")
                self.create_button(button_row1_layout, prefix, "Run")
            case "service":
                self.create_lineedit(form_layout, prefix, "Service Name", "rsyslog")
                self.create_button(button_row1_layout, prefix, "Restart")
                self.create_button(button_row1_layout, prefix, "Stop")
                self.create_button(button_row1_layout, prefix, "Start")
            case "playfile":
                state = ["file", "absent", "directory", "touch"]
                recurse = ["yes", "no"]
                form_layout.addRow(QLabel("ansible.builtin.file"))
                self.create_combobox(form_layout, prefix, "state", state)
                self.create_combobox(form_layout, prefix, "recurse", recurse)
                self.create_lineedit(form_layout, prefix, "path", "/etc/hosts")
                self.create_lineedit(form_layout, prefix, "owner", "root")
                self.create_lineedit(form_layout, prefix, "group", "root")
                self.create_lineedit(form_layout, prefix, "mode", "0744")
                self.create_button(form_layout, prefix, "Submit")
                self.create_v_spacer(form_layout)
                form_layout.addRow(QLabel("Variables"))
                self.create_combobox(form_layout, prefix, "Directory Vars", [])
                self.create_combobox(form_layout, prefix, "File Vars", [])
                self.create_button(button_row1_layout, prefix, "Create")
                self.create_button(button_row1_layout, prefix, "Absent")
                self.create_button(button_row1_layout, prefix, "Permissions")

                lst = ["Local to Remote", "Remote to Local"]
            case "playapt":
                self.create_combobox(form_layout, prefix, "Apt Vars", [])
                self.create_lineedit(form_layout, prefix, "Package", "nginx")
                self.create_checkbox(form_layout, prefix, "Update")
                self.create_button(button_row1_layout, prefix, "Install")
                self.create_button(button_row1_layout, prefix, "Remove")
            case "playufw":
                self.create_combobox(form_layout, prefix, "Rule Vars", [])
                self.create_lineedit(form_layout, prefix, "Port", "22")
                self.create_lineedit(form_layout, prefix, "Comment", "OpenSSH")
                self.create_button(button_row1_layout, prefix, "Allow")
                self.create_button(button_row1_layout, prefix, "Deny")
            case "varedit":
                self.create_button(button_row1_layout, prefix, "Save")
                self.create_button(button_row1_layout, prefix, "Reset")
            case "linkservice":
                self.create_lineedit(form_layout, prefix, "Service Name", "rsyslog")
                self.create_button(button_row1_layout, prefix, "Link")

        if len(self.get_children(button_row1_layout)) > 0:
            button_row1_container.setVisible(True)
            form_layout.addRow(button_row1_container)
        else:
            button_row1_container.setVisible(False)

        if len(self.get_children(button_row2_layout)) > 0:
            button_row2_container.setVisible(True)
            form_layout.addRow(button_row2_container)
        else:
            button_row2_container.setVisible(False)

        self.children_to_attr(groupbox)

    def create_widget(
        self,
        parent_layout: QHBoxLayout | QVBoxLayout,
        prefix: str,
        minwidth: int = None,
    ):
        layout = QVBoxLayout()
        match prefix:
            case "filetree":
                model = QFileSystemModel()
                model.setRootPath(self.ad.s_project["path"])
                tree = QTreeView()
                tree.setModel(model)
                tree.setRootIndex(model.index(self.ad.s_project["path"]))
                tree.setColumnWidth(0, 300)
                tree.clicked.connect(self.on_file_selected)
                tree.hideColumn(1)
                tree.hideColumn(2)
                tree.hideColumn(3)
                setattr(self, "model", model)
                setattr(self, "tree", tree)
                if minwidth is not None:
                    tree.setMinimumWidth(minwidth)
                layout.addWidget(tree)
            case "progress_bar":
                progress_bar = QProgressBar()
                progress_bar.setRange(0, 100)
                progress_bar.setTextVisible(True)
                progress_bar.setMaximumHeight(20)
                setattr(self, "progress_bar", progress_bar)
            case "varedit":
                textedit = QTextEdit()
                textedit.setReadOnly(True)
                self.setup_groupbox(layout, "varedit", "Modify Variables")
                setattr(self, "varedit_textedit", textedit)
                layout.addWidget(textedit)
            case "console":
                console_textedit = QTextEdit()
                console_textedit.setReadOnly(True)
                setattr(self, "console_textedit", console_textedit)
                layout.addWidget(console_textedit)
            case "control":
                layout.setSpacing(20)
                self.setup_groupbox(layout, "target", "Target Machines", 350)
                self.setup_groupbox(layout, "shell", "ansible.builtin.shell")
                self.setup_groupbox(layout, "file", "ansible.builtin.fetch/copy")
                self.setup_groupbox(
                    layout, "service", "ansible.builtin.systemd_service"
                )
                self.create_widget(layout, "progress_bar")
        parent_layout.addLayout(layout)

    # endregion

    # region GUI Creation
    def create_checkbox(self, layout: QVBoxLayout, name: str, desciption: str):
        checkbox = QCheckBox(desciption)
        suffix = desciption.lower().replace(" ", "_")
        checkbox.setObjectName(f"{name}_checkbox_{suffix}")
        layout.addWidget(checkbox)

    def create_v_spacer(self, layout):
        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        if isinstance(layout, QVBoxLayout):
            layout.addSpacerItem(spacer)
        if isinstance(layout, QFormLayout):
            layout.addItem(spacer)

    def create_button(self, layout, name: str, desciption: str):
        button = QPushButton(desciption)
        suffix = desciption.lower().replace(" ", "_")
        button.setObjectName(f"{name}_button_{suffix}")
        button.clicked.connect(self.buttons_changed)
        if isinstance(layout, QFormLayout):
            layout.addRow(button)
        else:
            layout.addWidget(button)

    def create_lineedit(self, layout: QFormLayout, name: str, desciption: str, ph: str):
        lineedit = QLineEdit()
        label = QLabel(desciption)
        suffix = desciption.lower().replace(" ", "_")
        lineedit.setObjectName(f"{name}_lineedit_{suffix}")
        lineedit.setPlaceholderText(ph)
        label.setObjectName(f"{name}_lineeditlabel_{suffix}")
        layout.addRow(label, lineedit)

    def create_combobox(
        self, layout: QFormLayout, name: str, desciption: str, options=[]
    ):
        combobox = QComboBox()
        label = QLabel(desciption)
        suffix = desciption.lower().replace(" ", "_")
        combobox.setObjectName(f"{name}_combobox_{suffix}")
        label.setObjectName(f"{name}_comboboxlabel_{suffix}")
        if len(options) > 0:
            combobox.addItems(options)
        elif desciption == "Host":
            if self.ad.s_project["hosts_list"] is not None:
                combobox.addItems(self.ad.s_project["hosts_list"])
        elif desciption == "Groups":
            if self.ad.s_project["groups_list"] is not None:
                combobox.addItems(self.ad.s_project["groups_list"])
        combobox.addItem("")
        combobox.setCurrentIndex(-1)
        combobox.currentIndexChanged.connect(self.comboboxes_changed)
        layout.addRow(label, combobox)

    def create_groupbox(
        self, parent_layout, prefix: str, title: str, layout, minwidth=None
    ):
        groupbox = QGroupBox(title)
        groupbox.setLayout(layout)
        groupbox.setObjectName(f"{prefix}_groupbox")
        layout.setObjectName(f"{prefix}_groupbox_layout")
        if minwidth is not None:
            groupbox.setMinimumWidth(minwidth)
        setattr(self, groupbox.objectName(), groupbox)
        setattr(self, layout.objectName(), layout)
        parent_layout.addWidget(groupbox)

    # endregion

    # region Signal Handling
    def buttons_changed(self):
        sender = self.sender().objectName()
        pdebug(f"buttons_changed(): {sender}", "yellow")
        match sender:
            case "change_action_button_file":
                self.setup_groupbox(
                    self.actions_groupbox_layout, "playfile", "File Utilities"
                )
                self.populate_play_fields_comboboxs("playfile")
            case "change_action_button_copy":
                self.setup_groupbox(self.actions_groupbox_layout, "playcopy")
            case "change_action_button_apt":
                self.setup_groupbox(
                    self.actions_groupbox_layout, "playapt", "ansible.builtin.apt"
                )
            case "change_action_button_ufw":
                self.setup_groupbox(
                    self.actions_groupbox_layout, "playufw", "ansible.builtin.ufw"
                )
            case "file_button_link_service":
                self.link_service()
            case _:
                self.ansible_execute()

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
            hostcombo = self.target_combobox_host
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
        if self.manual_change:
            self.manual_change = False
            choice = self.sender().currentText()
            childrenlist = self.get_children(self.actions_layout)
            sender_name = self.sender().objectName()
            match sender_name:
                case "target_combobox_groups":
                    self.target_combobox_host.setCurrentIndex(-1)
                    self.tree.collapseAll()
                    self.expand_tree(choice)
                    if len(childrenlist) > 0:
                        prefix = childrenlist[0].split("_")[0]
                        self.populate_play_fields_comboboxs(prefix)
                case "target_combobox_host":
                    if choice != "":
                        group = self.ad.s_project["hosts"][choice]["group"]
                        gi = self.target_combobox_groups.findText(group)
                        self.target_combobox_groups.setCurrentIndex(gi)
                        self.expand_tree(self.target_combobox_groups.currentText())
                        self.expand_tree(self.target_combobox_host.currentText())
                        if len(childrenlist) > 0:
                            prefix = childrenlist[0].split("_")[0]
                            self.populate_play_fields_comboboxs(prefix)
                    else:
                        group = None
                        self.tree.collapseAll()
                        self.target_combobox_host.setCurrentIndex(-1)
                        self.target_combobox_groups.setCurrentIndex(-1)

                case s if s.startswith("playfile_"):
                    match s:
                        case s if s.endswith("state"):
                            if choice == "directory":
                                self.modify_children("_recurse", "setVisible", True)
                            else:
                                self.modify_children("_recurse", "setVisible", False)
                        case s if s.endswith("directory_vars"):
                            self.modify_children("file_vars", "setCurrentIndex", -1)

                        case s if s.endswith("file_vars"):
                            self.modify_children(
                                "directory_vars", "setCurrentIndex", -1
                            )
            self.manual_change = True

    # endregion

    # region Ansible

    def ansible_execute(self):
        flag = None
        target = None
        pgroup = None
        phost = None
        sender_name = self.sender().objectName()

        pgroup = self.target_combobox_groups.currentText()
        phost = self.target_combobox_host.currentText()
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
            case "shell_button_run":
                commands = []
                flag = "-r-shell"
                com = [
                    self.findChild(QLineEdit, "shell_lineedit_command1"),
                    self.findChild(QLineEdit, "shell_lineedit_command2"),
                    self.findChild(QLineEdit, "shell_lineedit_command3"),
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
            self.ad.set_s_project(selection)
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
        self.setup_groupbox(linkservice_groupbox, "linkservice")
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

        host = self.target_combobox_host.currentText()
        group = self.target_combobox_groups.currentText()
        tree_item = f"{group}{file_path}"
        if self.target_combobox_host.currentText() != "":
            tree_item = f"{group}/{host}{file_path}"

        item_data = {"service": servicename}
        print(f"Linking {servicename} to {tree_item}")
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

    def debug_button(self):
        sender_name = self.sender().objectName()
        self.console_text(f"DEBUG {sender_name}", "red")

        group = self.target_combobox_groups
        host = self.target_combobox_host
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
            case s if s.startswith("shell"):
                self.setup_groupbox(self.actions_groupbox, "shell", True)
                com1 = self.findChild(QLineEdit, "shell_lineedit_command1")
                com1.setText("echo 'Hello World'")
                com2 = self.findChild(QLineEdit, "shell_lineedit_command2")
                com2.setText("echo 'Hello World'")
                com3 = self.findChild(QLineEdit, "shell_lineedit_command3")
                com3.setText("echo 'Hello World'")
            # case s if s.startswith("playfile"):
            #     self.setup_groupbox(self.actions_groupbox, "playfile", True)
            case s if s.startswith("playapt"):
                self.setup_groupbox(self.actions_groupbox, "playapt", True)
                self.findChild(QLineEdit, "playapt_lineedit_package").setText("btop")
                self.findChild(QCheckBox, "playapt_checkbox_update").setChecked(True)
            case s if s.startswith("playufw"):
                self.setup_groupbox(self.actions_groupbox, "playufw", True)
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

    def modify_children(self, name_keyword: str, purpose=None, value=None, exclude=[]):
        """
        name_keyword (str): name keyword to search for \n
        purpose: `setCurrentIndex`, `setText`, `setDisabled`, `setVisible`, `ReplaceItems`
        value: value to set
        """

        children = self.get_desired_class_attributes(
            obj_name=name_keyword, ret_type=list[object]
        )
        for child in children:
            if purpose == "setDisabled":
                child.setDisabled(value)
                continue
            elif purpose == "setVisible":
                child.setVisible(value)
                continue

            if isinstance(child, QComboBox):
                if purpose == "setCurrentIndex":
                    child.setCurrentIndex(value)
                if purpose == "ReplaceItems":
                    child.clear()
                    child.addItems(value)
            elif isinstance(child, QLineEdit):
                if purpose == "setText":
                    child.setText(value)
            elif isinstance(child, QPushButton):
                if purpose == "connect":
                    child.clicked.connect(value)
                if purpose == "setText":
                    child.setText(value)
            elif isinstance(child, QHBoxLayout) or isinstance(child, QVBoxLayout):
                pass
            elif isinstance(child, QFormLayout):
                if purpose == "deleteLater":
                    for i in self.get_children(child):
                        if i not in exclude:
                            # getattr(self, i).deleteLater()
                            print(f"Deleting {i}")
                        else:
                            print(f"Excluding {i}")

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
    ) -> list[str] | list[object]:
        """
        Return desired class attributes\n
        Usage: \n
        `ret_type=` -> return all attributes \n
        `prefix=` -> return all attributes with prefix \n
        `obj_name=` -> return all attributes that *contain* obj_name

        """
        types = [
            QComboBox,
            QLineEdit,
            QCheckBox,
            QPushButton,
            QWidget,
            QLabel,
            QHBoxLayout,
            QVBoxLayout,
            QFormLayout,
            QGroupBox,
        ]
        atribs = []
        select_attribs = []

        for i in dir(self):
            if type(getattr(self, i)) in types:
                atribs.append(i)

        if prefix is None and obj_name is None:
            ret_val = atribs
        elif prefix is not None and obj_name is None:
            for i in atribs:
                parts = i.split("_")
                if parts[0] == prefix:
                    select_attribs.append(i)
        elif obj_name is not None and prefix is None:
            for i in atribs:
                if obj_name in i:
                    select_attribs.append(i)

        if ret_type == list[str]:
            return select_attribs
        elif ret_type == list[object]:
            return [getattr(self, i) for i in select_attribs]

    def children_to_attr(self, parent):
        # pdebug("children_to_attr()", "purple")
        for child in parent.children():
            child_name = child.objectName()
            if child_name:
                setattr(self, child_name, child)

            if isinstance(child, (QHBoxLayout, QVBoxLayout, QFormLayout)):
                self.children_to_attr(child)
                # for i in range(child.count()):
                #     item = child.itemAt(i)

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

        def recursive_get_widget_names(widget):
            """Recursively print the object names of child widgets if they have a set objectName"""
            nonlocal children
            for child in widget.children():
                if isinstance(child, QWidget):  # Check if it is a QWidget
                    if child.objectName() and not child.objectName().startswith("qt_"):
                        children.append(child.objectName())
                    recursive_get_widget_names(
                        child
                    )  # Recursive call to handle all children

        if not isinstance(parent, str):
            for i in range(parent.count()):
                layout_item = parent.itemAt(i)
                widget = layout_item.widget()
                if isinstance(widget, QGroupBox):
                    recursive_get_widget_names(widget)
                elif isinstance(parent, QFormLayout):
                    item1 = parent.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    item2 = parent.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if item1 and item1.widget():
                        widget = item1.widget()
                        widget_name = widget.objectName()
                        children.append(widget_name)
                    if item2 and item2.widget():
                        widget = item2.widget()
                        widget_name = widget.objectName()
                        children.append(widget_name)
                elif isinstance(parent, QHBoxLayout) or isinstance(parent, QVBoxLayout):
                    children.append(widget.objectName())
        children = list(filter(None, children))
        return children

    def populate_play_fields_comboboxs(self, prefix: str):
        group = self.target_combobox_groups.currentText()
        if group == "":
            self.modify_children("_vars", "setVisible", False)
            return

        var_file_path = self.ad.s_project["groups"][group]["var_file_path"]
        vars_content = YamlManager(var_file_path).get_all()
        if vars_content is None:
            self.modify_children("_vars", "setVisible", False)
            return

        self.modify_children("_vars", "setVisible", True)

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
                for i in vars_content.keys():
                    if i.endswith("_packages"):
                        apt_vars.append(i)
                self.playapt_combobox_apt_vars.addItems(apt_vars)
            case "playufw":
                rule_vars = []
                for i in vars_content.keys():
                    if i.endswith("_firewall_rules"):
                        rule_vars.append(i)
                self.populate_combobox("playufw", "Rule Vars", rule_vars)

    # endregion


def anvil_gui(ad: AnvilData):
    app = QApplication(sys.argv)
    window = MainWindow(ad)
    window.show()
    app.exec()
