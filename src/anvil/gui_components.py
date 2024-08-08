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
from anvil.utilities import Printer


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
        self.target_layout = target_layout
        new_layout.setObjectName(f"{section_name}_layout")
        setattr(self.parent_obj, new_layout.objectName(), new_layout)
        target_layout.addLayout(new_layout)

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

    def info(self):
        # print_attributes(self)
        pass
