# coding:utf-8
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal, Property, QFileInfo
from PySide6.QtGui import QPixmap, QPainter, QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileIconProvider

from qfluentwidgets import (SimpleCardWidget, IconWidget, ToolButton, FluentIcon,
                            BodyLabel, CaptionLabel, ProgressBar, ImageLabel, setFont)

from ..common.database.entity import Task
from ..service.m3u8dl_service import DownloadProgressInfo


class DownloadingTaskCard(SimpleCardWidget):
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

        setFont(self.fileNameLabel, 16, QFont.Weight.Bold)

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
        self.infoLayout.addWidget(self.speedLabel)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.remainTimeIcon)
        self.infoLayout.addWidget(self.remainTimeLabel)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel)
        self.infoLayout.addStretch(1)

    def _connectSignalToSlot(self):
        pass

    def setInfo(self, info: DownloadProgressInfo):
        """ update progress info """
        self.speedLabel.setText(info.speed)
        self.remainTimeLabel.setText(info.remainTime)
        self.sizeLabel.setText(f"{info.currentSize}/{info.totalSize}")

        self.progressBar.setRange(0, info.totalChunks)
        self.progressBar.setValue(info.currentChunk)