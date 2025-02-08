# coding:utf-8
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QRect, QUrl, QPropertyAnimation, QFileInfo
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QAction, QFont, QStandardItem, QTextCursor, QTextOption
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QFileDialog, QGridLayout

from qfluentwidgets import ScrollArea, InfoBar, InfoBarPosition, PushButton

from ..components.info_card import M3U8DLInfoCard
from ..components.config_card import BasicConfigCard, AdvanceConfigCard, ProxyConfigCard

from ..service.m3u8dl_service import m3u8Service
from ..common.signal_bus import signalBus


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.loadProgressInfoBar = None
        self.installProgressInfoBar = None

        self.m3u8dlInfoCard = M3U8DLInfoCard()
        self.basicSettingCard = BasicConfigCard()
        self.advanceSettingCard = AdvanceConfigCard()
        self.proxySettingCard = ProxyConfigCard()

        self.vBoxLayout = QVBoxLayout(self.view)

        self._initWidget()

    def _initWidget(self):
        self.setWidget(self.view)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 10)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.m3u8dlInfoCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.basicSettingCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.proxySettingCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.advanceSettingCard, 0, Qt.AlignmentFlag.AlignTop)

        self.resize(780, 800)
        self.setObjectName("packageInterface")
        self.enableTransparentBackground()

        self._connectSignalToSlot()

    def _onDownloadButtonClicked(self):
        if not m3u8Service.isAvailable():
            InfoBar.error(
                self.tr("Task failed"),
                self.tr("Please choose N_m3u8DL-RE binary file in setting interface"),
                duration=-1,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
            return

        options = [
            *self.basicSettingCard.parseOptions(),
            *self.proxySettingCard.parseOptions(),
            *self.advanceSettingCard.parseOptions(),
        ]
        success = m3u8Service.download(options)
        button = PushButton(self.tr('Check'))

        if success:
            w = InfoBar.success(
                self.tr("Task created"),
                self.tr("Please check the download task"),
                duration=5000,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
            button.clicked.connect(signalBus.switchToTaskInterfaceSig)
        else:
            w = InfoBar.error(
                self.tr("Task failed"),
                self.tr("Please check the error log"),
                duration=-1,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
            button.clicked.connect(m3u8Service.showDownloadLog)

        w.widgetLayout.insertSpacing(0, 10)
        w.addWidget(button)

    def _connectSignalToSlot(self):
        self.basicSettingCard.downloadButton.clicked.connect(self._onDownloadButtonClicked)