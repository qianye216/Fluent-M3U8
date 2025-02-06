# coding:utf-8
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal, QSize, QUrl
from PySide6.QtGui import QPixmap, QIcon, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (BodyLabel, TransparentToolButton, FluentIcon, ElevatedCardWidget,
                            ImageLabel, SimpleCardWidget, HyperlinkLabel, VerticalSeparator,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont)

from .statistic_widget import StatisticsWidget


class M3U8DLInfoCard(SimpleCardWidget):
    """ M3U8DL information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)
        self.iconLabel = ImageLabel(QIcon(":/app/images/ico/M3U8DL.ico").pixmap(120, 120), self)

        self.nameLabel = TitleLabel(self.tr('M3U8 Downloader'), self)
        self.updateButton = PrimaryPushButton(self.tr("Update"), self)
        self.companyLabel = HyperlinkLabel(
            QUrl('https://github.com/nilaoda/N_m3u8DL-RE'), 'Nilaoda', self)

        self.versionWidget = StatisticsWidget(
            self.tr('Version'), 'v0.3.0', self)
        self.fileSizeWidget = StatisticsWidget(self.tr('File Size'), '19MB', self)
        self.updateTimeWidget = StatisticsWidget(self.tr('Update Time'), '2024-12-01', self)

        self.descriptionLabel = BodyLabel(
            self.tr('Cross-Platform, modern and powerful stream downloader for MPD/M3U8/ISM. Supports regular AES-128-CBC decryption, multi threading and custom request headers.'), self)

        self.tagButton = PillPushButton(self.tr('M3U8'), self)
        self.shareButton = TransparentToolButton(FluentIcon.SHARE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.__initWidgets()

    def __initWidgets(self):
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.updateButton.setFixedWidth(160)

        self.descriptionLabel.setWordWrap(True)
        # self.shareButton.clicked.connect(lambda: openUrl(DEPLOY_URL))

        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.shareButton.setFixedSize(32, 32)
        self.shareButton.setIconSize(QSize(14, 14))

        self.nameLabel.setObjectName("nameLabel")
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.initLayout()

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addWidget(self.updateButton, 0, Qt.AlignRight)

        # company label
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addWidget(self.companyLabel)

        # statistics widgets
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        self.statisticsLayout.addWidget(self.versionWidget)
        self.statisticsLayout.addWidget(VerticalSeparator())
        self.statisticsLayout.addWidget(self.fileSizeWidget)
        self.statisticsLayout.addWidget(VerticalSeparator())
        self.statisticsLayout.addWidget(self.updateTimeWidget)
        self.statisticsLayout.setAlignment(Qt.AlignLeft)

        # description label
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.tagButton, 0, Qt.AlignLeft)
        self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignRight)

    def setVersion(self, version: str):
        text = version or '0.3.0'
        self.versionWidget.valueLabel.setText(text)
        self.versionWidget.valueLabel.setTextColor(
            QColor(0, 0, 0), QColor(255, 255, 255))
