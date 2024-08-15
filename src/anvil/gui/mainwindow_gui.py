from PySide6.QtWidgets import QTabWidget, QVBoxLayout

from .create_components import (
    create_QComboBox,
    create_QGroupBox,
    create_QHBoxLayout,
    create_QLineEdit,
    create_QPushButton,
    create_QWidget,
)


def setup_quickactions_tab(parent_tabwidget: QTabWidget):
    widget, layout = create_QWidget("quickactions_tab", QVBoxLayout)
    parent_tabwidget.addTab(widget, "Quick Actions")
    # files
    quickactions_files(layout)
    # Commands
    quickactions_shell(layout)
    # Systemd
    quickactions_systemd(layout)


def quickactions_files(parent_layout: QVBoxLayout):
    quick_file_groupbox, quick_file_groupbox_layout = create_QGroupBox("quick_file", "Send / Fetch Files")
    target_file = create_QLineEdit("target_file_lineedit", "/etc/fstab")

    button_layout = create_QHBoxLayout("quick_file_btn_layout1")
    fetch_file_btn = create_QPushButton("fetch_file_btn", "Fetch File")
    send_file_button = create_QPushButton("send_file_btn", "Send File")
    button_layout.addWidget(fetch_file_btn)
    button_layout.addWidget(send_file_button)

    quick_file_groupbox_layout.addRow("Target", target_file)
    quick_file_groupbox_layout.addRow(button_layout)

    parent_layout.addWidget(quick_file_groupbox)


def quickactions_shell(target_layout: QVBoxLayout):
    groupbox, layout = create_QGroupBox("quick_shell", "Send Commands", QVBoxLayout)

    quickshell_1 = create_QLineEdit("quickshell_1", "ls -la")
    quickshell_2 = create_QLineEdit("quickshell_2", "df -h")
    quickshell_3 = create_QLineEdit("quickshell_3", "uptime")
    quickshell_run_button = create_QPushButton("quickshell_run_button", "Run")
    layout.addWidget(quickshell_1)
    layout.addWidget(quickshell_2)
    layout.addWidget(quickshell_3)
    layout.addWidget(quickshell_run_button)
    target_layout.addWidget(groupbox)


def quickactions_systemd(target_layout: QVBoxLayout):
    """
    - `quick_systemd_groupbox`, `quick_systemd_groupbox_layout`

    QLineEdit
    - `quick_systemd_service`, `service_start`

    QPushButton
    - `quick_systemd_service_start`
    - `quick_systemd_service_stop`
    - `quick_systemd_service_restart`
    - `quick_systemd_service_disable`
    - `quick_systemd_service_enable`
    - `quick_systemd_service_mask`
    """
    groupbox, layout = create_QGroupBox("quick_systemd", "Systemd", QVBoxLayout)
    target_layout.addWidget(groupbox)
    quick_systemd_service = create_QLineEdit("quick_systemd_service", "nginx")
    layout.addWidget(quick_systemd_service)

    button_layout = create_QHBoxLayout()
    service_start = create_QPushButton("quick_systemd_service_start", "Start")
    service_stop = create_QPushButton("quick_systemd_service_stop", "Stop")
    service_restart = create_QPushButton("quick_systemd_service_restart", "Restart")
    button_layout.addWidget(service_start)
    button_layout.addWidget(service_stop)
    button_layout.addWidget(service_restart)
    layout.addLayout(button_layout)

    button_layout = create_QHBoxLayout()
    service_disable = create_QPushButton("quick_systemd_service_disable", "Disable")
    service_enable = create_QPushButton("quick_systemd_service_enable", "Enable")
    service_mask = create_QPushButton("quick_systemd_service_mask", "Mask")
    button_layout.addWidget(service_disable)
    button_layout.addWidget(service_enable)
    button_layout.addWidget(service_mask)
    layout.addLayout(button_layout)

    return groupbox


def setup_files_tab(parent_tabwidget: QTabWidget):
    widget, layout = create_QWidget("files_tab", QVBoxLayout)
    parent_tabwidget.addTab(widget, "Files")

    groupbox, glayout = create_QGroupBox("files_tab", "Files")
    layout.addWidget(groupbox)
    state = ["file", "absent", "directory", "touch"]
    recurse = ["yes", "no"]
    # self.create_spacer(parent_layout)
    state_combobox = create_QComboBox("state_combobox", state)
    recurse_combobox = create_QComboBox("recurse_combobox", recurse)
    path_lineedit = create_QLineEdit("path_lineedit", "/etc/hosts")
    owner_lineedit = create_QLineEdit("owner_lineedit", "root")
    group_lineedit = create_QLineEdit("group_lineedit", "root")
    mode_lineedit = create_QLineEdit("mode_lineedit", "0744")
    submit_button = create_QPushButton("file_submit_button", "Submit")
    glayout.addRow("Path", path_lineedit)
    glayout.addRow("State", state_combobox)
    glayout.addRow("Recurse", recurse_combobox)
    glayout.addRow("Owner", owner_lineedit)
    glayout.addRow("Group", group_lineedit)
    glayout.addRow("Mode", mode_lineedit)
    glayout.addRow(submit_button)


# def setup_shell_tab(parent_tabwidget: QTabWidget):
# tab4 = ["shell_tab", "Shell", setup_shell_tab]
#
#   pass


# def setup_packages_tab(parent_tabwidget: QTabWidget):
# tab3 = ["packages_tab", "Packages", setup_packages_tab]
#     preset = [
#         "apt-get upgrade",
#         "apt-get dist-upgrade",
#         "apt-get update",
#         "autoclean",
#         "apt-get clean",
#         "autoremove",
#         "autoremove + purge",
#     ]
#     state = ["present", "latest", "absent"]
#     upgrade = ["dist", "full", "safe", "yes", "no"]

#     groupbox, layout = create_QGroupBox("packages_tab", "Packages")

#     preset_combobox = create_QComboBox("preset_combobox", preset)
#     state_combobox = create_QComboBox("state_combobox", state)
#     layout.addRow("Preset", preset_combobox)
#     layout.addRow("State", state_combobox)

#     package1_lineedit = create_QLineEdit("package_lineedit", "nginx")
#     package2_lineedit = create_QLineEdit("package_lineedit", "apache2")
#     package3_lineedit = create_QLineEdit("package_lineedit", "mysql-server")
#     package4_lineedit = create_QLineEdit("package_lineedit", "php")
#     layout.addRow("Package 1", package1_lineedit)
#     layout.addRow("Package 2", package2_lineedit)
#     layout.addRow("Package 3", package3_lineedit)
#     layout.addRow("Package 4", package4_lineedit)

#     autoclean = create_QCheckBox("autoclean", "autoclean")
#     autoremove = create_QCheckBox("autoremove", "autoremove")
#     clean = create_QCheckBox("clean", "clean")
#     purge = create_QCheckBox("purge", "purge")
#     update_cache = create_QCheckBox("update_cache", "update_cache")

#     cache_valid_time = create_QLineEdit("cache_valid_time", "86400")
#     upgrade_combobox = create_QComboBox("upgrade_combobox", upgrade)

#     hbox = create_QHBoxLayout()
#     hbox.addWidget(autoclean)
#     hbox.addWidget(autoremove)
#     hbox.addWidget(clean)
#     layout.addRow(hbox)

#     hbox = create_QHBoxLayout()
#     hbox.addWidget(purge)
#     hbox.addWidget(update_cache)
#     layout.addRow(hbox)

#     layout.addRow("Cache Valid Time", cache_valid_time)
#     layout.addRow("Upgrade", upgrade_combobox)

#     # self.create_spacer(parent_layout)

#     submit_button = create_QPushButton("package_submit_button", "Submit")
#     layout.addRow(submit_button)
#     target_layout.addWidget(groupbox)


# def setup_ufw_tab(parent_tabwidget: QTabWidget):
# tab6 = ["ufw_tab", "UFW", setup_ufw_tab]
#     rule = ["allow", "deny", "reject"]
#     proto = [
#         "any",
#         "tcp",
#         "udp",
#         "ipv6",
#         "esp",
#         "ah",
#         "gre",
#         "igmp",
#     ]
#     groupbox, layout = create_QGroupBox("ufw_tab", "UFW")
#     rule_combobox = create_QComboBox("rule_combobox", rule)
#     port_lineedit = create_QLineEdit("port_lineedit", "22")
#     proto_combobox = create_QComboBox("proto_combobox", proto)
#     comment_lineedit = create_QLineEdit("comment_lineedit", "OpenSSH")
#     delete_checkbox = create_QCheckBox("delete_checkbox", "delete")
#     submit_button = create_QPushButton("submit_button", "Submit")
#     layout.addRow("Rule", rule_combobox)
#     layout.addRow("Port", port_lineedit)
#     layout.addRow("Proto", proto_combobox)
#     layout.addRow("Comment", comment_lineedit)
#     layout.addRow(delete_checkbox)
#     layout.addRow(submit_button)
#     target_layout.addWidget(groupbox)


# def setup_systemd_tab(parent_tabwidget: QTabWidget):
# tab5 = ["systemd_tab", "Systemd", setup_systemd_tab]
#     pass
