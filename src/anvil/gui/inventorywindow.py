from typing import List

from PySide6.QtWidgets import QGroupBox, QLineEdit, QWidget

from anvil.config import Inventory, Project, ProjectData

from .create_components import (
    create_QComboBox,
    create_QGroupBox,
    create_QHBoxLayout,
    create_QLineEdit,
    create_QListWidget,
    create_QPushButton,
    create_QVBoxLayout,
)


class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()

        # attributes
        self.manual = False
        self.project: Project = ProjectData.get_project(ProjectData.selected_project)
        self.projectinventory = self.project.inventory
        self.hosts: List[Inventory.Host] = self.projectinventory.hosts
        self.groups: List[Inventory.Group] = self.projectinventory.groups

        # primary layout
        primary_layout = create_QHBoxLayout()
        self.primary_layout = primary_layout

        # section one
        section_one_layout = create_QVBoxLayout()
        primary_layout.addLayout(section_one_layout)

        target_selection = self.section_target_selection()
        section_one_layout.addWidget(target_selection)

        host_options = self.section_host_options()
        group_options = self.section_group_options()
        section_one_layout.addWidget(host_options)
        section_one_layout.addWidget(group_options)

        # Section two
        self.section_variable_fields(Inventory.VARS)

        self.setLayout(primary_layout)

    # GUI Sections

    def section_target_selection(self) -> QGroupBox:
        groupbox, groupbox_layout = create_QGroupBox("editinv", "Edit Inventory")

        # host dropdown
        hosts = []
        for host in self.hosts:
            hosts.append(host.name)
        hosts.append("New Host")
        selecthost = create_QComboBox("select_host", hosts)
        selecthost.currentIndexChanged.connect(self.signal_selecthost_changed)
        self.selecthost = selecthost
        groupbox_layout.addRow("Select Host", selecthost)

        # group dropdown
        groups = []
        for group in self.groups:
            groups.append(group.name)
        groups.append("New Group")
        selectgroup = create_QComboBox("select_group", groups)
        selectgroup.currentIndexChanged.connect(self.signal_selectgroup_changed)
        self.selectgroup = selectgroup
        groupbox_layout.addRow("Select Group", selectgroup)

        btnbox = create_QHBoxLayout("inv_btnbox")

        self.action_button = create_QPushButton("action_button", "Save")
        self.action_button.setDisabled(True)

        self.reject_button = create_QPushButton("reject_button", "Delete")
        self.reject_button.setDisabled(True)
        self.reject_button.clicked.connect(self.signal_delete_item)

        btnbox.addWidget(self.action_button)
        btnbox.addWidget(self.reject_button)

        groupbox_layout.addRow(btnbox)
        return groupbox

    def section_host_options(self) -> QGroupBox:
        groupbox, groupbox_layout = create_QGroupBox("hostoptions", "Host Options")

        target_host_name = create_QLineEdit("name")
        self.ansible_host = create_QLineEdit("ansible_host")

        groupbox_layout.addRow("Name", target_host_name)
        groupbox_layout.addRow("Ansible Host", self.ansible_host)

        self.hostoptions_groupbox = groupbox
        self.target_host_name = target_host_name
        return groupbox

    def section_group_options(self) -> QGroupBox:
        groupbox, groupbox_layout = create_QGroupBox("groupoptions", "Group Options")

        target_group_name = create_QLineEdit("name")

        available_groups = create_QComboBox("child_groups", [""])
        add_child_group = create_QPushButton("add_child_group", "Add Child")
        delete_child_group = create_QPushButton("delete_child_group", "Delete Child")
        current_group_children = create_QListWidget("group_children")

        available_hosts = create_QComboBox("child_hosts", [""])
        add_child_host = create_QPushButton("add_child_host", "Add Host")
        delete_child_host = create_QPushButton("delete_child_host", "Delete Host")
        # delete_child_host.clicked.connect(self.signal_delete_child_host)
        current_host_children = create_QListWidget("group_hosts")

        groupbox_layout.addRow("Name", target_group_name)

        groupbox_layout.addRow("Groups", available_groups)
        btn = create_QHBoxLayout()
        btn.addWidget(add_child_group)
        btn.addWidget(delete_child_group)
        groupbox_layout.addRow(btn)
        groupbox_layout.addRow(current_group_children)

        groupbox_layout.addRow("Hosts", available_hosts)
        btn = create_QHBoxLayout()
        btn.addWidget(add_child_host)
        btn.addWidget(delete_child_host)
        groupbox_layout.addRow(btn)
        groupbox_layout.addRow(current_host_children)

        self.groupoptions = groupbox
        self.target_group_name = target_group_name
        self.available_groups = available_groups
        self.available_hosts = available_hosts
        self.current_group_children = current_group_children
        self.current_host_children = current_host_children
        return groupbox

    def section_variable_fields(self, form_src: dict):
        groupbox, groupbox_layout = create_QGroupBox("variables", "Variables")
        self.variable_section = groupbox
        self.action_button.setEnabled(True)

        label_src = Inventory.VARS.keys()
        for label in label_src:
            val = form_src.get(label, "")

            if label == "ansible_host":
                self.ansible_host.setText(val)
                continue

            lineedit = create_QLineEdit(label)
            lineedit.setText(val)
            groupbox_layout.addRow(label, lineedit)
        self.primary_layout.addWidget(groupbox)

    # Signals

    def signal_selecthost_changed(self):
        if not self.manual:
            self.manual = True
            self.variable_section.deleteLater()
            self.clear_fields()
            self.selectgroup.setCurrentIndex(-1)
            self.manual = False

            selected = self.selecthost.currentText()
            host = self.projectinventory.get_host(selected)
            if host is None:
                form_src = Inventory.VARS
            else:
                form_src = host.vars
            self.host = host

            self.populate_host_options(selected)
            self.section_variable_fields(form_src)

    def signal_selectgroup_changed(self):
        if not self.manual:
            self.manual = True
            self.variable_section.deleteLater()
            self.clear_fields()
            self.selecthost.setCurrentIndex(-1)
            self.manual = False

            selected = self.selectgroup.currentText()
            group = self.projectinventory.get_group(selected)
            self.group = group
            self.populate_group_options(selected)
            form_src = group.vars
            self.section_variable_fields(form_src)

    def populate_host_options(self, selecthost: str):
        self.action_button.clicked.connect(self.signal_save_host)
        self.hostoptions_groupbox.setEnabled(True)
        self.groupoptions.setDisabled(True)
        if self.host is None:
            return
        if selecthost == "New Host":
            self.action_button.setText("Create Host")
            self.reject_button.setDisabled(True)
        else:
            self.action_button.setText("Update Host")
            self.reject_button.setDisabled(False)

            self.target_host_name.setText(selecthost)
            self.ansible_host.setText(self.host.vars.get("ansible_host", ""))

    def populate_group_options(self, selectgroup: str):
        self.action_button.clicked.connect(self.signal_save_group)
        self.hostoptions_groupbox.setDisabled(True)
        self.groupoptions.setEnabled(True)
        if selectgroup == "New Group":
            self.action_button.setText("Create Group")
            self.reject_button.setDisabled(True)
        else:
            self.action_button.setText("Update Group")
            self.reject_button.setDisabled(False)

            self.target_group_name.setText(self.selectgroup.currentText())
            self.current_group_children.clear()
            self.current_host_children.clear()

            # groups = []
            # for group in self.groups:
            #     if group.name == "all":
            #         continue
            #     groups.append(group.name)

            self.available_groups.clear()
            self.available_groups.addItem("NOT IMPLEMENTED")

            for child in self.group.children:
                self.current_group_children.addItem(child.name)
                self.available_groups.removeItem(self.available_groups.findText(child.name))

            # hosts = []
            # for host in self.hosts:
            #     hosts.append(host.name)
            self.available_hosts.clear()
            self.available_hosts.addItem("NOT IMPLEMENTED")

            for host in self.group.hosts:
                self.current_host_children.addItem(host.name)
                self.available_hosts.removeItem(self.available_hosts.findText(host.name))

    def signal_save_host(self):
        hostname = self.selecthost.currentText()
        host = self.projectinventory.get_host(hostname)
        if host is None:
            host, _ = self.projectinventory.add_host(hostname)

        var_vals = self.variable_section.findChildren(QLineEdit)
        for var in var_vals:
            if var.text():
                host.vars[var.objectName()] = var.text()

        host.name = self.target_host_name.text().strip()
        host.vars["ansible_host"] = self.ansible_host.text().strip()

        self.projectinventory.update_config()
        index = self.selecthost.currentIndex()
        self.selecthost.setItemText(index, host.name)

    def signal_save_group(self):
        groupname = self.selectgroup.currentText()
        group = self.projectinventory.get_group(groupname)
        if group is None:
            return

        var_vals = self.variable_section.findChildren(QLineEdit)
        for var in var_vals:
            group.vars[var.objectName()] = var.text()

        group.name = self.target_group_name.text().strip()
        self.projectinventory.update_config()
        index = self.selectgroup.currentIndex()
        self.selectgroup.setItemText(index, group.name)

    def signal_delete_item(self):
        if self.selectgroup.currentText():
            pass
        elif self.selecthost.currentText():
            if self.host is not None:
                self.projectinventory.delete_host(self.host)
                self.clear_fields()
                self.manual = True
                index = self.selecthost.currentIndex()
                self.manual = False
                self.selecthost.removeItem(index)

    # def signal_delete_child_host(self):
    #     selected = self.current_host_children.currentItem().text()
    #     host = self.projectinventory.get_host(selected)
    #     self.group.hosts.remove(host)
    #     self.current_host_children.takeItem(self.current_host_children.currentRow())
    #     self.available_hosts.addItem(selected)

    def clear_fields(self):
        self.target_host_name.setText("")
        self.ansible_host.setText("")
        self.target_group_name.setText("")
        self.available_groups.clear()
        self.current_host_children.clear()
        self.current_group_children.clear()
