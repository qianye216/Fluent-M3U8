from .db_initializer import DBInitializer
from .service import *
from collections import deque

from ..signal_bus import signalBus, SqlRequest, SqlResponse
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtSql import QSqlDatabase


def sqlRequest(service: str, method: str, slot=None, params: dict = None):
    """ query sql from database """
    request = SqlRequest(service, method, slot, params)
    signalBus.fetchDataSig.emit(request)



class Database(QObject):
    """ Database """

    def __init__(self, db: QSqlDatabase = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            audio directories

        db: QDataBase
            database to be used

        watch: bool
            whether to monitor audio directories

        parent:
            parent instance
        """
        super().__init__(parent=parent)
        self.taskService = TaskService(db)

    def setDatabase(self, db: QSqlDatabase):
        """ set the database to be used """
        self.taskService.userDao.setDatabase(db)



class DatabaseThread(QThread):
    """ Database thread """

    def __init__(self, db: QSqlDatabase = None, parent=None):
        """
        Parameters
        ----------
        directories: List[str]
            audio directories

        db: QDataBase
            database to be used

        watch: bool
            whether to monitor audio directories

        parent:
            parent instance
        """
        super().__init__(parent=parent)
        self.database = Database(db, self)
        self.tasks = deque()

        signalBus.fetchDataSig.connect(self.onFetchData)

    def run(self):
        while self.tasks:
            task, request = self.tasks.popleft()
            result = task(**request.params)
            signalBus.dataFetched.emit(SqlResponse(result, request.slot))

    def onFetchData(self, request: SqlRequest):
        service = getattr(self.database, request.service)
        task = getattr(service, request.method)
        self.tasks.append((task, request))

        if not self.isRunning():
            self.start()