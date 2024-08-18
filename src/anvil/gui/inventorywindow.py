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
        self.section_variable_fields()

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
        self.action_button.clicked.connect(self.signal_save_host)
        self.action_button.clicked.connect(self.signal_save_group)
        # These connected functions requre an item with text to be selected in the
        # host/group dropdowns. Both functions will be called, but only the one that
        # corresponds to the selected item will have any effect. See the returns at the start
        # of each function.

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
        group_child_groups = create_QListWidget("group_children")

        available_hosts = create_QComboBox("child_hosts", [""])
        add_child_host = create_QPushButton("add_child_host", "Add Host")
        delete_child_host = create_QPushButton("delete_child_host", "Delete Host")
        group_child_hosts = create_QListWidget("group_hosts")

        add_child_host.clicked.connect(self.signal_add_child_host)
        delete_child_host.clicked.connect(self.signal_remove_child_host)

        groupbox_layout.addRow("Name", target_group_name)

        groupbox_layout.addRow("Groups", available_groups)
        btn = create_QHBoxLayout()
        btn.addWidget(add_child_group)
        btn.addWidget(delete_child_group)
        groupbox_layout.addRow(btn)
        groupbox_layout.addRow(group_child_groups)

        groupbox_layout.addRow("Hosts", available_hosts)
        btn = create_QHBoxLayout()
        btn.addWidget(add_child_host)
        btn.addWidget(delete_child_host)
        groupbox_layout.addRow(btn)
        groupbox_layout.addRow(group_child_hosts)

        self.groupoptions = groupbox
        self.target_group_name = target_group_name
        self.available_groups = available_groups
        self.available_hosts = available_hosts
        self.group_child_groups = group_child_groups
        self.group_child_hosts = group_child_hosts
        return groupbox

    def section_variable_fields(self):
        groupbox, groupbox_layout = create_QGroupBox("variables", "Variables")
        self.variable_section = groupbox

        self.primary_layout.addWidget(groupbox)

        label_src = Inventory.VARS.keys()
        for label in label_src:

            if label == "ansible_host":
                continue

            lineedit = create_QLineEdit(label)
            groupbox_layout.addRow(label, lineedit)

    # Signals

    def signal_selecthost_changed(self):
        if not self.manual:
            # reset the window
            self.manual = True
            self.clear_fields()
            self.selectgroup.setCurrentIndex(-1)
            self.manual = False

            selected = self.selecthost.currentText()
            form_src = None
            host = self.projectinventory.get_host(selected)

            if host is not None:
                form_src = host.vars

            self.host = host
            self.populate_host_options(selected)
            self.populate_variable_fields(form_src)

    def signal_selectgroup_changed(self):
        if not self.manual:
            # reset the window
            self.manual = True
            self.clear_fields()
            self.selecthost.setCurrentIndex(-1)
            self.manual = False

            selected = self.selectgroup.currentText()
            form_src = None
            group = self.projectinventory.get_group(selected)

            if group is not None:
                form_src = group.vars

            self.group = group
            self.populate_group_options(selected)
            self.populate_variable_fields(form_src)

    def populate_host_options(self, selecthost: str):
        # self.action_button.clicked.connect(self.signal_save_host)
        self.action_button.setEnabled(True)
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
        self.action_button.setEnabled(True)
        self.hostoptions_groupbox.setDisabled(True)
        self.groupoptions.setEnabled(True)
        if self.group is None:
            return

        if selectgroup == "New Group":
            self.action_button.setText("Create Group")
            self.reject_button.setDisabled(True)
        else:
            self.action_button.setText("Update Group")
            self.reject_button.setDisabled(False)

            self.target_group_name.setText(self.selectgroup.currentText())
            self.group_child_groups.clear()
            self.group_child_hosts.clear()

            self.available_groups.clear()
            self.available_groups.addItem("NOT IMPLEMENTED")

            for child in self.group.children:
                self.group_child_groups.addItem(child.name)
                self.available_groups.removeItem(self.available_groups.findText(child.name))

            hosts = []
            for host in self.hosts:
                hosts.append(host.name)
            self.available_hosts.clear()
            self.available_hosts.addItems(hosts)
            self.available_hosts.addItem("")
            self.available_hosts.setCurrentIndex(-1)

            for host in self.group.hosts:
                self.group_child_hosts.addItem(host.name)
                self.available_hosts.removeItem(self.available_hosts.findText(host.name))

    def populate_variable_fields(self, form_src: dict | None):
        if form_src is None:
            form_src = Inventory.VARS

        variable_line_edits = self.variable_section.findChildren(QLineEdit)
        for line_edit in variable_line_edits:
            object_name = line_edit.objectName()
            value = form_src.get(object_name, "")

            if object_name == "ansible_host":
                self.ansible_host.setText(value)
                continue

            line_edit.setText(value)

    def signal_save_host(self):
        hostname = self.selecthost.currentText()
        if not hostname:
            return

        host, _ = self.projectinventory.add_host(hostname)

        # update vars from form
        var_vals = self.variable_section.findChildren(QLineEdit)
        for var in var_vals:
            host.vars[var.objectName()] = var.text()

        host.name = self.target_host_name.text().strip()
        host.vars["ansible_host"] = self.ansible_host.text().strip()

        self.projectinventory.save_host(host)

        # update/add to dropdown
        self.manual = True
        if hostname == "New Host":
            self.selecthost.addItem(host.name)
        else:
            index = self.selecthost.currentIndex()
            self.selecthost.setItemText(index, host.name)
        self.manual = False

    def signal_save_group(self):
        groupname = self.selectgroup.currentText()
        if not groupname:
            return
        group, _ = self.projectinventory.add_group(groupname)

        # update vars from form
        var_vals = self.variable_section.findChildren(QLineEdit)
        for var in var_vals:
            group.vars[var.objectName()] = var.text()

        group.name = self.target_group_name.text().strip()
        self.projectinventory.save_group(group)

        # update/add to dropdown
        self.manual = True
        if groupname == "New Group":
            self.selectgroup.addItem(group.name)
        else:
            index = self.selectgroup.currentIndex()
            self.selectgroup.setItemText(index, group.name)
        self.manual = False

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

    def signal_add_child_host(self):
        selected = self.available_hosts.currentText()
        self.group_child_hosts.addItem(selected)
        self.manual = True
        self.available_hosts.removeItem(self.available_hosts.findText(selected))
        self.manual = False

    def signal_remove_child_host(self):
        selected = self.group_child_hosts.currentItem()
        index = self.group_child_hosts.row(selected)
        print(index)
        self.group_child_hosts.takeItem(index)
        self.manual = True
        self.available_hosts.addItem(selected.text())
        self.manual = False

    def clear_fields(self):
        self.target_host_name.setText("")
        self.ansible_host.setText("")
        self.target_group_name.setText("")
        self.available_groups.clear()
        self.group_child_hosts.clear()
        self.group_child_groups.clear()
