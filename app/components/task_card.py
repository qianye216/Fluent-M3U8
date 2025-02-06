# coding:utf-8
from dataclasses import dataclass
from PySide6.QtCore import Qt, Signal, Property
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (SimpleCardWidget, IconWidget, ToolButton, FluentIcon,
                            BodyLabel, CaptionLabel, ProgressBar)


@dataclass
class DownloadProgressInfo:
    """ Download progress information """

    speed: str = ""
    remainTime: str = ""
    size: str = ""
    totalSize: str = ""
    progress: float = 0


class DownloadingTaskCard(SimpleCardWidget):
    """ Task card """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()

        self.iconWidget = IconWidget()
        self.fileNameLabel = BodyLabel()
        self.progressBar = ProgressBar()

        self.speedIcon = IconWidget(FluentIcon.SPEED_HIGH)
        self.speedLabel = CaptionLabel()
        self.remainTimeIcon = IconWidget(FluentIcon.STOP_WATCH)
        self.remainTimeLabel = CaptionLabel()
        self.sizeIcon = IconWidget(FluentIcon.PIE_SINGLE)
        self.sizeLabel = CaptionLabel()

        self.openFolderButton = ToolButton(FluentIcon.FOLDER)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

    def _initWidget(self):
        self.speedIcon.setFixedSize(16, 16)
        self.remainTimeIcon.setFixedSize(16, 16)
        self.sizeIcon.setFixedSize(16, 16)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addWidget(self.openFolderButton)
        self.hBoxLayout.addWidget(self.deleteButton)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)
        self.vBoxLayout.addWidget(self.progressBar)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(1)
        self.infoLayout.addWidget(self.speedIcon)
        self.infoLayout.addWidget(self.speedLabel)
        self.infoLayout.addSpacing(3)
        self.infoLayout.addWidget(self.remainTimeIcon)
        self.infoLayout.addWidget(self.remainTimeIcon)
        self.infoLayout.addSpacing(3)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel)

    def _connectSignalToSlot(self):
        pass

    def setInfo(self, info: DownloadProgressInfo):
        """ update progress info """
        self.speedLabel.setText(info.speed)
        self.remainTimeLabel.setText(info.remainTime)
        self.sizeLabel.setText(f"{info.size}/{info.totalSize}")
        self.progressBar.setValue(int(info.progress))