# coding:utf-8
import os
import re
from typing import List
from PySide6.QtCore import Qt, Signal, QTime

from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileDialog

from qfluentwidgets import (IconWidget, BodyLabel, FluentIcon, InfoBarIcon, ComboBox,
                            PrimaryPushButton, LineEdit, GroupHeaderCardWidget, PushButton,
                            CompactSpinBox, SwitchButton, IndicatorPosition, PlainTextEdit,
                            ToolTipFilter, ConfigItem)

from m3u8.model import StreamInfo

from ..common.icon import Logo, PNG
from ..common.config import cfg
from ..common.concurrent import TaskExecutor
from ..common.utils import adjustFileName

from ..service.m3u8dl_service import M3U8DLCommand, m3u8Service, BatchM3U8FileParser


class M3U8GroupHeaderCardWidget(GroupHeaderCardWidget):

    def addSwitchOption(self, icon, title, content, command: M3U8DLCommand, configItem: ConfigItem):
        button = SwitchButton(self.tr("Off"), self, IndicatorPosition.RIGHT)
        button.setOnText(self.tr("On"))
        button.setOffText(self.tr("Off"))
        button.setProperty("command", command)
        button.setProperty("config", configItem)
        button.setChecked(cfg.get(configItem))
        button.checkedChanged.connect(lambda c: cfg.set(configItem, c))

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

        self.threadCountSpinBox.setRange(*cfg.threadCount.range)
        self.threadCountSpinBox.setValue(cfg.get(cfg.threadCount))

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
        if (m3u8Service.isSupport(url) and fileName) or url.endswith(".txt"):
            self.downloadButton.setEnabled(True)
        else:
            self.downloadButton.setEnabled(False)

    def _onUrlChanged(self, url: str):
        url = url.strip()
        if not m3u8Service.isSupport(url):
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
        self.threadCountSpinBox.valueChanged.connect(lambda v: cfg.set(cfg.threadCount, v))

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
        if m3u8Service.isSupport(url):
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
        self.retryCountSpinBox.setRange(*cfg.retryCount.range)
        self.retryCountSpinBox.setValue(cfg.get(cfg.retryCount))

        self.httpTimeoutSpinBox.setRange(*cfg.httpRequestTimeout.range)
        self.httpTimeoutSpinBox.setValue(cfg.get(cfg.httpRequestTimeout))
        self.httpTimeoutSpinBox.setFixedWidth(120)

        self.httpHeaderEdit.setFixedSize(300, 56)
        self.httpHeaderEdit.setPlainText(cfg.get(cfg.httpHeader))
        self.httpHeaderEdit.setPlaceholderText("User-Agent: iOS\nCookie: mycookie")

        self.speedSpinBox.setRange(*cfg.maxSpeed.range)
        self.speedSpinBox.setValue(cfg.get(cfg.maxSpeed))
        self.speedComboBox.addItems(cfg.speedUnit.options)
        self.speedComboBox.setCurrentText(cfg.get(cfg.speedUnit))

        self.subtitleComboBox.setFixedWidth(120)
        self.subtitleComboBox.addItems(cfg.subtitleFormat.options)
        self.subtitleComboBox.setCurrentText(cfg.get(cfg.subtitleFormat))

        self._initLayout()
        self._connectSignalToSlot()

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
            command=M3U8DLCommand.AUTO_SELECT,
            configItem=cfg.autoSelect
        )
        self.addSwitchOption(
            icon=Logo.CARD_FILE_BOX.icon(),
            title=self.tr("Binary Merge"),
            content=self.tr("Merge ts files directly through binary copy connections"),
            command=M3U8DLCommand.BINARY_MERGE,
            configItem=cfg.binaryMerge
        )
        self.addSwitchOption(
            icon=Logo.WASTEBASKET.icon(),
            title=self.tr("Delete After Done"),
            content=self.tr("Delete temporary files after downloading is complete"),
            command=M3U8DLCommand.DEL_AFTER_DONE,
            configItem=cfg.delAfterDone
        )
        self.addSwitchOption(
            icon=Logo.CONTROL.icon(),
            title=self.tr("Check Segments Count"),
            content=self.tr("Check if downloaded shards matches the expected number"),
            command=M3U8DLCommand.CHECK_SEGMENTS_COUNT,
            configItem=cfg.checkSegmentsCount
        )
        self.addSwitchOption(
            icon=Logo.LINK.icon(),
            title=self.tr("Append URL Params"),
            content=self.tr("Adding the Params of the input URL to the shard"),
            command=M3U8DLCommand.APPEND_URL_PARAMS,
            configItem=cfg.appendURLParams
        )
        self.addSwitchOption(
            icon=Logo.CALENDAR.icon(),
            title=self.tr("Date Info"),
            content=self.tr("Do not write date information when mixing"),
            command=M3U8DLCommand.NO_DATE_INFO,
            configItem=cfg.noDateInfo
        )
        self.addSwitchOption(
            icon=Logo.INBOX.icon(),
            title=self.tr("Concurrent"),
            content=self.tr("Concurrent download of selected audio, video, and subtitles"),
            command=M3U8DLCommand.CONCURRENT_DOWNLOAD,
            configItem=cfg.concurrentDownload
        )

    def parseOptions(self):
        """ Returns the m3u8dl options """
        options = [
            M3U8DLCommand.HTTP_REQUEST_TIMEOUT.command(self.httpTimeoutSpinBox.value()),
            M3U8DLCommand.DOWNLOAD_RETRY_COUNT.command(self.retryCountSpinBox.value()),
            M3U8DLCommand.SUB_FORMAT.command(self.subtitleComboBox.currentText()),
        ]

        if self.httpHeaderEdit.toPlainText():
            headers = self.httpHeaderEdit.toPlainText().split("\n")
            for header in headers:
                options.append(M3U8DLCommand.HEADER.command(header))

        if self.speedSpinBox.value() > 0:
            speed = str(self.speedSpinBox.value()) + self.speedComboBox.currentText()
            options.append(M3U8DLCommand.MAX_SPEED.command(speed))

        for button in self.findChildren(SwitchButton):
            command = button.property("command")
            if command:
                options.append(command.command(button.isChecked()))

        return options

    def _connectSignalToSlot(self):
        self.speedSpinBox.valueChanged.connect(lambda v: cfg.set(cfg.maxSpeed, v))
        self.httpTimeoutSpinBox.valueChanged.connect(lambda v: cfg.set(cfg.httpRequestTimeout, v))
        self.retryCountSpinBox.valueChanged.connect(lambda v: cfg.set(cfg.retryCount, v))
        self.speedComboBox.currentTextChanged.connect(lambda t: cfg.set(cfg.speedUnit, t))
        self.subtitleComboBox.currentTextChanged.connect(lambda t: cfg.set(cfg.subtitleFormat, t))
        self.httpHeaderEdit.textChanged.connect(lambda: cfg.set(cfg.httpHeader, self.httpHeaderEdit.toPlainText()))


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
        self.proxyLineEdit.setDisabled(cfg.get(cfg.useSystemProxy))
        self.proxyLineEdit.setText(cfg.get(cfg.customProxy))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.systemProxyButton = self.addSwitchOption(
            icon=Logo.PLANET.icon(),
            title=self.tr("System Proxy"),
            content=self.tr("Use system default proxy"),
            command=M3U8DLCommand.USE_SYSTEM_PROXY,
            configItem=cfg.useSystemProxy
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

        proxy = self.proxyLineEdit.text().strip()
        if proxy:
            options.append(M3U8DLCommand.CUSTOM_PROXY.command(proxy))
            cfg.set(cfg.customProxy, proxy)

        return options


class TimeSpinBox(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hourSpinBox = CompactSpinBox(self)
        self.minuteSpinBox = CompactSpinBox(self)
        self.secondsSpinBox = CompactSpinBox(self)

        self._initWidgets()

    def _initWidgets(self):
        self.hourSpinBox.setRange(0, 100000)
        self.minuteSpinBox.setRange(0, 59)
        self.secondsSpinBox.setRange(0, 59)

        self._initLayout()

    def _initLayout(self):
        self.hBoxLayout.addWidget(self.hourSpinBox)
        self.hBoxLayout.addWidget(BodyLabel(":"))
        self.hBoxLayout.addWidget(self.minuteSpinBox)
        self.hBoxLayout.addWidget(BodyLabel(":"))
        self.hBoxLayout.addWidget(self.secondsSpinBox)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(5)

    def time(self):
        h = self.hourSpinBox.value()
        m = self.minuteSpinBox.value()
        s = self.secondsSpinBox.value()

        if h < 0 or h + m + s == 0:
            return ""

        return f"{h:02}:{m:02}:{s:02}"



class LiveConfigCard(M3U8GroupHeaderCardWidget):
    """ Live config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Live Settings"))

        self.timeSpinBox = TimeSpinBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)
        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.realtimeMergeButton = self.addSwitchOption(
            icon=Logo.PUZZLE.icon(),
            title=self.tr("Real-time Merge"),
            content=self.tr("Real-time merging during live streaming recording"),
            command=M3U8DLCommand.LIVE_REAL_TIME_MERGE,
            configItem=cfg.liveRealTimeMerge
        )
        self.keepSegmentButton = self.addSwitchOption(
            icon=Logo.BROOM.icon(),
            title=self.tr("Keep Segments"),
            content=self.tr("Keep shards when enabling real-time merge"),
            command=M3U8DLCommand.LIVE_KEEP_SEGMENTS,
            configItem=cfg.liveKeepSegments
        )
        self.pipeMuxButton = self.addSwitchOption(
            icon=Logo.SYRINGE.icon(),
            title=self.tr("Pipe Mux"),
            content=self.tr("Real-time mixing through pipes and ffmpeg to TS files"),
            command=M3U8DLCommand.LIVE_PIPE_MUX,
            configItem=cfg.livePipeMux
        )
        self.fixVttButton = self.addSwitchOption(
            icon=Logo.BANDAGE.icon(),
            title=self.tr("Fix VTT"),
            content=self.tr("Correction of VTT subtitles based on the start time of audio file"),
            command=M3U8DLCommand.LIVE_FIX_VTT_BY_AUDIO,
            configItem=cfg.liveFixVtt
        )
        self.addGroup(
            icon=Logo.TIMER.icon(),
            title=self.tr("Record Limit"),
            content=self.tr("Recording time limit in HH:mm:ss format"),
            widget=self.timeSpinBox
        )

    def _connectSignalToSlot(self):
        pass

    def parseOptions(self):
        """ Returns the m3u8dl options """
        options = []
        for button in self.findChildren(SwitchButton):
            command = button.property("command")
            if command:
                options.append(command.command(button.isChecked()))

        if self.timeSpinBox.time():
            options.append(M3U8DLCommand.LIVE_RECORD_LIMIT.command(self.timeSpinBox.time()))

        return options



class DecryptionConfigCard(M3U8GroupHeaderCardWidget):
    """ Decryption config card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Decryption Settings"))

        self.keyTextFilePath = None

        self.keyEdit = PlainTextEdit()
        self.engineComboBox = ComboBox()
        self.chooseKeyTextFileButton = PushButton(self.tr("Choose"))
        self.chooseEngineBinaryButton = PushButton(self.tr("Choose"))

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.keyEdit.setFixedSize(300, 56)
        self.keyEdit.setPlaceholderText("KID1:KEY1\nKID2:KEY2")

        self.engineComboBox.addItem("FFmpeg", userData="FFMPEG")
        self.engineComboBox.addItem("MP4Decrypt", userData="MP4DECRYPT")
        self.engineComboBox.addItem("Shaka Packager", userData="SHAKA_PACKAGER")

        self.engineComboBox.setMinimumWidth(120)
        self.chooseKeyTextFileButton.setFixedWidth(120)
        self.chooseEngineBinaryButton.setFixedWidth(120)

        self._initLayout()
        self._connectSignalToSlot()

        self.engineComboBox.setCurrentText(cfg.get(cfg.decryptionEngine))

    def _initLayout(self):
        self.mp4RealTimeDecryptionButton = self.addSwitchOption(
            icon=Logo.UNLOCKED.icon(),
            title=self.tr("Real-time Decryption"),
            content=self.tr("Real time decryption of MP4 shards"),
            command=M3U8DLCommand.MP4_REAL_TIME_DECRYPTION,
            configItem=cfg.mp4RealTimeDecryption
        )
        self.engineGroup = self.addGroup(
            icon=Logo.FFMPEG.icon(),
            title=self.tr("Decryption Engine"),
            content=self.tr("Third party program used for decryption"),
            widget=self.engineComboBox
        )
        self.enginePathGroup = self.addGroup(
            icon=Logo.GEAR.icon(),
            title=self.tr("Engine Binary Path"),
            content=cfg.get(cfg.decryptionBinaryPath),
            widget=self.chooseEngineBinaryButton
        )
        self.keyFileGroup = self.addGroup(
            icon=Logo.LEDGER.icon(),
            title=self.tr("Key Text File"),
            content=self.tr("Search for KEY from text file by KID to decrypt"),
            widget=self.chooseKeyTextFileButton
        )
        self.addGroup(
            icon=Logo.KEY.icon(),
            title=self.tr("Key"),
            content=self.tr("Use the key to call engine for decryption"),
            widget=self.keyEdit
        )

    def _onEngineChanged(self):
        icons = [Logo.FFMPEG, Logo.BENTO, PNG.SHAKA_PACKAGER]
        self.engineGroup.setIcon(icons[self.engineComboBox.currentIndex()].icon())
        cfg.set(cfg.decryptionEngine, self.engineComboBox.currentText())

    def _onChooseEngineButtonClicked(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Choose"))

        if not path or cfg.get(cfg.decryptionBinaryPath) == path:
            return

        cfg.set(cfg.decryptionBinaryPath, path)
        self.enginePathGroup.setContent(path)

    def _onChooseKeyTextFileButtonClicked(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Choose"))
        if not path:
            return

        self.keyTextFilePath = path
        self.keyFileGroup.setContent(path)

    def _connectSignalToSlot(self):
        self.engineComboBox.currentIndexChanged.connect(self._onEngineChanged)
        self.chooseEngineBinaryButton.clicked.connect(self._onChooseEngineButtonClicked)
        self.chooseKeyTextFileButton.clicked.connect(self._onChooseKeyTextFileButtonClicked)

    def parseOptions(self):
        """ Returns the m3u8dl options """
        options = [
            M3U8DLCommand.MP4_REAL_TIME_DECRYPTION.command(self.mp4RealTimeDecryptionButton.isChecked()),
            M3U8DLCommand.DECRYPTION_ENGINE.command(self.engineComboBox.currentData()),
            M3U8DLCommand.DECRYPTION_BINARY_PATH.command(cfg.get(cfg.decryptionBinaryPath)),
        ]

        if self.keyTextFilePath:
            options.append(M3U8DLCommand.KEY_TEXT_FILE.command(self.keyTextFilePath))

        if self.keyEdit.toPlainText():
            keys = self.keyEdit.toPlainText().split("\n")
            for key in keys:
                options.append(M3U8DLCommand.KEY.command(key))

        return options