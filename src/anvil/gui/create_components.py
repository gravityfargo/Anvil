from typing import Callable, Type, TypeVar

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFileSystemModel,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

T = TypeVar("T")
AnyLayout = TypeVar("AnyLayout", QVBoxLayout, QHBoxLayout, QFormLayout)


def create_QComboBox(obj_name: str, options: list) -> QComboBox:
    """
    "{obj_name}_combobox"
    """
    combobox = QComboBox()
    combobox.setObjectName(f"{obj_name}_combobox")
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


def create_QLabel(text: str, obj_name: str = "") -> QLabel:
    label = QLabel(text)
    if obj_name:
        label.setObjectName(obj_name)
    return label


def create_QCheckBox(obj_name: str, text: str) -> QCheckBox:
    checkbox = QCheckBox(text)
    checkbox.setObjectName(obj_name)
    return checkbox


def create_QSpacerItem(layout_type: QLayout) -> QSpacerItem:
    if isinstance(layout_type, QHBoxLayout):
        h = QSizePolicy.Policy.Expanding
        v = QSizePolicy.Policy.Minimum
    else:
        h = QSizePolicy.Policy.Minimum
        v = QSizePolicy.Policy.Expanding
    spacer = QSpacerItem(1, 1, h, v)
    return spacer


def create_QProgressBar(obj_name: str) -> QProgressBar:
    progress_bar = QProgressBar()
    progress_bar.setObjectName(obj_name)
    progress_bar.setRange(0, 100)
    progress_bar.setTextVisible(True)
    progress_bar.setMaximumHeight(20)
    return progress_bar


def create_QTextEdit(obj_name: str, setReadOnly: bool = False) -> QTextEdit:
    textedit = QTextEdit()
    textedit.setReadOnly(setReadOnly)
    textedit.setObjectName(obj_name)
    return textedit


def create_QAction(parent: QWidget, parent_menu: QMenu | QMenuBar, text: str, connection: Callable) -> QAction:
    action = QAction(text, parent)
    action.triggered.connect(connection)
    parent_menu.addAction(action)
    return action


def create_QFileDialog(directory_mode=False) -> QFileDialog:
    """
    fileNames: list[str] = []
    fileNames = dialog.selectedFiles()
    """
    dialog = QFileDialog()
    dialog.setViewMode(QFileDialog.ViewMode.Detail)
    if directory_mode:
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly)
    return dialog


def create_QHBoxLayout(obj_name: str = "") -> QHBoxLayout:
    """Create a QHBoxLayout object with the given name."""
    layout = QHBoxLayout()
    if obj_name:
        layout.setObjectName(obj_name)
    return layout


def create_QVBoxLayout(obj_name: str = "") -> QVBoxLayout:
    """Create a QVBoxLayout object with the given name."""
    layout = QVBoxLayout()
    if obj_name:
        layout.setObjectName(obj_name)
    return layout


def create_QFormLayout(obj_name: str = "") -> QFormLayout:
    """Create a QFormLayout object with the given name."""
    layout = QFormLayout()
    if obj_name:
        layout.setObjectName(obj_name)
    return layout


def create_QGroupBox(
    obj_name: str = "", title: str = "", layout_type: Type[AnyLayout] = QFormLayout
) -> tuple[QGroupBox, AnyLayout]:
    """
    - `(obj_name + "_groupbox")`
    - `(obj_name + "_groupbox_layout")`
    """
    groupbox = QGroupBox()
    groupbox.setStyleSheet("QGroupBox { margin: 10px; padding-top: 10px; }")
    layout = layout_type()
    groupbox.setLayout(layout)

    if title:
        groupbox.setTitle(title)
    if obj_name:
        groupbox.setObjectName(obj_name + "_groupbox")
        layout.setObjectName(obj_name + "_groupbox_layout")

    return groupbox, layout


def create_QWidget(obj_name: str = "", layout_type: Type[AnyLayout] = QVBoxLayout) -> tuple[QWidget, AnyLayout]:
    widget = QWidget()

    layout = layout_type()
    widget.setLayout(layout)

    if obj_name:
        widget.setObjectName(obj_name + "_widget")
        layout.setObjectName(obj_name + "_layout")
    return widget, layout


def create_QListWidget(obj_name: str) -> QListWidget:
    widget = QListWidget()
    widget.setObjectName(obj_name)
    return widget


def create_QTabWidget(obj_name: str, min_width: int = 0) -> QTabWidget:
    tab_widget = QTabWidget()
    tab_widget.setObjectName(obj_name)
    if min_width > 0:
        tab_widget.setMinimumWidth(min_width)
    return tab_widget


def create_QTreeView(obj_name: str, root_path: str = "") -> tuple[QTreeView, QFileSystemModel]:
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


# def get_child(parent: QWidget, obj_name: str, obj_type: T) -> T:
#     """Get a child widget from a parent widget by object name."""
#     for child in parent.children():
#         if child.objectName() == obj_name:
#             return child
#     return None


# def mw() -> QMainWindow:
#     """Get the main window object."""
#     parentframe = inspect.currentframe().f_back.f_back
#     caller_self = parentframe.f_locals["self"]
#     return caller_self


# def list_item_clicked(self):
#     sender = self.sender()
#     self.textedit.clear()
#     self.textedit.setTabStopDistance(24)

#     if sender is self.group_list:
#         self.host_list.clearSelection()
#         selected_group = self.project.inventory.get_group(
#             self.group_list.currentItem().text()
#         )
#         group_data = selected_group.to_dict()
#         var_data = yaml.dump(group_data, default_flow_style=False)
#         self.set_textedit_text(var_data, "black")

#     elif sender is self.host_list:
#         self.group_list.clearSelection()

# def set_textedit_text(self, text, color_name):
#     color_map = {
#         "red": QColor(192, 57, 43),
#         "green": QColor(39, 174, 96),
#         "yellow": QColor(241, 196, 15),
#         "purple": QColor(155, 89, 182),
#         "cyan": QColor(93, 173, 226),
#         "gray": QColor(149, 165, 166),
#         "black": QColor(23, 32, 42),
#     }
#     color = color_map.get(color_name, QColor(0, 0, 0))

#     charformat = QTextCharFormat()
#     charformat.setForeground(color)
#     cursor = self.textedit.textCursor()
#     cursor.movePosition(QTextCursor.MoveOperation.End)

#     cursor.insertText(text, charformat)
#     cursor.insertText("\n")

#     self.textedit.ensureCursorVisible()
