from typing import Callable
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
from core.helpers import print_attributes


class MakeSection:
    def __init__(
        self,
        parent_obj,
        target_layout: QLayout,
        new_layout: QLayout,
        section_name: str,
        mute: bool = False,
    ):
        self.parent_obj = parent_obj
        self.p = Printer("class", "MakeSection")
        self.p.mute = mute
        self.p.set("function", "__init__")

        self.target_layout = target_layout
        new_layout.setObjectName(f"{section_name}_layout")
        setattr(self.parent_obj, new_layout.objectName(), new_layout)
        self.p.created(new_layout.objectName())

        target_layout.addLayout(new_layout)

        self.active_layout = new_layout
        self.active_widget = None

        self.layouts = []
        self.widgets = []
        self.layouts.append(target_layout)
        self.layouts.append(new_layout)

        self.primary_layout = None
        self.primary_widget = None

        self.prefix = None
        self.insert_mode = False
        """ When true, all subsequent widgets/layouts created will be inserted into `self.primary_layout` """

    def _process(self, **kwargs):
        layout = kwargs.get("layout")
        widget = kwargs.get("widget")
        desciption = kwargs.get("desciption", "")

        if self.insert_mode:
            if widget:
                self.insert(widget, desciption)
            elif layout:
                self.insert(layout, desciption)

        input_widgets = [QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox]
        if widget and type(widget) not in input_widgets:
            self.prefix = widget.objectName().split("_")[0]
            self.set_active([widget, layout])

        if layout and not widget:
            self.set_active(layout)

        if widget:
            self.widgets.append(widget)
            if self.primary_widget is None:
                self.primary_widget = widget
        if layout:
            self.layouts.append(layout)
            if self.primary_layout is None:
                self.primary_layout = layout

    def last(self, option):
        """
        Sets the active widget or layout to the previous one. \n
        """

        if option == "layout":
            self.layouts.pop()
            self.set_active(self.layouts[-1])
        elif option == "widget":
            self.widgets.pop()
            self.set_active(self.widgets[-1])

    def set_active(self, data: list[QWidget | QLayout] | str | QWidget | QLayout):
        """
        Set the active widget or layout to the given object(s) for manipulation. \n
        If a string is given, it will be converted to the object first.
        """
        self.p.set("function", "set_active")
        objs = data
        if isinstance(data, str):
            objs = [getattr(self.parent_obj, data)]
        if not isinstance(objs, list):
            objs = [data]
        for obj in objs:
            if obj is None:
                continue

            if issubclass(type(obj), QWidget):
                self.active_widget = obj
            if issubclass(type(obj), QLayout):
                self.active_layout = obj

            if obj.objectName() == "":
                obj_name = type(obj).__name__
            else:
                obj_name = obj.objectName()
            self.p.ok(obj_name, "ACTIVE:")

    def insert(self, obj: QWidget | QLayout, desciption: str = ""):
        """
        Insert a widget or layout into the active layout. \n
        If the active layout is a form layout, the description will be added as a label.
        """
        self.p.set("function", "insert")
        obj_name = obj.objectName()
        active_layout_name = self.active_layout.objectName()
        if obj.objectName() == "":
            obj_name = type(obj).__name__
        if self.active_layout.objectName() == "":
            active_layout_name = type(self.active_layout).__name__

        if len(self.widgets) > 0:
            if isinstance(self.widgets[-1], QTabWidget):
                if isinstance(obj, QWidget):
                    self.primary_widget.addTab(obj, desciption)
                    self.p.inserted(
                        f"{obj_name} -> {self.primary_widget.objectName()}", "ADDEDTAB"
                    )
                    return

        if isinstance(self.active_layout, QFormLayout):
            if desciption != "":
                self.active_layout.addRow(desciption, obj)
            else:
                if isinstance(obj, QWidget):
                    self.active_layout.addWidget(obj)
                elif isinstance(obj, QLayout):
                    self.active_layout.addRow(obj)

        elif type(self.active_layout) in (QVBoxLayout, QHBoxLayout):
            if issubclass(type(obj), QWidget):
                self.active_layout.addWidget(obj)
            elif issubclass(type(obj), QLayout):
                self.active_layout.addLayout(obj)
        self.p.inserted(f"{obj_name} -> {active_layout_name}")

    def qgroupbox(
        self, obj_name: str, title: str = ""
    ) -> tuple[QGroupBox, QFormLayout]:
        """
        Creates a QGroupBox with a QFormLayout inside. \n
        """
        self.p.set("function", "qgroupbox")
        groupbox = QGroupBox(title)
        layout = QFormLayout()
        # if not self.insert_mode:
        groupbox.setLayout(layout)

        groupbox.setObjectName(obj_name)
        layout.setObjectName(f"{obj_name}_layout")
        setattr(self.parent_obj, groupbox.objectName(), groupbox)
        setattr(self.parent_obj, layout.objectName(), layout)
        self.p.created(f"{groupbox.objectName()} & {layout.objectName()}")
        self._process(layout=layout, widget=groupbox)
        return groupbox, layout

    def qwidget(
        self, obj_name: str, layout: QLayout, desciption: str = ""
    ) -> tuple[QWidget, QLayout]:
        """
        Creates a QWidget with a layout inside. \n
        Optional desciption for being a tab. \n
        """
        self.p.set("function", "qwidget")
        widget = QWidget()
        layout = layout(widget)
        widget.setObjectName(obj_name)
        layout.setObjectName(f"{obj_name}_layout")
        setattr(self.parent_obj, widget.objectName(), widget)
        setattr(self.parent_obj, layout.objectName(), layout)
        self.p.created(f"{widget.objectName()} & {layout.objectName()}")
        self._process(layout=layout, widget=widget, desciption=desciption)
        return widget, layout

    def qtabwidget(self, obj_name: str) -> QTabWidget:
        """
        `{obj_name}_tab_widget`
        """
        self.p.set("function", "qtabwidget")
        tab_widget = QTabWidget()
        tab_widget.setObjectName(obj_name)
        setattr(self.parent_obj, tab_widget.objectName(), tab_widget)
        self.p.created(tab_widget.objectName())
        self._process(widget=tab_widget)
        return tab_widget

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

    def qspaceritem(self):
        p = Printer("function", "qspaceritem")
        if isinstance(self.active_layout, QHBoxLayout):
            h = QSizePolicy.Policy.Expanding
            v = QSizePolicy.Policy.Minimum
        else:
            h = QSizePolicy.Policy.Minimum
            v = QSizePolicy.Policy.Expanding
        spacer = QSpacerItem(1, 1, h, v)
        if isinstance(self.active_layout, QFormLayout):
            self.active_layout.addItem(spacer)
        else:
            self.active_layout.addSpacerItem(spacer)
        p.changed("spacer")

    def qpushbutton(self, obj_name: str, text: str) -> QPushButton:
        """
        Create a QPushButton with the given text and objectName
        """
        self.p.set("function", "qpushbutton")
        button = QPushButton(text)
        button.setObjectName(obj_name)
        setattr(self.parent_obj, button.objectName(), button)
        button.clicked.connect(self.parent_obj.signal_connect_button)
        self.p.changed(button.objectName())
        self._process(widget=button)
        return button

    def qlineedit(self, obj_name: str, ph: str = "", desciption: str = "") -> QLineEdit:
        """
        Create a QLineEdit with the given placeholder text and objectName
        """
        self.p.set("function", "qlineedit")
        lineedit = QLineEdit()
        lineedit.setObjectName(obj_name)
        lineedit.setPlaceholderText(ph)
        setattr(self.parent_obj, lineedit.objectName(), lineedit)
        self.p.created(lineedit.objectName())
        self._process(widget=lineedit, desciption=desciption)
        return lineedit

    def qcombobox(
        self, obj_name: str, desciption: str = "", options: list = []
    ) -> QComboBox:
        """
        Create a QComboBox with the given options and objectName

        objectName = `{obj_name}_combobox`
        """
        self.p.set("function", "qcombobox")
        combobox = QComboBox()
        combobox.setObjectName(f"{obj_name}_combobox")
        setattr(self.parent_obj, combobox.objectName(), combobox)
        if len(options) > 0:
            combobox.addItems(options)
        combobox.addItem("")
        combobox.setCurrentIndex(-1)
        combobox.currentIndexChanged.connect(
            self.parent_obj.signal_combobox_index_changed
        )
        self.p.created(combobox.objectName())
        self._process(widget=combobox)
        return combobox

    def qlayout(self, layout_type: QLayout = QVBoxLayout, name: str = None) -> QLayout:
        """
        `{prefix}_{name}_layout`
        """
        self.p.set("function", "qlayout")
        layout = layout_type()
        if name is not None:
            obj_name = f"{self.prefix}_{name}_layout"
            layout.setObjectName(obj_name)
            setattr(self.parent_obj, obj_name, layout)
        else:
            obj_name = layout_type.__name__
        self.p.created(obj_name)
        self._process(layout=layout)
        return layout

    def qlabel(self, obj_name: str, text: str) -> QLabel:
        """
        Create a QLabel with the given text and objectName

        `{obj_name}_label`
        """
        self.p.set("function", "QLabel")
        label = QLabel(text)
        label.setObjectName(obj_name)
        setattr(self.parent_obj, label.objectName(), label)
        self.p.created(label.objectName())
        self._process(widget=label)
        return label

    def info(self):
        print_attributes(self)
