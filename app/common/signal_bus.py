# coding: utf-8
from PySide6.QtCore import QObject, Signal


class SqlRequest:
    """ Sql request """

    def __init__(self, service: str, method: str, slot=None, params: dict = None):
        self.service = service
        self.method = method
        self.slot = slot
        self.params = params or {}


class SqlResponse:
    """ Sql response """

    def __init__(self, data, slot):
        self.slot = slot
        self.data = data


class SignalBus(QObject):
    """ Signal bus """

    checkUpdateSig = Signal()
    micaEnableChanged = Signal(bool)

    downloadTerminated = Signal(int, bool)  # pid, isClearCache

    switchToTaskInterfaceSig = Signal()

    fetchDataSig = Signal(SqlRequest)
    dataFetched = Signal(SqlResponse)

signalBus = SignalBus()