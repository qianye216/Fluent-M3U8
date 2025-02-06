# coding:utf-8
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QRect, QUrl, QPropertyAnimation, QFileInfo
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QAction, QFont, QStandardItem, QTextCursor, QTextOption
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect, QFileDialog, QGridLayout

from qfluentwidgets import ScrollArea

from ..common.utils import openUrl, showInFolder
from ..common.config import cfg
from ..common.icon import Icon

from ..components.info_card import M3U8DLInfoCard
from ..components.config_card import BasicConfigCard, AdvanceConfigCard, ProxyConfigCard



class DownloadInterface(ScrollArea):
    """ Download interface """

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

        self.__initWidget()

    def __initWidget(self):
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

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        pass