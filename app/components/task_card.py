# coding:utf-8
from pathlib import Path
import sys
from PySide6.QtCore import Qt, Signal, Property, QFileInfo, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileIconProvider

from qfluentwidgets import (SimpleCardWidget, IconWidget, ToolButton, FluentIcon,
                            BodyLabel, CaptionLabel, ProgressBar, ImageLabel, setFont,
                            MessageBoxBase, SubtitleLabel, CheckBox, InfoBar, InfoBarPosition,
                            PushButton, ToolTipFilter)

from ..common.utils import showInFolder, removeFile, openUrl
from ..common.database.entity import Task
from ..common.signal_bus import signalBus
from ..common.database import sqlRequest
from ..service.download_task_service import downloadTaskService
from ..service.m3u8dl_service import DownloadProgressInfo, m3u8Service


class TaskCardBase(SimpleCardWidget):
    """ Task card base class """

    deleted = Signal(Task)


class DownloadingTaskCard(TaskCardBase):
    """ Task card """

    def __init__(self, task: Task, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()

        self.task = task
        self.imageLabel = ImageLabel()
        self.fileNameLabel = BodyLabel(task.fileName)
        self.progressBar = ProgressBar()

        self.speedIcon = IconWidget(FluentIcon.SPEED_HIGH)
        self.speedLabel = CaptionLabel("0MB/s")
        self.remainTimeIcon = IconWidget(FluentIcon.STOP_WATCH)
        self.remainTimeLabel = CaptionLabel("00:00:00")
        self.sizeIcon = IconWidget(FluentIcon.BOOK_SHELF)
        self.sizeLabel = CaptionLabel("0MB/0MB")

        self.openFolderButton = ToolButton(FluentIcon.FOLDER)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

        self._initWidget()

    def _initWidget(self):
        self.imageLabel.setImage(QFileIconProvider().icon(
            QFileInfo(self.task.videoPath)).pixmap(32, 32))
        self.speedIcon.setFixedSize(16, 16)
        self.remainTimeIcon.setFixedSize(16, 16)
        self.sizeIcon.setFixedSize(16, 16)

        setFont(self.fileNameLabel, 18, QFont.Weight.Bold)
        self.fileNameLabel.setWordWrap(True)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.addWidget(self.imageLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addSpacing(20)
        self.hBoxLayout.addWidget(self.openFolderButton)
        self.hBoxLayout.addWidget(self.deleteButton)

        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)
        self.vBoxLayout.addWidget(self.progressBar)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(3)
        self.infoLayout.addWidget(self.speedIcon)
        self.infoLayout.addWidget(self.speedLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.remainTimeIcon)
        self.infoLayout.addWidget(self.remainTimeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addStretch(1)

    def _connectSignalToSlot(self):
        self.openFolderButton.clicked.connect(self._onOpenButtonClicked)
        self.deleteButton.clicked.connect(self._onDeleteButtonClicked)

    def _onOpenButtonClicked(self):
        path = Path(self.task.saveFolder) / self.task.fileName
        showInFolder(path)

    def _onDeleteButtonClicked(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        if w.exec():
            self.deleted.emit(self.task)
            downloadTaskService.removeDownloadingTask(self.task, w.deleteFileCheckBox.isChecked())

        w.deleteLater()

    def setInfo(self, info: DownloadProgressInfo):
        """ update progress info """
        self.speedLabel.setText(info.speed)
        self.remainTimeLabel.setText(info.remainTime)
        self.sizeLabel.setText(f"{info.currentSize}/{info.totalSize}")

        self.progressBar.setRange(0, info.totalChunks)
        self.progressBar.setValue(info.currentChunk)


class SuccessTaskCard(TaskCardBase):

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()

        self.task = task
        self.imageLabel = ImageLabel()
        self.fileNameLabel = BodyLabel(task.fileName)

        self.createTimeIcon = IconWidget(FluentIcon.DATE_TIME)
        self.createTimeLabel = CaptionLabel(
            task.createTime.toString("yyyy-MM-dd hh:mm:ss"))
        self.sizeIcon = IconWidget(FluentIcon.BOOK_SHELF)
        self.sizeLabel = CaptionLabel(task.size)

        self.redownloadButton = ToolButton(FluentIcon.UPDATE)
        self.openFolderButton = ToolButton(FluentIcon.FOLDER)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

        self._initWidget()

    def _initWidget(self):
        self.imageLabel.setBorderRadius(4, 4, 4, 4)
        self.createTimeIcon.setFixedSize(16, 16)
        self.sizeIcon.setFixedSize(16, 16)

        self.redownloadButton.setToolTip(self.tr("Restart"))
        self.redownloadButton.setToolTipDuration(3000)
        self.redownloadButton.installEventFilter(ToolTipFilter(self.redownloadButton))

        setFont(self.fileNameLabel, 18, QFont.Weight.Bold)
        self.fileNameLabel.setWordWrap(True)

        if self.task.coverPath.exists():
            self.updateCover()

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.addWidget(self.imageLabel)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addSpacing(20)
        self.hBoxLayout.addWidget(self.redownloadButton)
        self.hBoxLayout.addWidget(self.openFolderButton)
        self.hBoxLayout.addWidget(self.deleteButton)

        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(3)
        self.infoLayout.addWidget(self.createTimeIcon)
        self.infoLayout.addWidget(self.createTimeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(8)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addStretch(1)

    def updateCover(self):
        self.imageLabel.setImage(str(self.task.coverPath))
        self.imageLabel.setScaledSize(QSize(112, 63))

    def _onOpenButtonClicked(self):
        exist = showInFolder(self.task.videoPath)
        if not exist:
            InfoBar.error(
                title=self.tr("Open failed"),
                content=self.tr("Video file have been deleted"),
                duration=2000,
                parent=self.window().taskInterface
            )

    def _onDeleteButtonClicked(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        w.deleteFileCheckBox.setChecked(False)

        if w.exec():
            self.deleted.emit(self.task)
            downloadTaskService.removedSuccessTask(self.task, w.deleteFileCheckBox.isChecked())

        w.deleteLater()

    def _onRedownloadButtonClicked(self):
        signalBus.redownloadTask.emit(self.task)

    def _connectSignalToSlot(self):
        self.openFolderButton.clicked.connect(self._onOpenButtonClicked)
        self.deleteButton.clicked.connect(self._onDeleteButtonClicked)
        self.redownloadButton.clicked.connect(self._onRedownloadButtonClicked)


class FailedTaskCard(TaskCardBase):

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()

        self.task = task
        self.imageLabel = ImageLabel()
        self.fileNameLabel = BodyLabel(task.fileName)

        self.createTimeIcon = IconWidget(FluentIcon.DATE_TIME)
        self.createTimeLabel = CaptionLabel(
            task.createTime.toString("yyyy-MM-dd hh:mm:ss"))
        self.sizeIcon = IconWidget(FluentIcon.BOOK_SHELF)
        self.sizeLabel = CaptionLabel(task.size)

        self.redownloadButton = ToolButton(FluentIcon.UPDATE)
        self.logButton = ToolButton(FluentIcon.COMMAND_PROMPT)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

        self._initWidget()

    def _initWidget(self):
        self.imageLabel.setImage(QFileIconProvider().icon(
            QFileInfo(self.task.videoPath)).pixmap(32, 32))
        self.createTimeIcon.setFixedSize(16, 16)
        self.sizeIcon.setFixedSize(16, 16)

        self.redownloadButton.setToolTip(self.tr("Restart"))
        self.redownloadButton.setToolTipDuration(3000)
        self.redownloadButton.installEventFilter(
            ToolTipFilter(self.redownloadButton))

        self.logButton.setToolTip(self.tr("View log"))
        self.logButton.setToolTipDuration(3000)
        self.logButton.installEventFilter(ToolTipFilter(self.logButton))

        setFont(self.fileNameLabel, 18, QFont.Weight.Bold)
        self.fileNameLabel.setWordWrap(True)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.addWidget(self.imageLabel)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addSpacing(20)
        self.hBoxLayout.addWidget(self.redownloadButton)
        self.hBoxLayout.addWidget(self.logButton)
        self.hBoxLayout.addWidget(self.deleteButton)

        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(3)
        self.infoLayout.addWidget(self.createTimeIcon)
        self.infoLayout.addWidget(self.createTimeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(8)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addStretch(1)

    def _onLogButtonClicked(self):
        openUrl(self.task.logFile)

    def _onDeleteButtonClicked(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        if w.exec():
            self.deleted.emit(self.task)
            downloadTaskService.removeFailedTask(self.task, w.deleteFileCheckBox.isChecked())

        w.deleteLater()

    def _onRedownloadButtonClicked(self):
        signalBus.redownloadTask.emit(self.task)

    def _connectSignalToSlot(self):
        self.logButton.clicked.connect(self._onLogButtonClicked)
        self.deleteButton.clicked.connect(self._onDeleteButtonClicked)
        self.redownloadButton.clicked.connect(self._onRedownloadButtonClicked)


class DeleteTaskDialog(MessageBoxBase):

    def __init__(self, parent=None, showCheckBox=True, deleteOnClose=True):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr("Delete task"), self)
        self.contentLabel = BodyLabel(
            self.tr("Are you sure to delete this task?"), self)
        self.deleteFileCheckBox = CheckBox(self.tr("Remove file"), self)

        self.deleteFileCheckBox.setVisible(showCheckBox)

        if deleteOnClose:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self._initWidgets()

    def _initWidgets(self):
        self.deleteFileCheckBox.setChecked(True)
        self.widget.setMinimumWidth(330)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleLabel)
        layout.addSpacing(12)
        layout.addWidget(self.contentLabel)
        layout.addSpacing(10)
        layout.addWidget(self.deleteFileCheckBox)
        self.viewLayout.addLayout(layout)