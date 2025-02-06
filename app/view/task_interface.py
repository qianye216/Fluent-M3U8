# coding:utf-8
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from ..components.interface import Interface
from qfluentwidgets import Pivot, FluentIcon, SegmentedWidget


class TaskInterface(Interface):
    """ Task Interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitle(self.tr("Task"))

        self.pivot = SegmentedWidget()

        self._initWidgets()

    def _initWidgets(self):
        self.pivot.addItem("downloading", self.tr("Downloading"), icon=FluentIcon.SYNC)
        self.pivot.addItem("finished", self.tr("Finished"), icon=FluentIcon.COMPLETED)
        self.pivot.addItem("failed", self.tr("Failed"), icon=FluentIcon.INFO)
        self.pivot.setCurrentItem("downloading")

        self._initLayout()

    def _initLayout(self):
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)