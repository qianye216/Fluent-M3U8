# coding:utf-8
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, QFileInfo
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import ScrollArea, InfoBar, InfoBarPosition, PushButton

from ..components.info_card import M3U8DLInfoCard
from ..components.config_card import BasicConfigCard, AdvanceConfigCard, ProxyConfigCard, LiveConfigCard, DecryptionConfigCard

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
        self.liveSettingCard = LiveConfigCard()
        self.decryptionCard = DecryptionConfigCard()

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
            self.liveSettingCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(
            self.decryptionCard, 0, Qt.AlignmentFlag.AlignTop)
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

        basicOptions = self.basicSettingCard.parseOptions()
        if not basicOptions:
            InfoBar.warning(
                self.tr("Task failed"),
                self.tr("No available tasks found, please check the format of txt"),
                duration=-1,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
            return

        success = True

        for basicOption in basicOptions:
            options = [
                *basicOption,
                *self.proxySettingCard.parseOptions(),
                *self.advanceSettingCard.parseOptions(),
                *self.liveSettingCard.parseOptions(),
                *self.decryptionCard.parseOptions(),
            ]
            success = m3u8Service.download(options, self.basicSettingCard.mediaParser) and success

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

    def dragEnterEvent(self, e):
        if not e.mimeData().hasUrls():
            return e.ignore()

        e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        if not e.mimeData().urls():
            return

        fileInfo = QFileInfo(e.mimeData().urls()[0].toLocalFile())
        path = fileInfo.absoluteFilePath()

        if fileInfo.isFile() and path.lower().endswith(".txt"):
            self.setDownloadLink(path)

    def setDownloadLink(self, url: str):
        self.basicSettingCard.urlLineEdit.setText(url)

    def _connectSignalToSlot(self):
        self.basicSettingCard.downloadButton.clicked.connect(self._onDownloadButtonClicked)