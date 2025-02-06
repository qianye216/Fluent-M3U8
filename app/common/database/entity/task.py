# coding:utf-8
from typing import List
from .entity import Entity
from dataclasses import dataclass, field

from PySide6.QtCore import QDateTime


@dataclass
class Task(Entity):

    id: int = None
    fileName: str = None            # 文件名
    saveFolder: str = None          # 保存文件夹
    command: str = None             # 下载命令
    status: int = 0                 # 状态，0 为下载中，1 为下载完成，2 为下载失败
    createTime: QDateTime = field(default_factory=QDateTime.currentDateTime)    # 创建时间


