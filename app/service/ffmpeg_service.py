# coding:utf-8
from pathlib import Path
import subprocess
from typing import Union
from PySide6.QtCore import Qt, Signal, Property, QObject
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

import ffmpeg

from ..common.config import cfg
from ..common.utils import removeFile


class FFmpegService(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def saveVideoCover(self, videoPath: Path | str, savePath: Path | str):
        if Path(savePath).exists():
            removeFile(savePath)

        ffmpeg.input(str(videoPath), ss=0).output(str(savePath), vframes=1).run(self.path)

    @property
    def path(self):
        return cfg.get(cfg.ffmpegPath)



ffmpegService = FFmpegService()