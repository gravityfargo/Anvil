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
    QLayout,
    QSizePolicy,
    QMenu,
    QTabWidget,
)
from PySide6.QtGui import QTextCharFormat, QTextCursor, QColor, QAction
from core.classes import Printer


class CreateCompentent:
    def __init__(
        self, parent_obj, target_layout: QLayout, working_layout: QLayout, prefix: str
    ):
        self.parent_obj = parent_obj
        self.p = parent_obj.ad.p
        self.p.obj("class", "CreateCompentent")
        self.prefix = prefix
        self.target_layout = target_layout

        self.working_layout = working_layout
        self.working_widget = None

        self.primary_layout = None
        self.primary_widget = None

        target_layout.addLayout(working_layout)

    def set(self, objs: list[QWidget | QLayout]):
        for obj in objs:
            if issubclass(type(obj), QWidget):
                if self.primary_widget is None:
                    self.primary_widget = obj
                self.working_widget = obj

            elif issubclass(type(obj), QLayout):
                if self.primary_layout is None:
                    self.primary_layout = obj
                self.working_layout = obj

    def put_into_layout(self, obj: QWidget | QLayout, desciption: str = ""):
        if isinstance(self.working_layout, QFormLayout):
            if desciption != "":
                self.working_layout.addRow(desciption, obj)
                return
            self.working_layout.addRow(obj)

        elif type(self.working_layout) in (QVBoxLayout, QHBoxLayout):
            self.working_layout.addWidget(obj)

        self.set(widget=obj)

    def create_layout(
        self, layout_type: QVBoxLayout | QHBoxLayout = QVBoxLayout, name: str = None
    ):
        """
        `{prefix}_{name}_layout`
        """
        p = Printer("function", "create_layout()")
        layout = layout_type()
        obj_name = "temp_layout"

        if isinstance(self.working_layout, QFormLayout):
            self.working_layout.addItem(layout)
        else:
            self.working_layout.addLayout(layout)

        if name is not None:
            obj_name = f"{self.prefix}_{name}_layout"
            setattr(self.parent_obj, obj_name, layout)

        layout.setObjectName(obj_name)
        self.set(layout=layout)

        p.changed(layout.objectName())

    def container_tab(self, tab_name: str):
        """
        `{prefix}_tab` \n
        `{prefix}_tab_layout`
        """
        p = Printer("function", "container_tab()")
        tab = QWidget()
        tab.setObjectName(f"{self.prefix}_tab")
        layout = QVBoxLayout(tab)
        layout.setObjectName(f"{self.prefix}_tab_layout")
        self.working_widget.addTab(tab, tab_name)
        self.set(tab, layout)
        p.changed(tab.objectName())

    def create_container_tabs(self) -> QTabWidget:
        """
        `{prefix}_tab_widget`
        """
        p = Printer("function", "container_tabs()")
        tab_widget = QTabWidget()
        tab_widget.setObjectName(f"{self.prefix}_tab_widget")
        self.set_attr_safe(tab_widget.objectName(), tab_widget, QTabWidget)
        self.add_widget(tab_widget)
        p.changed(tab_widget.objectName())
        return tab_widget

        # pdebug([["container_tabs()", "cyan"], [tab_widget.objectName(), "yellow"]])

    def create_container_groupbox(self, title: str = ""):
        """
        widget and layout.
            `{prefix}_groupbox` \n
            `{prefix}_groupbox_layout`
        """
        p = Printer("function", "container_groupbox()")
        groupbox = QGroupBox(title)
        layout = QFormLayout(groupbox)
        groupbox.setObjectName(f"{self.prefix}_groupbox")
        layout.setObjectName(f"{self.prefix}_groupbox_layout")
        setattr(self.parent_obj, groupbox.objectName(), groupbox)
        setattr(self.parent_obj, layout.objectName(), layout)

        self.set([groupbox, layout])
        p.changed(groupbox.objectName())

    def container_widget(self):
        """
        widget and layout.
            `{prefix}_widget` \n
            `{prefix}_widget_layout`
        """
        p = Printer("function", "container_widget()")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        widget.setObjectName(f"{self.prefix}_widget")
        layout.setObjectName(f"{self.prefix}_widget_layout")
        setattr(self.parent_obj, widget.objectName(), widget)
        setattr(self.parent_obj, layout.objectName(), layout)
        self.working_layout.addWidget(widget)
        self.set(widget, layout)
        p.changed(widget.objectName())

    def create_qaction(
        self, parent_menu: QMenu, name: str, connection: Callable, obj_name: str = None
    ):
        p = Printer("function", "create_qaction()")
        action = QAction(name, self)
        action.triggered.connect(connection)
        parent_menu.addAction(action)
        if obj_name is not None:
            action.setObjectName(obj_name)
        p.changed(action.objectName())

    def create_progress_bar(self, parent_layout: QVBoxLayout):
        p = Printer("function", "create_progress_bar()")
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(True)
        progress_bar.setMaximumHeight(20)
        setattr(self.parent_obj, "progress_bar", progress_bar)
        parent_layout.addWidget(progress_bar)
        p.changed("progress_bar")

    def create_checkbox(self, parent_layout: QVBoxLayout, name: str, desciption: str):
        p = Printer("function", "create_checkbox()")
        checkbox = QCheckBox(desciption)
        suffix = desciption.lower().replace(" ", "_")
        checkbox.setObjectName(f"{name}_checkbox_{suffix}")
        setattr(self.parent_obj, checkbox.objectName(), checkbox)
        if isinstance(parent_layout, QFormLayout):
            parent_layout.addRow(checkbox)
        elif type(parent_layout) in (QVBoxLayout, QHBoxLayout):
            parent_layout.addWidget(checkbox)
        p.changed(checkbox.objectName())

    def create_expanding_spacer(self):
        p = Printer("function", "create_expanding_spacer()")
        if isinstance(self.working_layout, QHBoxLayout):
            h = QSizePolicy.Policy.Expanding
            v = QSizePolicy.Policy.Minimum
        else:
            h = QSizePolicy.Policy.Minimum
            v = QSizePolicy.Policy.Expanding
        spacer = QSpacerItem(1, 1, h, v)
        if isinstance(self.working_layout, QFormLayout):
            self.working_layout.addItem(spacer)
        else:
            self.working_layout.addSpacerItem(spacer)
        p.changed("spacer")

    def create_button(self, text: str):
        """
        Create a QPushButton with the given text and objectName

        objectName = `{prefix}_button_{text}`
        """
        p = Printer("function", "create_button()")
        button = QPushButton(text)
        suffix = text.lower().replace(" ", "_")
        button.setObjectName(f"{self.prefix}_button_{suffix}")
        setattr(self.parent_obj, button.objectName(), button)
        button.clicked.connect(self.parent_obj.signal_connect_button)
        self.add_widget(button)
        p.changed(button.objectName())

    def create_lineedit(self, purpose: str, ph: str = ""):
        """
        `{prefix}_lineedit_{purpose}`
        """
        p = Printer("function", "create_lineedit()")
        lineedit = QLineEdit()
        lineedit.setObjectName(f"{self.prefix}_lineedit_{purpose}")
        lineedit.setPlaceholderText(ph)
        setattr(self.parent_obj, lineedit.objectName(), lineedit)
        self.add_widget(lineedit)
        p.changed(lineedit.objectName())

    def create_combobox(self, purpose: str, desciption: str = "", options: list = []):
        """
        Create a QComboBox with the given options and objectName

        objectName = `{prefix}_combobox_{purpose}`
        """
        p = Printer("function", "create_combobox()")
        combobox = QComboBox()
        combobox.setObjectName(f"{self.prefix}_combobox_{purpose}")
        # setattr(self.parent_obj, combobox.objectName(), combobox)
        self.set_attr_safe(combobox.objectName(), combobox, QComboBox)
        if len(options) > 0:
            combobox.addItems(options)
        combobox.addItem("")
        combobox.setCurrentIndex(-1)
        combobox.currentIndexChanged.connect(
            self.parent_obj.signal_combobox_index_changed
        )
        self.add_widget(combobox, desciption)
        p.changed(combobox.objectName())
