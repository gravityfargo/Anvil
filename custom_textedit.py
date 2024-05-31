import sys, subprocess, os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from cli.file_utils import YamlManager


class CustomTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setTabSize(4)  # Set tab size to 4 spaces

    def setTabSize(self, spaces):
        font_metrics = QFontMetrics(self.font())
        self.setTabStopDistance(font_metrics.horizontalAdvance(" ") * spaces)
