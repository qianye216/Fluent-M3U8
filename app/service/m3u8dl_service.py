# coding:utf-8
import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Dict, List
import shutil

from PySide6.QtCore import Qt, Signal, QProcess, QObject, QDateTime, QEventLoop
import m3u8

from ..common.logger import Logger
from ..common.database.entity import Task
from ..common.config import cfg
from ..common.utils import openUrl
from ..common.signal_bus import signalBus
from ..common.concurrent import TaskExecutor
from ..common.exception_handler import exceptionTracebackHandler
from ..common.database import sqlRequest
from ..common.media_parser import MediaParser
from .ffmpeg_service import ffmpegService


class M3U8DLCommand(Enum):
    """ M3U8DL command options """

    TMP_DIR = "--tmp-dir"
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
    LIVE_REAL_TIME_MERGE = "--live-real-time-merge"
    LIVE_KEEP_SEGMENTS = "--live-keep-segments"
    LIVE_PIPE_MUX = "--live-pipe-mux"
    LIVE_FIX_VTT_BY_AUDIO = "--live-fix-vtt-by-audio"
    LIVE_RECORD_LIMIT= "--live-record-limit"
    LIVE_WAIT_TIME = "--live-wait-time"
    LIVE_TAKE_COUNT = "--live-take-count"
    CHECK_SEGMENTS_COUNT = "--check-segments-count"
    KEY = "--key"
    KEY_TEXT_FILE = "--key-text-file"
    DECRYPTION_ENGINE = "--decryption-engine"
    DECRYPTION_BINARY_PATH = "--decryption-binary-path"
    MP4_REAL_TIME_DECRYPTION = "--mp4-real-time-decryption"
    NO_ASCII_COLOR = "--no-ansi-color"
    DISABLE_UPDATE_CHECK = "--disable-update-check"
    UI_LANGUAGE = "--ui-language"
    AD_KEYWORD = "--ad-keyword"
    MUX_AFTER_DONE = "--mux-after-done"
    MUX_IMPORT = "--mux-import"

    def command(self, value=None):
        if value is None:
            return self.value

        if isinstance(value, list):
            return f"{self.value}={','.join(value)}"

        value = str(value)
        return f'{self.value}="{value}"' if value.find(" ") >= 0 else f'{self.value}={value}'


class M3U8DLEnvVariable:

    RE_KEEP_IMAGE_SEGMENTS = "RE_KEEP_IMAGE_SEGMENTS"


@dataclass
class VODDownloadProgressInfo:
    """ VOD Download progress information """

    currentChunk: int = 0
    totalChunks: int = 0
    speed: str = ""
    remainTime: str = ""
    currentSize: str = ""
    totalSize: str = ""


@dataclass
class LiveDownloadProgressInfo:
    """ VOD Download progress information """

    status: str = ""
    speed: str = ""
    percent: int = 0
    currentTime: str = ""
    totalTime: str = ""


class LiveDownloadStatus(Enum):

    RECORDING = "Recording"
    WAITING = "Waiting"


class BatchM3U8FileParser:
    """ Batch M3U8 File Parser """

    @exceptionTracebackHandler('download', [])
    def parse(self, file: Path | str):
        """ parse txt file

        Parameters
        ----------
        file: str | Path
            txt file path, each line of file is `fileName,url`

        Returns
        -------
        tasks: List[Tuple[str, str]]
            `(fileName, url)` list
        """
        with open(file, encoding='utf-8') as f:
            lines = f.readlines()

        result = []
        for line in lines:
            fileName, url = line.strip().split(",")
            result.append((fileName, url))

        return result


def str2bool(value):
    if isinstance(value, bool):
        return value

    return True if value.lower() == "true" else False


class M3U8DLCommandLineParser(QObject):
    """ M3U8DL Command line parser """

    def __init__(self):
        super().__init__()
        self._parser = argparse.ArgumentParser(
            description="handle N_m3u8DL-RE's command line")
        self._setUpParser()

    def _setUpParser(self):
        self._parser.add_argument('url', type=str, nargs='?', default=None)
        self._parser.add_argument(M3U8DLCommand.SAVE_NAME.value, type=str)
        self._parser.add_argument(M3U8DLCommand.SAVE_DIR.value, type=str)
        self._parser.add_argument(M3U8DLCommand.BINARY_MERGE.value, type=str2bool, default=False)
        self._parser.add_argument(M3U8DLCommand.LIVE_REAL_TIME_MERGE.value, type=str2bool, default=False)

    def parse(self, options: List[str]) -> Task:
        """ process args """
        args, _ = self._parser.parse_known_args(options)
        task = Task(
            url=args.url,
            fileName=args.save_name,
            saveFolder=args.save_dir,
            isBinaryMerge=args.binary_merge,
            isLiveRealTimeMerge=args.live_real_time_merge,
            command=" ".join(options),
        )
        return task


class M3U8DLService(QObject):

    downloadCreated = Signal(Task)
    downloadProcessChanged = Signal((Task, VODDownloadProgressInfo), (Task, LiveDownloadProgressInfo))
    downloadFinished = Signal(Task, bool, str)   # task, isSuccess, message

    coverSaved = Signal(Task)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.logger = Logger("download")
        self.cmdParser = M3U8DLCommandLineParser()
        self.processMap = {}    # type: Dict[str, QProcess]

    @exceptionTracebackHandler("download", False)
    def download(self, options: List[str], parser: MediaParser = None):
        if not self.isAvailable():
            return False

        # create task
        options = self.generateCommand(options)
        task = self.cmdParser.parse(options)

        # determine live recording
        if not parser:
            parser = MediaParser.parse(task.url)

        if parser:
            eventLoop = QEventLoop(self)
            TaskExecutor.runTask(parser.isLive).then(lambda isLive: self._onLiveInfoFetched(isLive, task, eventLoop))
            eventLoop.exec()

        # auto rename
        currentTime = task.createTime.toString("yyyy-MM-dd_hh-mm-ss")
        if task.hasAvailableVideo():
            task.fileName += '_' + currentTime
            options = [M3U8DLCommand.SAVE_NAME.command(task.fileName) if i.startswith(M3U8DLCommand.SAVE_NAME.value) else i for i in options]
            task.command = " ".join([self.downloaderPath, *options])

        # create logger
        taskLogger = Logger("Tasks/" + currentTime, False)
        task.logFile = str(taskLogger.logFile.absolute())

        message = f"Add download task：{self.downloaderPath} {' '.join(options)}"
        self.logger.info(message)
        taskLogger.info(message)

        # create N_m3u8dl-RE process
        process = QProcess()
        self._setupEnv(process)
        process.setWorkingDirectory(str(Path(self.downloaderPath).parent))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        process.readyRead.connect(lambda: self._onDownloadMessage(process, task, taskLogger))
        process.finished.connect(lambda code, status: self._onDownloadFinished(process, task, code, status))
        process.start(self.downloaderPath, options)

        task.pid = process.processId()
        process.setProperty("task", task)
        self.processMap[task.pid] = process
        self.downloadCreated.emit(task)
        return True

    def _setupEnv(self, process: QProcess):
        env = process.systemEnvironment()

        if cfg.get(cfg.keepImageSegments):
            env.append(f"{M3U8DLEnvVariable.RE_KEEP_IMAGE_SEGMENTS}=1")

        process.setEnvironment(env)

    def _onDownloadMessage(self, process: QProcess, task: Task, logger: Logger):
        try:
            message = process.readAllStandardOutput().toStdString()
        except:
            return

        logger.info(message)

        if 'WARN' in message:
            return

        # parse progress message
        if not task.isLive:
            regex = r"(\d+)\/(\d+)\s+(\d+\.\d+)%\s+(\d+\.\d+)(KB|MB|GB)\/(\d+\.\d+)(KB|MB|GB)\s+(\d+\.\d+)(GBps|MBps|KBps|Bps)\s(.+)"
            match = re.search(regex, message)

            if not match:
                return

            info = VODDownloadProgressInfo(
                currentChunk=int(match[1]),
                totalChunks=int(match[2]),
                currentSize=match[4]+match[5],
                totalSize=match[6]+match[7],
                speed=match[8]+match[9],
                remainTime=match[10]
            )
            task.size = info.totalSize
            info.speed = info.speed.replace("KBps", "KB/s").replace("MBps", "MB/s").replace("GBps", "GB/s")
            self.downloadProcessChanged.emit(task, info)
        else:
            regex = r"(\d{2}m\d{2}s)/(\d{2}m\d{2}s)\s(\d+/\d+)\s(Recording|Waiting)\s+(\d+)%\s(-|(\d+\.\d+)(GBps|MBps|KBps|Bps))"
            match = re.search(regex, message)

            if not match:
                return

            info = LiveDownloadProgressInfo(
                currentTime=match[1],
                totalTime=match[2],
                status=match[4],
                percent=int(match[5]),
                speed=match[6],
            )
            info.speed = info.speed.replace("KBps", "KB/s").replace("MBps", "MB/s").replace("GBps", "GB/s")
            self.downloadProcessChanged.emit(task, info)

    def _onDownloadFinished(self, process: QProcess, task: Task, code, status: QProcess.ExitStatus):
        if task.pid not in self.processMap:
            return

        self.processMap.pop(task.pid)

        if status == QProcess.ExitStatus.NormalExit:
            if task.hasAvailableVideo():
                # save cover:
                TaskExecutor.runTask(ffmpegService.saveVideoCover, task.availableVideoPath(), task.coverPath).then(
                    lambda: self.coverSaved.emit(task), lambda e: self.logger.error(e))

                self.downloadFinished.emit(task, True, "")
                task.success()
            else:
                self.downloadFinished.emit(task, False, "")
                task.error()
        else:
            self.downloadFinished.emit(task, False, process.errorString())
            task.error()

        sqlRequest("taskService", "add", task=task)

    def generateCommand(self, options):
        options.extend([
            M3U8DLCommand.NO_ASCII_COLOR.command(),
            M3U8DLCommand.DISABLE_UPDATE_CHECK.command(),
            M3U8DLCommand.SELECT_AUDIO.command("all"),
            M3U8DLCommand.SELECT_SUBTITLE.command("all"),
        ])
        return options

    @exceptionTracebackHandler("download")
    def clearTasks(self):
        for process in self.processMap.values():
            if process.state() != QProcess.ProcessState.NotRunning:
                process.terminate()

        self.processMap.clear()

    def _onLiveInfoFetched(self, isLive: bool, task: Task, eventLoop: QEventLoop):
        task.isLive = isLive
        eventLoop.quit()

    @property
    def downloaderPath(self):
        return cfg.get(cfg.m3u8dlPath)

    def isAvailable(self):
        return Path(self.downloaderPath).exists()

    def terminateTask(self, task: Task):
        process = self.processMap.get(task.pid)
        if not process:
            return

        self.processMap.pop(task.pid)
        process.terminate()

    def stopLiveTask(self, task: Task):
        process = self.processMap.get(task.pid)
        if not process:
            return

        self._onDownloadFinished(process, task, 0, QProcess.ExitStatus.NormalExit)
        process.terminate()

    def showDownloadLog(self):
        """ show download log """
        openUrl(str(self.logger.logFile))

    def isSupport(self, url: str):
        """ Returns whether the format is supported """
        return MediaParser.canParse(url)


m3u8Service = M3U8DLService()