# coding:utf-8
import os
import sys
from enum import Enum

from PySide6.QtCore import QLocale, QStandardPaths
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, FolderValidator, ConfigSerializer, RangeConfigItem,
                            RangeValidator)

from .setting import CONFIG_FILE, EXE_SUFFIX
from pathlib import Path


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # download
    saveFolder = ConfigItem("Download", "SaveFolder", QStandardPaths.writableLocation(QStandardPaths.DownloadLocation), FolderValidator())
    m3u8dlPath = ConfigItem("Download", "M3U8DLPath", str(Path(f"tools/N_m3u8DL-RE{EXE_SUFFIX}").absolute()))
    ffmpegPath = ConfigItem("Download", "FFmpegPath", str(Path(f"tools/ffmpeg{EXE_SUFFIX}").absolute()))
    autoResetLink = ConfigItem("Download", "AutoResetLink", False, BoolValidator())

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    accentColor = OptionsConfigItem(
        "MainWindow", "AccentColor", "#009faa", OptionsValidator(["#009faa", "Auto"]))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())

    # m3u8dl
    threadCount = RangeConfigItem("M3U8DL", "ThreadCount", os.cpu_count(), RangeValidator(1, 1000))
    liveRealTimeMerge = ConfigItem("M3U8DL", "LiveRealTimeMerge", True, BoolValidator())
    liveKeepSegments = ConfigItem("M3U8DL", "LiveKeepSegments", False, BoolValidator())
    livePipeMux = ConfigItem("M3U8DL", "LivePipeMux", False, BoolValidator())
    liveFixVtt = ConfigItem("M3U8DL", "LiveFixVtt", False, BoolValidator())
    useSystemProxy = ConfigItem("M3U8DL", "UseSystemProxy", True, BoolValidator())
    customProxy = ConfigItem("M3U8DL", "CustomProxy", "")
    httpHeader = ConfigItem("M3U8DL", "HttpHeader", "")
    maxSpeed = RangeConfigItem("M3U8DL", "MaxSpeed", -1, RangeValidator(-1, 1000000000))
    speedUnit = OptionsConfigItem("M3U8DL", "SpeedUnit", "Mbps", OptionsValidator(["Mbps", "Kbps"]))
    httpRequestTimeout = RangeConfigItem("M3U8DL", "HttpRequestTimeout", 100, RangeValidator(5, 100000))
    retryCount = RangeConfigItem("M3U8DL", "RetryCount", 3, RangeValidator(1, 1000))
    subtitleFormat = OptionsConfigItem("M3U8DL", "SubtitleFormat", "SRT", OptionsValidator(["SRT", "VTT"]))
    autoSelect = ConfigItem("M3U8DL", "AutoSelect", False, BoolValidator())
    binaryMerge = ConfigItem("M3U8DL", "BinaryMerge", False, BoolValidator())
    delAfterDone = ConfigItem("M3U8DL", "DeleteAfterDone", True, BoolValidator())
    appendURLParams = ConfigItem("M3U8DL", "AppendURLParams", False, BoolValidator())
    noDateInfo = ConfigItem("M3U8DL", "NoDateInfo", False, BoolValidator())
    concurrentDownload = ConfigItem("M3U8DL", "ConcurrentDownload", False, BoolValidator())
    checkSegmentsCount = ConfigItem("M3U8DL", "CheckSegmentsCount", True, BoolValidator())
    mp4RealTimeDecryption = ConfigItem("M3U8DL", "MP4RealTimeDecryption", True, BoolValidator())
    decryptionEngine = OptionsConfigItem("M3U8DL", "DecryptionEngine", "FFmpeg", OptionsValidator([
                                         "FFmpeg", "MP4Decrypt", "Shaka Packager"]))
    decryptionBinaryPath = ConfigItem("M3U8DL", "DecryptionBinaryPath", str(Path(f"tools/ffmpeg{EXE_SUFFIX}").absolute()))

cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE.absolute()), cfg)