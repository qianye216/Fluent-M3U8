# coding:utf-8
from pathlib import Path
from typing import List
from .entity import Entity
from dataclasses import dataclass, field

from PySide6.QtCore import QDateTime, QFileInfo

from ...setting import COVER_FOLDER


@dataclass
class Task(Entity):

    id: int = None
    pid: int = None                 # 进程 id
    fileName: str = None            # 文件名
    saveFolder: str = None          # 保存文件夹
    size: str = None                # 文件大小
    command: str = None             # 下载命令
    status: int = 0                 # 状态，0 为下载中，1 为下载完成，2 为下载失败
    createTime: QDateTime = field(default_factory=QDateTime.currentDateTime)    # 创建时间

    def error(self):
        self.status = 2

    def success(self):
        self.status = 1

    @property
    def videoPath(self):
        return Path(self.saveFolder) / (self.fileName + ".mp4")

    @property
    def coverPath(self):
        return COVER_FOLDER / (self.fileName + ".jpg")
