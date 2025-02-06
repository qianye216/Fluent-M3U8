# coding:utf-8
from dataclasses import dataclass
from pathlib import Path
from PySide6.QtCore import Qt, Signal, Property, QFileInfo
from PySide6.QtGui import QPixmap, QPainter, QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileIconProvider

from qfluentwidgets import (SimpleCardWidget, IconWidget, ToolButton, FluentIcon,
                            BodyLabel, CaptionLabel, ProgressBar, ImageLabel, setFont,
                            MessageBoxBase, SubtitleLabel, CheckBox)

from ..common.utils import showInFolder
from ..common.database.entity import Task
from ..common.signal_bus import signalBus
from ..service.m3u8dl_service import DownloadProgressInfo, m3u8Service


class DownloadingTaskCard(SimpleCardWidget):
    """ Task card """

    deleted = Signal(int)

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
        self.speedLabel = CaptionLabel()
        self.remainTimeIcon = IconWidget(FluentIcon.STOP_WATCH)
        self.remainTimeLabel = CaptionLabel()
        self.sizeIcon = IconWidget(FluentIcon.PIE_SINGLE)
        self.sizeLabel = CaptionLabel()

        self.openFolderButton = ToolButton(FluentIcon.FOLDER)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

        self._initWidget()

    def _initWidget(self):
        self.imageLabel.setImage(QFileIconProvider().icon(
            QFileInfo(self.task.fileName)).pixmap(32, 32))
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

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)
        self.vBoxLayout.addWidget(self.progressBar)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(2)
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
        path = Path(m3u8Service.downloaderPath).parent / self.task.fileName
        showInFolder(path)

    def _onDeleteButtonClicked(self):
        w = DeleteTaskDialog(self.window())
        if w.exec():
            signalBus.downloadTerminated.emit(self.task.pid, w.deleteFileCheckBox.isChecked())
            self.deleted.emit(self.task.pid)

        w.deleteLater()

    def setInfo(self, info: DownloadProgressInfo):
        """ update progress info """
        self.speedLabel.setText(info.speed)
        self.remainTimeLabel.setText(info.remainTime)
        self.sizeLabel.setText(f"{info.currentSize}/{info.totalSize}")

        self.progressBar.setRange(0, info.totalChunks)
        self.progressBar.setValue(info.currentChunk)


class DeleteTaskDialog(MessageBoxBase):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr("Delete task"))
        self.contentLabel = BodyLabel(
            self.tr("Are you sure to delete this task?"))
        self.deleteFileCheckBox = CheckBox(self.tr("Clear cache"))

        self._initWidgets()

    def _initWidgets(self):
        self.deleteFileCheckBox.setCheckable(True)
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