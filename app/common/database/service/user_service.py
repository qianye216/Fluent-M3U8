# coding:utf-8
from typing import List

from PySide6.QtSql import QSqlDatabase

from ..dao import TaskDao
from ..entity import Task

from .service_base import ServiceBase


class TaskService(ServiceBase):
    """ Task service """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.userDao = TaskDao(db)

    def createTable(self) -> bool:
        return self.userDao.createTable()

    def findBy(self, **condition) -> Task:
        return self.userDao.selectBy(**condition)

    def listBy(self, **condition) -> List[Task]:
        return self.userDao.listBy(**condition)

    def listAll(self) -> List[Task]:
        return self.userDao.listAll()

    def listByIds(self, ids: List[str]) -> List[Task]:
        return self.userDao.listByIds(ids)

    def modify(self, id: str, field: str, value) -> bool:
        return self.userDao.update(id, field, value)

    def modifyById(self, user: Task) -> bool:
        return self.userDao.updateById(user)

    def modifyByIds(self, users: List[Task]) -> bool:
        return self.userDao.updateByIds(users)

    def add(self, user: Task) -> bool:
        return self.userDao.insert(user)

    def addBatch(self, users: List[Task]) -> bool:
        return self.userDao.insertBatch(users)

    def removeById(self, id: str) -> bool:
        return self.userDao.deleteById(id)

    def removeByIds(self, ids: List[str]) -> bool:
        return self.userDao.deleteByIds(ids)

    def clearTable(self) -> bool:
        return self.userDao.clearTable()

    def setDatabase(self, db: QSqlDatabase):
        self.userDao.setDatabase(db)

    def listLike(self, **condition) -> List[Task]:
        return self.userDao.listLike(**condition)

    def count(self) -> int:
        return self.userDao.count()
