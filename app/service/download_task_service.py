# coding:utf-8
from pathlib import Path
import shutil
from PySide6.QtCore import Qt, Signal, Property, QObject
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from ..common.database import sqlRequest
from ..common.database.entity import Task
from ..common.utils import removeFile
from .m3u8dl_service import m3u8Service


class DownloadTaskService(QObject):
    """ Download task service """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def redownload(self, task: Task):
        """ redownload task """
        options = task.command.split(" ")[1:]
        return m3u8Service.download(options)

    def removeDownloadingTask(self, task: Task, deleteFile=True):
        """ remove downloading task """
        m3u8Service.terminateTask(task)

        if deleteFile:
            self._removeTmpFolder(task)

    def finishLiveRecordingTask(self, task: Task):
        m3u8Service.stopLiveTask(task)
        self._removeTmpFolder(task)

    def removedSuccessTask(self, task: Task, deleteFile=True):
        """ remove success task """
        sqlRequest("taskService", "removeById", id=task.id)

        if deleteFile:
            removeFile(task.videoPath)

    def removeFailedTask(self, task: Task, deleteFile=True):
        """ remove failed task """
        sqlRequest("taskService", "removeById", id=task.id)

        if deleteFile:
            self._removeTmpFolder(task)

    def _removeTmpFolder(self, task: Task):
        folder = task.videoPath.parent / task.fileName
        shutil.rmtree(folder, ignore_errors=True)


downloadTaskService = DownloadTaskService()