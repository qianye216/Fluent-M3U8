# coding:utf-8
from typing import Dict, List
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout

from qfluentwidgets import Pivot, FluentIcon, SegmentedWidget

from ..common.icon import Logo
from ..common.database import sqlRequest
from ..service.m3u8dl_service import m3u8Service, DownloadProgressInfo
from ..components.interface import Interface
from ..components.task_card import DownloadingTaskCard, Task, SuccessTaskCard, TaskCardBase
from ..components.empty_status_widget import EmptyStatusWidget


class TaskInterface(Interface):
    """ Task Interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitle(self.tr("Task"))

        self.pivot = SegmentedWidget()
        self.stackedWidget = QStackedWidget()
        self.downloadingTaskView = DownloadingTaskView(self)
        self.successTaskView = SuccessTaskView(self)
        self.emptyStatusWidget = EmptyStatusWidget(Logo.SMILEFACE, self.tr("Currently no download tasks"), self)

        self._initWidgets()

    def _initWidgets(self):
        self.setViewportMargins(0, 140, 0, 10)
        self.pivot.addItem("downloading", self.tr("Downloading"), icon=FluentIcon.SYNC)
        self.pivot.addItem("finished", self.tr("Finished"), icon=FluentIcon.COMPLETED)
        self.pivot.addItem("failed", self.tr("Failed"), icon=FluentIcon.INFO)
        self.pivot.setCurrentItem("downloading")

        self.emptyStatusWidget.setMinimumWidth(200)

        self.stackedWidget.addWidget(self.downloadingTaskView)
        self.stackedWidget.addWidget(self.successTaskView)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignmentFlag.AlignLeft)
        self.viewLayout.addWidget(self.stackedWidget)

    def _onTaskCreated(self, task: Task):
        self.downloadingTaskView.addTask(task)
        if self.stackedWidget.currentIndex() == 0:
            self.emptyStatusWidget.hide()

    def _onDownloadFinished(self, task: Task, isSuccess, errorMsg):
        self.downloadingTaskView.removeTask(task.pid)

        if isSuccess:
            self.successTaskView.addTask(task)
        else:
            pass

        self._updateEmptyStatus()

    def _onDownloadProgressChanged(self, pid, info: DownloadProgressInfo):
        card = self.downloadingTaskView.findCard(pid)
        if card:
            card.setInfo(info)

    def _onCoverSaved(self, pid):
        card = self.successTaskView.findCard(pid)
        if card:
            card.updateCover()

    def _onCurrentWidgetChanged(self):
        view = self.stackedWidget.currentWidget()   # type: TaskCardView
        self.pivot.setCurrentItem(view.objectName())
        self.emptyStatusWidget.setVisible(view.count() == 0)

    def _connectSignalToSlot(self):
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))
        self.stackedWidget.currentChanged.connect(self._onCurrentWidgetChanged)
        self.successTaskView.cardCountChanged.connect(self._updateEmptyStatus)

        m3u8Service.downloadCreated.connect(self._onTaskCreated)
        m3u8Service.downloadProcessChanged.connect(self._onDownloadProgressChanged)
        m3u8Service.downloadFinished.connect(self._onDownloadFinished)

        m3u8Service.coverSaved.connect(self._onCoverSaved)

    def _updateEmptyStatus(self):
        visible = self.stackedWidget.currentWidget().count() == 0
        self.emptyStatusWidget.setVisible(visible)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.emptyStatusWidget.adjustSize()
        w, h = self.emptyStatusWidget.width(), self.emptyStatusWidget.height()
        y = self.stackedWidget.y() + (self.height() - self.stackedWidget.y()) // 2 - h //2
        self.emptyStatusWidget.move(int(self.width()/2 - w/2), y)


class TaskCardView(QWidget):
    """ Download task view """

    cardCountChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cards = []     # type: List[TaskCardBase]
        self.cardMap = {}  # type: Dict[str, TaskCardBase]

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(30, 0, 30, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def createCard(self, task: Task) -> TaskCardBase:
        raise NotImplementedError

    def addTask(self, task: Task) -> TaskCardBase:
        card = self.createCard(task)
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

        self.cardCountChanged.emit(self.count())

    def findCard(self, pid):
        return self.cardMap.get(pid)

    def count(self):
        return len(self.cards)


class DownloadingTaskView(TaskCardView):
    """ Downloading task view """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("downloading")

    def createCard(self, task: Task):
        return DownloadingTaskCard(task, self)


class SuccessTaskView(TaskCardView):
    """ Success task view """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("finished")

        # load cards
        sqlRequest("taskService", "listAll", self._loadTasks)

    def _loadTasks(self, tasks: List[Task]):
        if not tasks:
            return

        for task in tasks:
            self.addTask(task)

        self.cardCountChanged.emit(self.count())

    def createCard(self, task: Task):
        return SuccessTaskCard(task, self)
