# coding:utf-8
from .dao_base import DaoBase


class TaskDao(DaoBase):
    """ Task DAO """

    table = 'tbl_task'
    fields = ['id', 'fileName', "saveFolder", 'size', 'command', 'status', 'logFile', 'createTime']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                id CHAR(32) PRIMARY KEY,
                fileName TEXT,
                saveFolder TEXT,
                size TEXT,
                command TEXT,
                status INTEGER,
                logFile TEXT,
                createTime TEXT
            )
        """)
        return success
