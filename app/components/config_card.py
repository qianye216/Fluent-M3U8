# coding:utf-8
import os
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QRect, QUrl
from PySide6.QtWidgets import QWidget, QHBoxLayout

from qfluentwidgets import (IconWidget, BodyLabel, FluentIcon, InfoBarIcon, ComboBox,
                            PrimaryPushButton, LineEdit, GroupHeaderCardWidget, PushButton,
                            CompactSpinBox)

from ..common.icon import Logo
from ..common.config import cfg


class BasicConfigCard(GroupHeaderCardWidget):
    """ Basic config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Basic settings"))

        self.urlLineEdit = LineEdit()
        self.fileNameLineEdit = LineEdit()
        self.saveFolderButton = PushButton(self.tr("Choose"))
        self.threadCountSpinBox = CompactSpinBox()
        self.retryCountSpinBox = CompactSpinBox()

        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION, self)
        self.hintLabel = BodyLabel(
            self.tr("Click the download button to start downloading") + ' 👉')
        self.downloadButton = PrimaryPushButton(
            self.tr("Download"), self, FluentIcon.PLAY_SOLID)

        self.toolBarLayout = QHBoxLayout()

        self.__initWidgets()

    def __initWidgets(self):
        self.hintIcon.setFixedSize(16, 16)
        self.setBorderRadius(8)

        self.urlLineEdit.setFixedWidth(300)
        self.fileNameLineEdit.setFixedWidth(300)
        self.saveFolderButton.setFixedWidth(120)
        self.threadCountSpinBox.setFixedWidth(120)
        self.retryCountSpinBox.setFixedWidth(120)

        self.urlLineEdit.setClearButtonEnabled(True)
        self.fileNameLineEdit.setClearButtonEnabled(True)

        self.urlLineEdit.setPlaceholderText(self.tr("Please enter the url of m3u8 file"))
        self.fileNameLineEdit.setPlaceholderText(self.tr("Please enter the name of downloaded file"))

        self.threadCountSpinBox.setRange(1, 1000)
        self.threadCountSpinBox.setValue(os.cpu_count())

        self.retryCountSpinBox.setRange(1, 1000)
        self.retryCountSpinBox.setValue(3)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.LINK,
            title=self.tr("Download URL"),
            content=self.tr("The URL of m3u8 file"),
            widget=self.urlLineEdit
        )
        self.addGroup(
            icon=Logo.FILM,
            title=self.tr("File Name"),
            content=self.tr("The name of downloaded file"),
            widget=self.fileNameLineEdit
        )
        self.addGroup(
            icon=Logo.FOLDER,
            title=self.tr("Save Folder"),
            content=cfg.get(cfg.saveFolder),
            widget=self.saveFolderButton
        )
        self.addGroup(
            icon=Logo.KNOT,
            title=self.tr("Download Threads"),
            content=self.tr("Set the number of concurrent download threads"),
            widget=self.threadCountSpinBox
        )
        group = self.addGroup(
            icon=Logo.JOYSTICK,
            title=self.tr("Retry Count"),
            content=self.tr(
                "Set the retry count for each shard download exception"),
            widget=self.retryCountSpinBox
        )
        group.setSeparatorVisible(True)

        # add widgets to bottom toolbar
        self.toolBarLayout.setContentsMargins(24, 15, 24, 20)
        self.toolBarLayout.setSpacing(10)
        self.toolBarLayout.addWidget(
            self.hintIcon, 0, Qt.AlignmentFlag.AlignLeft)
        self.toolBarLayout.addWidget(
            self.hintLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.toolBarLayout.addStretch(1)
        self.toolBarLayout.addWidget(
            self.downloadButton, 0, Qt.AlignmentFlag.AlignRight)
        self.toolBarLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.vBoxLayout.addLayout(self.toolBarLayout)

    def __connectSignalToSlot(self):
        pass
