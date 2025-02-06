# coding:utf-8
from enum import Enum
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, Signal, QProcess, QObject
import m3u8

from ..common.logger import Logger
from ..common.config import cfg
from ..common.signal_bus import signalBus
from ..common.exception_handler import exceptionTracebackHandler


class M3U8DLCommand(Enum):
    """ M3U8DL command options """

    SAVE_DIR = "--save-dir"
    SAVE_NAME = "--save-name"
    THREAD_COUNT = "--thread-count"
    DOWNLOAD_RETRY_COUNT = "--download-retry-count"
    HTTP_REQUEST_TIMEOUT = "--http-request-timeout"
    HEADER = "--header"
    BINARY_MERGE = "--binary-merge"
    DEL_AFTER_DONE = "--del-after-done"
    APPEND_URL_PARAMS = "--append-url-params"
    MAX_SPEED = "--max-speed"
    SUB_FORMAT = "--sub-format"
    SELECT_VIDEO = "--select-video"
    SELECT_AUDIO = "--select-audio"
    SELECT_SUBTITLE = "--select-subtitle"
    AUTO_SELECT = "--auto-select"
    NO_DATE_INFO = "--no-date-info"
    CONCURRENT_DOWNLOAD = "--concurrent-download"
    USE_SYSTEM_PROXY = "--use-system-proxy"
    CUSTOM_PROXY = "--custom-proxy"

    def command(self, value=None):
        if value is None:
            return self.value

        if isinstance(value, list):
            return f"{self.value}={','.join(value)}"

        value = str(value)
        return f'{self.value}="{value}"' if value.find(" ") >= 0 else f'{self.value}={value}'


class M3U8DLService(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.logger = Logger("download")

    def download(self, options: List[str]):
        options = self.generateCommand(options)

        self.logger.info(f"添加下载任务：{self.downloaderPath} {' '.join(options)}")

        process = QProcess()
        process.setWorkingDirectory(str(Path(self.downloaderPath).parent))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        process.readyRead.connect(lambda: signalBus.emit(
            process.processId(), process.readAllStandardOutput().toStdString()))
        process.finished.connect(lambda code, status: self._onCompileFinished(process, code, status))

        # compileTerminated.connect(process.terminate)

        # process.start(self.downloaderPath, options)
        return True

    def _onDownloadFinished(self, process: QProcess, code, status: QProcess.ExitStatus):
        if status == QProcess.ExitStatus.NormalExit:
            signalBus.downloadFinished.emit(process.processId(), True, "")
        else:
            signalBus.downloadFinished.emit(process.processId(), False, process.errorString())

    def generateCommand(self, options):
        options.extend([
            M3U8DLCommand.SELECT_AUDIO.command(),
            'for=best',
            M3U8DLCommand.SELECT_SUBTITLE.command(),
            'for=all'
        ])
        return options

    @exceptionTracebackHandler("download", [])
    def getStreamInfos(self, url: str, timeout=10):
        """ Returns the available streams information """
        response = m3u8.load(url, timeout=timeout)

        if not response.playlists:
            return []

        streamInfos = []
        for playlist in response.playlists:
            streamInfos.append(playlist.stream_info)

        return streamInfos

    @property
    def downloaderPath(self):
        return cfg.get(cfg.m3u8dlPath)


m3u8Service = M3U8DLService()