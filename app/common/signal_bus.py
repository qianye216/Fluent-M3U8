# coding: utf-8
from PySide6.QtCore import QObject, Signal
from .database.entity import Task


class SignalBus(QObject):
    """ Signal bus """

    appMessageSig = Signal(str)
    appErrorSig = Signal(str)

    checkUpdateSig = Signal()
    micaEnableChanged = Signal(bool)

    downloadTerminated = Signal(int, bool)  # pid, isClearCache

    switchToTaskInterfaceSig = Signal()

    redownloadTask = Signal(Task)

signalBus = SignalBus()