import sys, os, json
from typing import Callable
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
    QHBoxLayout,
    QMessageBox,
    QMainWindow,
    QWidget,
    QSpacerItem,
    QApplication,
    QSizePolicy,
    QMenu,
    QTabWidget,
)
from PySide6.QtGui import QTextCharFormat, QTextCursor, QColor, QAction
import qdarktheme
from core.classes import AnvilData, YamlManager, Printer
from core.dialogs import ImportProjectDialog, SelectProjectDialog
from core.ansible import playbook
from core.worker import Worker
from core.gui_components import MakeSection


class MainWindow(QMainWindow):
    def __init__(self, ad: AnvilData):
        super().__init__()
        qdarktheme.setup_theme()
        self.ad = ad
        self.manual_change = True
        self.thread_pool = QThreadPool()
        self.setWindowTitle("Anvil")
        self.p = Printer("class", "MainWindow")

        top_layout = QHBoxLayout()
        top_layout.setObjectName("top_layout")
        bottom_layout = QVBoxLayout()
        bottom_layout.setObjectName("bottom_layout")

        s1 = MakeSection(self, top_layout, QVBoxLayout(), "s1", True)
        s1.insert_mode = True
        s1.qgroupbox("target_groupbox", "Target Machines")
        self.setup_widget(s1)
        s1.set_active("s1_layout")
        s1.insert(self.setup_file_tree())

        # Section 2, the tab area.
        s2 = MakeSection(self, top_layout, QVBoxLayout(), "s2", True)
        s2.insert_mode = True
        s2.qtabwidget("s2_tabs")

        _, widget = s2.qwidget("quick_actions_tab", QVBoxLayout, "Quick Actions")
        widget.setSpacing(20)

        quick_tab = MakeSection(
            self, s2.active_layout, QVBoxLayout(), "quick_tab", True
        )
        quick_tab.insert_mode = True
        quick_tab.qgroupbox("quickfile", "File")
        self.setup_widget(quick_tab)
        quick_tab.last("layout")
        quick_tab.qgroupbox("quickshell", "Shell")
        self.setup_widget(quick_tab)
        quick_tab.last("layout")
        quick_tab.qgroupbox("quickservice", "Service")
        self.setup_widget(quick_tab)

        s2.qwidget("file_tab", QVBoxLayout, "File")

        # file_tab = MakeSection(self, top_layout, QVBoxLayout(), "file_tab")

        # section2.qwidget("tab_shell", "ansible.builtin.shell")
        # section2.last("layout")
        # section2.qwidget("tab_apt", "ansible.builtin.apt")
        # section2.last("layout")
        # section2.qwidget("tab_ufw", "community.general.ufw")
        # section.container_widget()
        # self.setup_groupbox(section, "")

        console_section = MakeSection(self, top_layout, QVBoxLayout(), "console", True)
        console_textedit = QTextEdit()
        console_textedit.setMinimumWidth(400)
        console_textedit.setReadOnly(True)
        setattr(self, "console_textedit", console_textedit)
        console_section.insert(console_textedit)

        main_container = QWidget()
        window_layout = QVBoxLayout(main_container)
        window_layout.addLayout(top_layout)

        self.setCentralWidget(main_container)
        # quit()
        # self.setup_menubar()
        # self.showMaximized()

    # region GUI_Setup

    #             # top_actions_layout = QVBoxLayout()
    #             # top_actions_layout.setObjectName("top_actions_layout")
    #             # setattr(self, "top_actions_layout", top_actions_layout)
    #             # bottom_actions_layout = QVBoxLayout()
    #             # bottom_actions_layout.setObjectName("bottom_actions_layout")
    #             # setattr(self, "bottom_actions_layout", bottom_actions_layout)
    #             # self.setup_groupbox(top_actions_layout, "empty", "Action Area", 350)
    #             # layout.addLayout(top_actions_layout)
    #             # layout.addLayout(bottom_actions_layout)

    def setup_menubar(self):
        menu = self.menuBar()
        prj_menu = menu.addMenu("Project Settings")
        dbg_menu = menu.addMenu("Debug")

        self.create_qaction(prj_menu, "Import a Project", self.import_project_dialog)
        self.create_qaction(prj_menu, "Select a Project", self.select_project_dialog)
        self.create_qaction(
            prj_menu, "Select Playbook Directory", self.select_playbook_directory
        )

        self.create_qaction(prj_menu, "Sync Tree", self.dialog_sync_tree)
        self.create_qaction(
            dbg_menu,
            "File Send",
            self.signal_connect_debug_button,
            "file_button_send",
        )
        self.create_qaction(
            dbg_menu,
            "File Fetch",
            self.signal_connect_debug_button,
            "file_button_fetch",
        )
        self.create_qaction(
            dbg_menu,
            "Service Restart",
            self.signal_connect_debug_button,
            "service_button_restart",
        )
        self.create_qaction(
            dbg_menu,
            "Service Start",
            self.signal_connect_debug_button,
            "service_button_start",
        )
        self.create_qaction(
            dbg_menu,
            "Service Stop",
            self.signal_connect_debug_button,
            "service_button_stop",
        )
        self.create_qaction(
            dbg_menu,
            "Files",
            self.signal_connect_debug_button,
            "playfile_button_create",
        )
        self.create_qaction(
            dbg_menu,
            "Apt",
            self.signal_connect_debug_button,
            "playapt_button_install",
        )
        self.create_qaction(
            dbg_menu, "UFW", self.signal_connect_debug_button, "playufw_button_allow"
        )
        self.create_qaction(
            dbg_menu, "Shell", self.signal_connect_debug_button, "shell_button_run"
        )
        self.create_qaction(
            dbg_menu,
            "Link Service",
            self.signal_connect_debug_button,
            "file_button_link_service",
        )

    def setup_file_tree(self) -> QTreeView:
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
        setattr(self, "file_system_model", model)
        setattr(self, "tree_view", tree)
        tree.setMinimumWidth(350)
        tree.setMaximumWidth(400)
        tree.setObjectName("file_tree")
        return tree

    def setup_widget(
        self,
        ms: MakeSection,
        purpose: str = None,
    ):
        self.p.set("function", "setup_widget")
        active_widget = ms.active_widget.objectName()
        bc1 = QWidget()
        bl1 = QHBoxLayout(bc1)
        bl1.setContentsMargins(0, 0, 0, 0)

        bc2 = QWidget()
        bl2 = QHBoxLayout(bc2)
        bl2.setContentsMargins(0, 0, 0, 0)

        match active_widget:
            case "target_groupbox":
                ms.qcombobox("groups", "Groups", self.ad.s_project["groups_list"])
                ms.qcombobox("hosts", "Hosts", self.ad.s_project["hosts_list"])
            case "quickfile":
                ms.qlineedit("quickfile_target", "/etc/hosts", "Target File")
                ms.qlayout(QHBoxLayout)
                ms.qpushbutton("quickfile_fetch", "Fetch")
                ms.qpushbutton("quickfile_send", "Send")
                ms.last("layout")
                ms.qlayout(QHBoxLayout)
                ms.qpushbutton("quickfile_linkservice", "Link Service")
                ms.qpushbutton("quickfile_linkcommands", "Link Commands")
                ms.last("layout")
            case "quickshell":
                ms.qlineedit("quickshell_1", "echo 'Hello'")
                ms.qlineedit("quickshell_2", "echo 'World'")
                ms.qlineedit("quickshell_3", "echo '!'")
                ms.qpushbutton("quickshell_run", "Run")
                ms.qspaceritem()
            case "quickservice":
                ms.qlineedit("service_name", "rsyslog")
                ms.qlayout(QHBoxLayout)
                ms.qpushbutton("quickservice_start", "Start")
                ms.qpushbutton("quickservice_restart", "Restart")
                ms.last("layout")
                ms.qlayout(QHBoxLayout)
                ms.qpushbutton("quickservice_stop", "Stop")
                ms.qpushbutton("quickservice_enable", "Enable")
                ms.qpushbutton("quickservice_disable", "Disable")
                ms.last("layout")
        self.p.ok(ms.active_widget.objectName())

        #     case "playfile":
        #         state = ["file", "absent", "directory", "touch"]
        #         recurse = ["yes", "no"]
        #         self.qcombobox(parent_layout, prefix, "state", state)
        #         self.qcombobox(parent_layout, prefix, "recurse", recurse)
        #         self.qlineedit(parent_layout, prefix, "path", "/etc/hosts")
        #         self.qlineedit(parent_layout, prefix, "owner", "root")
        #         self.qlineedit(parent_layout, prefix, "group", "root")
        #         self.qlineedit(parent_layout, prefix, "mode", "0744")
        #         self.create_spacer(parent_layout)
        #         self.qpushbutton(bl1, prefix, "Submit")
        #     case "playfile_vars":
        #         self.qcombobox(parent_layout, prefix, "Directories", [])
        #         self.qcombobox(parent_layout, prefix, "Files", [])
        #         self.qpushbutton(bl1, prefix, "Create")
        #         self.qpushbutton(bl1, prefix, "Absent")
        #         self.qpushbutton(bl1, prefix, "Permissions")
        #     case "playpackage":
        #         preset = [
        #             "apt-get upgrade",
        #             "apt-get dist-upgrade",
        #             "apt-get update",
        #             "autoclean",
        #             "apt-get clean",
        #             "autoremove",
        #             "autoremove + purge",
        #         ]
        #         self.qcombobox(parent_layout, prefix, "Preset", preset)
        #         state = ["present", "latest", "absent"]
        #         self.qcombobox(parent_layout, prefix, "State", state)
        #         self.qlineedit(parent_layout, prefix, "Package 1", "nginx")
        #         self.qlineedit(parent_layout, prefix, "Package 2")
        #         self.qlineedit(parent_layout, prefix, "Package 3")
        #         self.qlineedit(parent_layout, prefix, "Package 4")
        #         hbox1 = QHBoxLayout()
        #         self.create_checkbox(hbox1, prefix, "autoclean")
        #         self.create_checkbox(hbox1, prefix, "autoremove")
        #         # parent_layout.addRow(hbox1)
        #         hbox2 = QHBoxLayout()
        #         self.create_checkbox(hbox2, prefix, "clean")
        #         self.create_checkbox(hbox2, prefix, "purge")
        #         # parent_layout.addRow(hbox2)
        #         self.create_checkbox(parent_layout, prefix, "update_cache")
        #         self.qlineedit(parent_layout, prefix, "cache_valid_time")
        #         upgrade = ["dist", "full", "safe", "yes", "no"]
        #         self.qcombobox(parent_layout, prefix, "upgrade", upgrade)
        #         self.create_spacer(parent_layout)
        #         self.qpushbutton(bl1, prefix, "Submit")
        #     case "playpackage_vars":
        #         self.qcombobox(parent_layout, prefix, "Package List", [])
        #         parent_layout.addRow(QLabel("Package List must have options defined."))
        #         self.create_spacer(parent_layout)
        #         self.qpushbutton(bl1, prefix, "Submit")
        #     # case "playcopy":
        #     #     self.qcombobox(parent_layout, prefix, "Files", [])
        #     #     self.create_spacer(parent_layout)
        #     #     self.qpushbutton(bl1, prefix, "Submit")
        #     case "playfirewall":
        #         rule = ["allow", "deny", "reject"]
        #         self.qcombobox(parent_layout, prefix, "rule", rule)
        #         self.qlineedit(parent_layout, prefix, "port", "22")
        #         proto = [
        #             "any",
        #             "tcp",
        #             "udp",
        #             "ipv6",
        #             "esp",
        #             "ah",
        #             "gre",
        #             "igmp",
        #         ]

        #         self.qcombobox(parent_layout, prefix, "proto", proto)
        #         self.qlineedit(parent_layout, prefix, "Comment", "OpenSSH")
        #         self.create_checkbox(parent_layout, prefix, "delete")
        #         self.create_spacer(parent_layout)
        #         self.qpushbutton(bl1, prefix, "Submit")
        #     case "playfirewall_vars":
        #         self.qcombobox(parent_layout, prefix, "Rule List", [])
        #         parent_layout.addRow(QLabel("Rule List must have options defined."))
        #         self.qpushbutton(bl1, prefix, "Submit")
        #     case "linkservice":
        #         self.qlineedit(parent_layout, prefix, "Service", "rsyslog")
        #         self.qpushbutton(bl1, prefix, "Link")

        # if len(self.get_children(bl1)) > 0:
        #     bc1.setVisible(True)
        #     parent_layout.addRow(bc1)
        # else:
        #     bc1.setVisible(False)

        # if len(self.get_children(bl2)) > 0:
        #     bc2.setVisible(True)
        #     parent_layout.addRow(bc2)
        # else:
        #     bc2.setVisible(False)

    # endregion

    # region Signals

    def signal_connect_button(self):
        sender = self.sender().objectName()
        if sender.startswith("change_action"):
            self.modify_children("_actions_layout", "RemoveChildren")
        match sender:
            case "change_action_button_file":

                self.setup_groupbox(
                    self.top_actions_layout, "playfile", "File Utilities", 350
                )
                self.populate_play_fields_comboboxs()
            case "change_action_button_copy":
                self.setup_groupbox(
                    self.top_actions_layout, "playcopy", "ansible.builtin.copy", 350
                )
                self.populate_play_fields_comboboxs()
            case "change_action_button_apt":
                self.setup_groupbox(
                    self.top_actions_layout, "playapt", "ansible.builtin.apt", 350
                )
                self.playapt_lineedit_cache_valid_time.setText("3600")
                self.populate_play_fields_comboboxs()
            case "change_action_button_ufw":
                self.setup_groupbox(
                    self.top_actions_layout, "playufw", "community.general.ufw", 350
                )
                self.populate_play_fields_comboboxs()
                ind = self.playufw_combobox_proto.findText("tcp")
                self.playufw_combobox_proto.setCurrentIndex(ind)

            case "file_button_link_service":
                self.link_service()
            case "file_button_link_commands":
                pass
            case _:
                self.ansible_execute()

    def signal_connect_debug_button(self):
        sender_name = self.sender().objectName()
        group = self.target_combobox_groups
        host = self.target_combobox_host

        i = host.findText("peddle-cluster-mgmt")
        host.setCurrentIndex(i)

        match sender_name:
            case "file_button_send":
                pass
                # file_target.setText("/etc/anviltest.txt")
            case "file_button_fetch":
                pass
                # file_target.setText("/etc/anviltest.txt")
            case s if s.startswith("service"):
                pass
                # service_target.setText("rsyslog")
            case s if s.startswith("shell"):
                pass
                # self.setup_groupbox(self.actions_groupbox, "shell", True)
                # com1 = self.findChild(QLineEdit, "shell_lineedit_command1")
                # com1.setText("echo 'Hello World'")
                # com2 = self.findChild(QLineEdit, "shell_lineedit_command2")
                # com2.setText("echo 'Hello World'")
                # com3 = self.findChild(QLineEdit, "shell_lineedit_command3")
                # com3.setText("echo 'Hello World'")
            case s if s.startswith("playfile"):
                pass
                # self.setup_groupbox(self.actions_groupbox, "playfile", True)
            case s if s.startswith("playapt"):
                pass
                # self.setup_groupbox(self.actions_groupbox, "playapt", True)
                # self.findChild(QLineEdit, "playapt_lineedit_package").setText("btop")
                # self.findChild(QCheckBox, "playapt_checkbox_update").setChecked(True)
            case s if s.startswith("playufw"):
                pass
                # self.setup_groupbox(self.actions_groupbox, "playufw", True)
                # self.findChild(QLineEdit, "playufw_lineedit_port").setText("420")
                # self.findChild(QLineEdit, "playufw_lineedit_comment").setText("Test")
            case s if s.startswith("file_button_link_service"):
                self.file_lineedit_target.setText("/etc/sssd/sssd.conf")
                self.service_lineedit_service_name.setText("sssd")
                self.link_service()
                return

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

    def signal_combobox_index_changed(self):
        if self.manual_change:
            self.manual_change = False
            prefix = None
            sender_name = self.sender().objectName()
            choice = self.sender().currentText()

            match sender_name:
                case "target_combobox_groups":
                    self.ad.set_s_group(choice)
                    self.target_combobox_host.setCurrentIndex(-1)
                    self.tree.collapseAll()
                    self.expand_tree(choice)
                    self.populate_play_fields_comboboxs()
                case "target_combobox_host":
                    if choice != "":
                        self.ad.set_s_host(choice)
                        group = self.ad.s_host["group"]
                        gi = self.target_combobox_groups.findText(group)
                        self.target_combobox_groups.setCurrentIndex(gi)
                        self.expand_tree(self.target_combobox_groups.currentText())
                        self.expand_tree(self.target_combobox_host.currentText())
                        self.populate_play_fields_comboboxs()
                    else:
                        group = None
                        self.tree.collapseAll()
                        self.target_combobox_host.setCurrentIndex(-1)
                        self.target_combobox_groups.setCurrentIndex(-1)

                case s if s.startswith("playfile_"):
                    if s.endswith("state"):
                        if choice == "directory":
                            self.modify_children("_recurse", "setVisible", True)
                        else:
                            self.modify_children("_recurse", "setVisible", False)

                    if s.endswith("directories"):
                        self.modify_children("files", "setCurrentIndex", -1)

                    if s.endswith("files"):
                        self.modify_children("directories", "setCurrentIndex", -1)

                case s if s.startswith("playapt"):
                    if s.endswith("preset"):
                        if choice != "":
                            ex = ["playapt_combobox_preset"]
                            self.modify_children("playapt_", "setDisabled", True, ex)
                        else:
                            self.modify_children("playapt_", "setDisabled", False)
            self.manual_change = True

    # endregion

    # region Ansible Execution

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

    # region Dialogs Handling

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
            self.ad.import_existing_project(projectname, projectdir)
        else:
            pass

    def select_project_dialog(self):
        dlg = SelectProjectDialog(self.ad, self)
        if dlg.exec():
            selection = dlg.projects_combo.currentText()
            self.ad.set_s_project(selection)
            self.update_gui()

    def dialog_sync_tree(self):
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
            self.ad.sync_tree_with_file_system()
            self.model.setRootPath(self.ad.s_project["path"])
            self.tree.setRootIndex(self.model.index(self.ad.s_project["path"]))

    def select_playbook_directory(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        if dlg.exec():
            self.ad.sp_playbooks_directory = dlg.selectedFiles()[0]
            self.ad.sync_project_with_file_system()

    def simplge_message(self, message):
        msgBox = QMessageBox()
        msgBox.setText(message)
        msgBox.exec()

    def link_service(self):
        p = Printer("function", "link_service()")
        dlg = QDialog(self)
        dlg.setWindowTitle("Link Service")
        layout = QVBoxLayout()
        dlg.setLayout(layout)
        self.setup_groupbox(layout, "linkservice", "Link Service")

        button = dlg.findChild(QPushButton, "linkservice_button_link")
        servicename = self.service_lineedit_service_name.text()
        button.clicked.connect(dlg.accept)
        file_path = self.file_lineedit_target.text()

        if servicename == "":
            if dlg.exec():
                servicename = dlg.linkservice_lineedit_service.text()

        host = self.target_combobox_host.currentText()
        group = self.target_combobox_groups.currentText()

        tree_item = f"{group}{file_path}"
        if self.target_combobox_host.currentText() != "":
            tree_item = f"{group}/{host}{file_path}"

        item_data = YamlManager(self.ad.s_project["tree_file"]).get_item(tree_item)
        item_data["service"] = servicename

        YamlManager(self.ad.s_project["tree_file"]).create_or_update_item(
            tree_item, item_data
        )
        self.console_text(f"Linked {servicename} to {file_path}", "black")
        p.changedata(f"linked {servicename} to {tree_item}")

    # endregion

    # region Helpers and Utils

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
        single = getattr(self, name_keyword, None)
        if single is not None:
            children = [single]
        else:
            children = self.get_desired_class_attributes(
                obj_name=name_keyword, ret_type=list[object]
            )

        for child in children:
            if child.objectName() in exclude:
                continue
            if isinstance(child, QFormLayout):
                continue
            elif type(child) in (QHBoxLayout, QVBoxLayout):
                if purpose == "RemoveChildren":
                    while child.count():
                        item = child.takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)
                    continue
                # else:
                #     print(child.objectName())
                #     self.modify_children(child.objectName(), purpose)
                #     continue

            if purpose == "setVisible":
                child.setVisible(value)
                continue

            if isinstance(child, QComboBox):
                if purpose == "setDisabled":
                    child.setCurrentIndex(-1)
                    child.setDisabled(value)
                if purpose == "setCurrentIndex":
                    child.setCurrentIndex(value)
                if purpose == "ReplaceItems":
                    child.clear()
                    child.addItems(value)
            elif isinstance(child, QLineEdit):
                if purpose == "setDisabled":
                    child.setText("")
                    child.setDisabled(value)
                if purpose == "setText":
                    child.setText(value)
            elif isinstance(child, QPushButton):
                if purpose == "setDisabled":
                    child.setDisabled(value)
                if purpose == "connect":
                    child.clicked.connect(value)
                if purpose == "setText":
                    child.setText(value)
            elif isinstance(child, QCheckBox):
                if purpose == "setDisabled":
                    child.setChecked(False)
                    child.setDisabled(value)

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

        if obj_name is not None and prefix is None:
            for i in atribs:
                if obj_name in i:
                    select_attribs.append(i)

        elif prefix is not None and obj_name is None:
            for i in atribs:
                parts = i.split("_")
                if parts[0] == prefix:
                    select_attribs.append(i)

        if ret_type == list[object]:
            return [getattr(self, i) for i in select_attribs]
        if ret_type == list[str]:
            return select_attribs

    def get_children(self, obj) -> list[str]:
        p = Printer("function", "get_children()")
        children = []
        if isinstance(obj, str):
            p.error("Parent is a string")
            return children

        if isinstance(obj, (QGroupBox, QWidget)):
            obj = obj.layout()

        def recursive_get_widget_names(obj):
            for i in range(obj.count()):
                layout_item = obj.itemAt(i)
                widget = layout_item.widget()

                if isinstance(obj, QFormLayout):
                    item1 = obj.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    item2 = obj.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if item1 and item1.widget():
                        widget = item1.widget()
                        widget_name = widget.objectName()
                        children.append(widget_name)
                    if item2 and item2.widget():
                        widget = item2.widget()
                        widget_name = widget.objectName()
                        children.append(widget_name)
                elif isinstance(obj, (QWidget, QGroupBox)):
                    children.append(widget.objectName())
                elif isinstance(obj, (QHBoxLayout, QVBoxLayout)):
                    children.append(widget.objectName())

        recursive_get_widget_names(obj)
        children = list(filter(None, children))
        return children

    def populate_play_fields_comboboxs(self):
        self.modify_children("bottom_actions_layout", "RemoveChildren", True)
        group = self.target_combobox_groups.currentText()
        top_actions_layout_children = self.get_children(self.top_actions_layout)
        if group == "":
            return
        if len(top_actions_layout_children) == 0:
            return

        prefix = top_actions_layout_children[0].split("_")[0]
        if self.ad.s_project["groups"][group].get("var_file_path") is not None:
            var_file_path = self.ad.s_project["groups"][group]["var_file_path"]
            vars_content = YamlManager(var_file_path).get_all()
            if vars_content is None:
                return

        var_names = list(vars_content.keys())
        if len(var_names) == 0:
            return

        var_list1 = []
        var_list2 = []
        match prefix:
            case "playfile":
                var_list1 = [s for s in var_names if s.endswith("_config_files")]
                var_list2 = [s for s in var_names if s.endswith("_directories")]
                if len(var_list1) == 0 and len(var_list2) == 0:
                    return

                self.setup_groupbox(
                    self.bottom_actions_layout, "playfile_vars", "Variables", 350
                )
                self.playfile_vars_combobox_files.clear()
                self.playfile_vars_combobox_directories.clear()
                self.playfile_vars_combobox_files.addItem("")
                self.playfile_vars_combobox_directories.addItem("")

                self.playfile_vars_combobox_files.addItems(var_list1)
                self.playfile_vars_combobox_directories.addItems(var_list2)

                self.playfile_combobox_state.setCurrentIndex(-1)
                self.playfile_vars_combobox_files.setCurrentIndex(-1)
                self.playfile_vars_combobox_directories.setCurrentIndex(-1)
            case "playapt":
                var_list1 = [s for s in var_names if s.endswith("_packages")]
                if len(var_list1) == 0:
                    return

                self.setup_groupbox(
                    self.bottom_actions_layout, "playapt_vars", "Variables", 350
                )
                self.playapt_vars_combobox_package_list.clear()
                self.playapt_vars_combobox_package_list.addItem("")
                self.playapt_vars_combobox_package_list.addItems(var_list1)

            case "playufw":
                var_list1 = [s for s in var_names if s.endswith("firewall_rules")]
                if len(var_list1) == 0:
                    return

                self.setup_groupbox(
                    self.bottom_actions_layout, "playufw_vars", "Variables", 350
                )
                self.playufw_vars_combobox_rule_list.clear()
                self.playufw_vars_combobox_rule_list.addItem("")
                self.playufw_vars_combobox_rule_list.addItems(var_list1)

    # endregion

    def dummy(self):
        pass


def anvil_gui(ad: AnvilData):
    app = QApplication(sys.argv)
    window = MainWindow(ad)
    window.show()
    app.exec()
