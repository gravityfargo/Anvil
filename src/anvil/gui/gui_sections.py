from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QHBoxLayout
from .create_components import (
    create_QLineEdit,
    create_QPushButton,
    create_QGroupBox,
    create_QHBoxLayout,
)


def setup_quick_files_groupbox() -> QGroupBox:
    """
    children:
    - target_file_lineedit
    - fetch_file_btn
    - send_file_btn
    """
    groupbox, layout = create_QGroupBox("quick_file", "Send / Fetch Files")
    target_file = create_QLineEdit("target_file_lineedit", "/etc/fstab")

    button_layout = create_QHBoxLayout("quick_file_btn_layout1")
    fetch_file_btn = create_QPushButton("fetch_file_btn", "Fetch File")
    send_file_button = create_QPushButton("send_file_btn", "Send File")
    button_layout.addWidget(fetch_file_btn)
    button_layout.addWidget(send_file_button)

    layout.addRow("Target", target_file)
    layout.addRow(button_layout)

    return groupbox


def setup_quick_shell_groupbox() -> QGroupBox:
    groupbox, layout = create_QGroupBox("quick_shell", "Send Commands", QVBoxLayout)

    quickshell_1 = create_QLineEdit("quickshell_1", "ls -la")
    quickshell_2 = create_QLineEdit("quickshell_2", "df -h")
    quickshell_3 = create_QLineEdit("quickshell_3", "uptime")
    quickshell_run_button = create_QPushButton("quickshell_run_button", "Run")
    layout.addWidget(quickshell_1)
    layout.addWidget(quickshell_2)
    layout.addWidget(quickshell_3)
    layout.addWidget(quickshell_run_button)
    return groupbox


def setup_quick_systemd_groupbox() -> QGroupBox:
    groupbox, layout = create_QGroupBox("quick_systemd", "Systemd", QVBoxLayout)
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
