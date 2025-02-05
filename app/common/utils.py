# coding: utf-8
from pathlib import Path
import sys
from typing import Union
from json import loads

from PySide6.QtCore import QFile, QUrl, QFileInfo, QDir, QProcess, QStandardPaths
from PySide6.QtGui import QDesktopServices


def readFile(filePath: str):
    """ load json data from file """
    file = QFile(filePath)
    file.open(QFile.OpenModeFlag.ReadOnly)
    data = str(file.readAll(), encoding='utf-8')
    file.close()
    return data


def loadJsonData(filePath: str):
    """ load json data from file """
    return loads(readFile(filePath))


def openUrl(url: str):
    QDesktopServices.openUrl(QUrl(url))



def showInFolder(path: Union[str, Path]):
    """ show file in file explorer """
    if isinstance(path, Path):
        path = str(path.absolute())

    if not path or path.lower() == 'http':
        return

    if path.startswith('http'):
        QDesktopServices.openUrl(QUrl(path))
        return

    info = QFileInfo(path)   # type:QFileInfo
    if sys.platform == "win32":
        args = [QDir.toNativeSeparators(path)]
        if not info.isDir():
            args.insert(0, '/select,')

        QProcess.startDetached('explorer', args)
    elif sys.platform == "darwin":
        args = [
            "-e", 'tell application "Finder"', "-e", "activate",
            "-e", f'select POSIX file "{path}"', "-e", "end tell",
            "-e", "return"
        ]
        QProcess.execute("/usr/bin/osascript", args)
    else:
        url = QUrl.fromLocalFile(path if info.isDir() else info.path())
        QDesktopServices.openUrl(url)


def runProcess(executable: Union[str, Path], args=None, timeout=5000, cwd=None) -> str:
    process = QProcess()

    if cwd:
        process.setWorkingDirectory(str(cwd))

    process.start(str(executable).replace("\\", "/"), args or [])
    process.waitForFinished(timeout)
    return process.readAllStandardOutput().toStdString()


def runDetachedProcess(executable: Union[str, Path], args=None, cwd=None):
    process = QProcess()

    if cwd:
        process.setWorkingDirectory(str(cwd))

    process.startDetached(str(executable).replace("\\", "/"), args or [])