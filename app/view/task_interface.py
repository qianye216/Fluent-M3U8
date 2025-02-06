# coding:utf-8
from typing import Dict, List
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout

from qfluentwidgets import Pivot, FluentIcon, SegmentedWidget

from ..service.m3u8dl_service import m3u8Service, DownloadProgressInfo
from ..components.interface import Interface
from ..components.task_card import DownloadingTaskCard, Task


class TaskInterface(Interface):
    """ Task Interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitle(self.tr("Task"))

        self.pivot = SegmentedWidget()
        self.stackedWidget = QStackedWidget()
        self.downloadingTaskView = DownloadingTaskView(self)

        self._initWidgets()

    def _initWidgets(self):
        self.setViewportMargins(0, 140, 0, 10)
        self.pivot.addItem("downloading", self.tr("Downloading"), icon=FluentIcon.SYNC)
        self.pivot.addItem("finished", self.tr("Finished"), icon=FluentIcon.COMPLETED)
        self.pivot.addItem("failed", self.tr("Failed"), icon=FluentIcon.INFO)
        self.pivot.setCurrentItem("downloading")

        self.stackedWidget.addWidget(self.downloadingTaskView)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)
        self.viewLayout.addWidget(self.stackedWidget)

    def _onDownloadFinished(self, pid, isSuccess, errorMsg):
        self.downloadingTaskView.removeTask(pid)
        if isSuccess:
            pass

    def _onDownloadProgressChanged(self, pid, info: DownloadProgressInfo):
        card = self.downloadingTaskView.findCard(pid)
        if card:
            card.setInfo(info)

    def _connectSignalToSlot(self):
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

        m3u8Service.downloadCreated.connect(self.downloadingTaskView.addTask)
        m3u8Service.downloadProcessChanged.connect(self._onDownloadProgressChanged)
        m3u8Service.downloadFinished.connect(self._onDownloadFinished)


class DownloadingTaskView(QWidget):
    """ Download task view """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("downloading")
        self.cards = []     # type: List[DownloadingTaskCard]
        self.cardMap = {}  # type: Dict[str, DownloadingTaskCard]

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(30, 0, 30, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def addTask(self, task: Task):
        card = DownloadingTaskCard(task, self)
        card.deleted.connect(self.removeTask)
        
        self.vBoxLayout.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        self.cards.append(card)
        self.cardMap[task.pid] = card

    def removeTask(self, pid: int):
        if pid not in self.cardMap:
            return

        card = self.cardMap.pop(pid)
        self.cards.remove(card)
        self.vBoxLayout.removeWidget(card)
        card.hide()
        card.deleteLater()

    def findCard(self, pid):
        return self.cardMap.get(pid)