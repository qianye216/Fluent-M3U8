# coding:utf-8
import os
from typing import List
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QRect, QUrl
from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileDialog

from qfluentwidgets import (IconWidget, BodyLabel, FluentIcon, InfoBarIcon, ComboBox,
                            PrimaryPushButton, LineEdit, GroupHeaderCardWidget, PushButton,
                            CompactSpinBox, SwitchButton, IndicatorPosition, PlainTextEdit,
                            ToolTipFilter)

from m3u8.model import StreamInfo

from ..common.icon import Logo
from ..common.config import cfg
from ..common.concurrent import TaskExecutor
from ..common.utils import adjustFileName

from ..service.m3u8dl_service import M3U8DLCommand, m3u8Service, BatchM3U8FileParser


class M3U8GroupHeaderCardWidget(GroupHeaderCardWidget):

    def addSwitchOption(self, icon, title, content, config: M3U8DLCommand, checked=False):
        button = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        button.setOnText(self.tr("On"))
        button.setOffText(self.tr("Off"))
        button.setProperty("config", config)
        button.setChecked(checked)

        self.addGroup(icon, title, content, button)
        return button


class BasicConfigCard(GroupHeaderCardWidget):
    """ Basic config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Basic Settings"))

        self.urlLineEdit = LineEdit()
        self.fileNameLineEdit = LineEdit()
        self.saveFolderButton = PushButton(self.tr("Choose"))
        self.threadCountSpinBox = CompactSpinBox()
        self.streamInfoComboBox = ComboBox()

        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION, self)
        self.hintLabel = BodyLabel(
            self.tr("Click the download button to start downloading") + ' 👉')
        self.downloadButton = PrimaryPushButton(
            self.tr("Download"), self, FluentIcon.PLAY_SOLID)

        self.toolBarLayout = QHBoxLayout()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.streamInfoComboBox.setMinimumWidth(120)
        self.streamInfoComboBox.addItem(self.tr("Default"))

        self.downloadButton.setEnabled(False)
        self.hintIcon.setFixedSize(16, 16)

        self.urlLineEdit.setFixedWidth(300)
        self.fileNameLineEdit.setFixedWidth(300)
        self.saveFolderButton.setFixedWidth(120)
        self.threadCountSpinBox.setFixedWidth(120)

        self.urlLineEdit.setClearButtonEnabled(True)
        self.fileNameLineEdit.setClearButtonEnabled(True)

        self.fileNameLineEdit.setPlaceholderText(self.tr("Please enter the name of downloaded file"))
        self.urlLineEdit.setPlaceholderText(self.tr("Please enter the path of m3u8 or txt"))
        self.urlLineEdit.setToolTip(self.tr("The format of each line in the txt file is FileName,URL"))
        self.urlLineEdit.setToolTipDuration(3000)
        self.urlLineEdit.installEventFilter(ToolTipFilter(self.urlLineEdit))

        self.threadCountSpinBox.setRange(1, 1000)
        self.threadCountSpinBox.setValue(os.cpu_count())

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.GLOBE.icon(),
            title=self.tr("Download URL"),
            content=self.tr("The path of m3u8 or txt file, support drag and drop txt file"),
            widget=self.urlLineEdit
        )
        self.addGroup(
            icon=Logo.FILM.icon(),
            title=self.tr("File Name"),
            content=self.tr("The name of downloaded file"),
            widget=self.fileNameLineEdit
        )
        self.addGroup(
            icon=Logo.PROJECTOR.icon(),
            title=self.tr("Stream Info"),
            content=self.tr("Select the stream to be downloaded"),
            widget=self.streamInfoComboBox
        )
        self.saveFolderGroup = self.addGroup(
            icon=Logo.FOLDER.icon(),
            title=self.tr("Save Folder"),
            content=cfg.get(cfg.saveFolder),
            widget=self.saveFolderButton
        )
        group = self.addGroup(
            icon=Logo.KNOT.icon(),
            title=self.tr("Download Threads"),
            content=self.tr("Set the number of concurrent download threads"),
            widget=self.threadCountSpinBox
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

    def _onTextChanged(self):
        url = self.urlLineEdit.text().strip()
        fileName = self.fileNameLineEdit.text()
        if (url.endswith('m3u8') and fileName) or url.endswith(".txt"):
            self.downloadButton.setEnabled(True)
        else:
            self.downloadButton.setEnabled(False)

    def _onUrlChanged(self, url: str):
        url = url.strip()
        if not url.endswith(".m3u8"):
            return self._resetStreamInfo()

        TaskExecutor.runTask(m3u8Service.getStreamInfos, url).then(
            self._onStreamInfosFetched)

    def _onStreamInfosFetched(self, streamInfos: List[StreamInfo]):
        if not streamInfos:
            return self._resetStreamInfo()

        self.streamInfoComboBox.clear()

        for info in streamInfos:
            texts = []

            if info.resolution:
                w, h = info.resolution
                texts.append(self.tr("Resolution: ") + f"{w} × {h}")

            if info.codecs:
                texts.append(self.tr("Codecs: ") + info.codecs)

            if info.frame_rate is not None:
                texts.append(self.tr("Fps: ") + f"{info.frame_rate:.1f}")

            self.streamInfoComboBox.addItem("; ".join(texts), userData=info)

    def _chooseSaveFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), self.saveFolderGroup.content())

        if folder:
            self.saveFolderGroup.setContent(folder)

    def _resetStreamInfo(self):
        self.streamInfoComboBox.clear()
        self.streamInfoComboBox.addItem(self.tr("Default"))

    def _connectSignalToSlot(self):
        self.urlLineEdit.textChanged.connect(self._onUrlChanged)
        self.urlLineEdit.textChanged.connect(self._onTextChanged)
        self.fileNameLineEdit.textChanged.connect(self._onTextChanged)
        self.saveFolderButton.clicked.connect(self._chooseSaveFolder)

    def parseOptions(self) -> List[List[str]]:
        """ Returns the m3u8dl options """
        result = []

        options = [
            M3U8DLCommand.SAVE_DIR.command(self.saveFolderGroup.content()),
            M3U8DLCommand.TMP_DIR.command(self.saveFolderGroup.content()),
            M3U8DLCommand.THREAD_COUNT.command(self.threadCountSpinBox.value()),
        ]

        if self.streamInfoComboBox.count() > 1:
            info = self.streamInfoComboBox.currentData()    # type: StreamInfo
            cmds = []

            if info.resolution:
                cmds.append(f"res={info.resolution[0]}*")

            if info.frame_rate:
                cmds.append(f"frame={int(info.frame_rate)}*")

            options.extend([
                M3U8DLCommand.SELECT_VIDEO.command(),
                ":".join(cmds)
            ])
        else:
            options.append(M3U8DLCommand.SELECT_VIDEO.command('best'))

        url = self.urlLineEdit.text().strip()
        if url.endswith(".m3u8"):
            fileName = adjustFileName(self.fileNameLineEdit.text())
            result = [
                [url, M3U8DLCommand.SAVE_NAME.command(fileName), *options]
            ]
        else:
            tasks = BatchM3U8FileParser().parse(url)
            for fileName, m3u8Url in tasks:
                fileName = adjustFileName(fileName)
                result.append([
                    m3u8Url, M3U8DLCommand.SAVE_NAME.command(fileName), *options
                ])

        return result


class AdvanceConfigCard(M3U8GroupHeaderCardWidget):
    """ Advance config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Advance Settings"))

        self.httpTimeoutSpinBox = CompactSpinBox()
        self.httpHeaderEdit = PlainTextEdit()
        self.speedSpinBox = CompactSpinBox()
        self.speedComboBox = ComboBox()
        self.retryCountSpinBox = CompactSpinBox()
        self.subtitleComboBox = ComboBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.retryCountSpinBox.setFixedWidth(120)
        self.retryCountSpinBox.setRange(1, 1000)
        self.retryCountSpinBox.setValue(3)

        self.httpTimeoutSpinBox.setRange(5, 100000)
        self.httpTimeoutSpinBox.setValue(100)
        self.httpTimeoutSpinBox.setFixedWidth(120)

        self.httpHeaderEdit.setFixedSize(300, 56)
        self.httpHeaderEdit.setPlaceholderText("User-Agent: iOS\nCookie: mycookie")

        self.speedSpinBox.setRange(-1, 1000000000)
        self.speedSpinBox.setValue(-1)
        self.speedComboBox.addItems(["Mbps", "Kbps"])

        self.subtitleComboBox.setFixedWidth(120)
        self.subtitleComboBox.addItems(["SRT", "VTT"])

        self._initLayout()

    def _initLayout(self):
        self.addGroup(
            icon=Logo.COOKIE.icon(),
            title=self.tr("Header"),
            content=self.tr("Set custom headers for HTTP requests"),
            widget=self.httpHeaderEdit
        )

        speedGroup = self.addGroup(
            icon=Logo.ROCKET.icon(),
            title=self.tr("Max Speed"),
            content=self.tr("Set maximum download speed, -1 indicates no speed limit"),
            widget=self.speedSpinBox
        )
        speedGroup.addWidget(self.speedComboBox)

        self.addGroup(
            icon=Logo.HOURGLASS.icon(),
            title=self.tr("Request Timeout"),
            content=self.tr("Set timeout for HTTP requests (in seconds)"),
            widget=self.httpTimeoutSpinBox
        )
        self.addGroup(
            icon=Logo.JOYSTICK.icon(),
            title=self.tr("Retry Count"),
            content=self.tr(
                "Set the retry count for each shard download exception"),
            widget=self.retryCountSpinBox
        )

        self.addGroup(
            icon=Logo.SCROLL.icon(),
            title=self.tr("Subtitle Format"),
            content=self.tr("Set the output type of subtitle"),
            widget=self.subtitleComboBox
        )

        self.addSwitchOption(
            icon=Logo.ALEMBIC.icon(),
            title=self.tr("Auto Select"),
            content=self.tr("Automatically select the best track of all types"),
            config=M3U8DLCommand.AUTO_SELECT,
        )
        self.addSwitchOption(
            icon=Logo.CARD_FILE_BOX.icon(),
            title=self.tr("Binary Merge"),
            content=self.tr("Merge ts files directly through binary copy connections"),
            config=M3U8DLCommand.BINARY_MERGE
        )
        self.addSwitchOption(
            icon=Logo.WASTEBASKET.icon(),
            title=self.tr("Delete After Done"),
            content=self.tr("Delete temporary files after downloading is complete"),
            config=M3U8DLCommand.DEL_AFTER_DONE,
            checked=True
        )
        self.addSwitchOption(
            icon=Logo.LINK.icon(),
            title=self.tr("Append URL Params"),
            content=self.tr("Adding the Params of the input URL to the shard"),
            config=M3U8DLCommand.APPEND_URL_PARAMS,
        )
        self.addSwitchOption(
            icon=Logo.CALENDAR.icon(),
            title=self.tr("Date Info"),
            content=self.tr("Do not write date information when mixing"),
            config=M3U8DLCommand.NO_DATE_INFO,
        )
        self.addSwitchOption(
            icon=Logo.INBOX.icon(),
            title=self.tr("Concurrent"),
            content=self.tr("Concurrent download of selected audio, video, and subtitles"),
            config=M3U8DLCommand.CONCURRENT_DOWNLOAD,
        )

    def parseOptions(self):
        """ Returns the m3u8dl options """
        options = [
            M3U8DLCommand.HTTP_REQUEST_TIMEOUT.command(self.httpTimeoutSpinBox.value()),
            M3U8DLCommand.DOWNLOAD_RETRY_COUNT.command(self.retryCountSpinBox.value()),
            M3U8DLCommand.SUB_FORMAT.command(self.subtitleComboBox.currentText()),
        ]

        if self.httpHeaderEdit.toPlainText():
            options.append(M3U8DLCommand.HEADER.command(self.httpHeaderEdit.toPlainText()))

        if self.speedSpinBox.value() > 0:
            speed = str(self.speedSpinBox.value()) + self.speedComboBox.currentText()
            options.append(M3U8DLCommand.MAX_SPEED.command(speed))

        for button in self.findChildren(SwitchButton):
            config = button.property("config")
            if config:
                options.append(config.command(button.isChecked()))

        return options


class ProxyConfigCard(M3U8GroupHeaderCardWidget):
    """ Proxy config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Proxy Settings"))

        self.proxyLineEdit = LineEdit()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.proxyLineEdit.setFixedWidth(300)
        self.proxyLineEdit.setPlaceholderText("http://127.0.0.1:8080")
        self.proxyLineEdit.setEnabled(False)

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.systemProxyButton = self.addSwitchOption(
            icon=Logo.PLANET.icon(),
            title=self.tr("System Proxy"),
            content=self.tr("Use system default proxy"),
            config=M3U8DLCommand.USE_SYSTEM_PROXY,
            checked=True
        )
        self.addGroup(
            icon=Logo.AIRPLANE.icon(),
            title=self.tr("Custom Proxy"),
            content=self.tr("Set the http request proxy to be used"),
            widget=self.proxyLineEdit
        )

    def _connectSignalToSlot(self):
        self.systemProxyButton.checkedChanged.connect(self.proxyLineEdit.setDisabled)

    def parseOptions(self):
        """ Returns the m3u8dl options """
        if self.systemProxyButton.isChecked():
            return []

        options = [M3U8DLCommand.USE_SYSTEM_PROXY.command(False)]

        if self.proxyLineEdit.text():
            options.append(M3U8DLCommand.CUSTOM_PROXY.command(self.proxyLineEdit.text().strip()))

        return options
