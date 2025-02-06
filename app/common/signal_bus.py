# coding: utf-8
from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    """ Signal bus """

    checkUpdateSig = Signal()
    micaEnableChanged = Signal(bool)

    downloadProcessChanged = Signal(int, str)   # pid, message
    downloadFinished = Signal(int, bool, str)   # pid, isSuccess, message

signalBus = SignalBus()