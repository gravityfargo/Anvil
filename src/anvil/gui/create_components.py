import inspect
from typing import TypeVar, Callable
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

T = TypeVar("T")


def create_QComboBox(obj_name: str, options: list = []) -> QComboBox:
    """
    "{obj_name}_combobox"
    """
    combobox = QComboBox()
    combobox.setObjectName(f"{obj_name}_combobox")
    if len(options) > 0:
        combobox.addItems(options)
    combobox.addItem("")
    combobox.setCurrentIndex(-1)
    return combobox


def create_QLineEdit(obj_name: str, placeholder: str = "") -> QLineEdit:
    lineedit = QLineEdit()
    lineedit.setObjectName(obj_name)
    lineedit.setPlaceholderText(placeholder)
    return lineedit


def create_QPushButton(obj_name: str, text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(obj_name)
    return button


def create_QLabel(text: str, obj_name: str = None) -> QLabel:
    label = QLabel(text)
    if obj_name is not None:
        label.setObjectName(obj_name)
    return label


def create_QAction(
    parent_menu: QMenu, name: str, connection: Callable, obj_name: str = None
) -> QAction:
    action = QAction(name)
    action.triggered.connect(connection)
    parent_menu.addAction(action)
    if obj_name is not None:
        action.setObjectName(obj_name)
    return action


def create_QHBoxLayout(obj_name: str = None) -> QHBoxLayout:
    """Create a QHBoxLayout object with the given name."""
    layout = QHBoxLayout()
    if obj_name is not None:
        layout.setObjectName(obj_name)
    return layout


def create_QVBoxLayout(obj_name: str = None) -> QVBoxLayout:
    """Create a QVBoxLayout object with the given name."""
    layout = QVBoxLayout()
    if obj_name is not None:
        layout.setObjectName(obj_name)
    return layout


def create_QGroupBox(
    obj_name: str, title: str = "", layout: QLayout = QFormLayout
) -> tuple[QGroupBox, QFormLayout]:
    """Create a QGroupBox object with the given title and layout."""
    groupbox = QGroupBox(title)
    layout = layout()
    groupbox.setLayout(layout)
    groupbox.setStyleSheet("QGroupBox { padding: 10px; padding-top: 20px; }")

    groupbox.setObjectName(obj_name + "_groupbox")
    layout.setObjectName(obj_name + "_layout")

    return groupbox, layout


def create_QWidget(obj_name: str, layout: QLayout) -> tuple[QWidget, QLayout]:
    widget = QWidget()
    widget.setObjectName(obj_name + "_widget")
    layout = layout(widget)
    layout.setObjectName(obj_name + "_layout")
    return widget, layout


def create_QTabWidget(obj_name: str) -> QTabWidget:
    tab_widget = QTabWidget()
    tab_widget.setObjectName(obj_name)
    return tab_widget


def create_QTreeView(
    obj_name: str, root_path: str = ""
) -> tuple[QTreeView, QFileSystemModel]:
    model = QFileSystemModel()
    model.setRootPath(root_path)

    tree = QTreeView()
    tree.setModel(model)
    tree.setRootIndex(model.index(root_path))
    tree.setColumnWidth(0, 300)
    tree.hideColumn(1)
    tree.hideColumn(2)
    tree.hideColumn(3)
    tree.setMinimumWidth(350)
    tree.setMaximumWidth(400)
    tree.setObjectName(obj_name)
    return tree, model


def add_widgets(layout: QLayout, widgets: list, parent: QWidget = None) -> None:
    """Add a list of widgets to a layout.

    Args:
        layout (QLayout): Some layout object.
        widgets (list): A list of widgets.
    """
    if parent is None:
        parent = mw()
    for widget in widgets:
        widget.setParent(parent)
        layout.addWidget(widget)


def add_layouts(target_layout: QLayout, layouts: list) -> None:
    """Add a list of layouts to a layout.

    Args:
        layout (QLayout): Some layout object.
        layouts (list): A list of layouts.
    """
    for layout_ in layouts:
        target_layout.addLayout(layout_)


def add_Rows(
    layout: QFormLayout, items: list[tuple[str, QWidget]], parent=None
) -> None:
    if parent is None:
        parent = mw()
    for label, widget in items:
        widget.setParent(parent)
        layout.addRow(label, widget)


def get_child(parent: QWidget, obj_name: str, obj_type: T) -> T:
    """Get a child widget from a parent widget by object name."""
    for child in parent.children():
        if child.objectName() == obj_name:
            return child
    return None


def mw() -> QMainWindow:
    """Get the main window object."""
    parentframe = inspect.currentframe().f_back.f_back
    caller_self = parentframe.f_locals["self"]
    return caller_self
