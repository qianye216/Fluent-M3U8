# coding:utf-8
from .dao_base import DaoBase


class TaskDao(DaoBase):
    """ Task DAO """

    table = 'tbl_task'
    fields = ['id', 'fileName', "saveFolder", 'size', 'command', 'status', 'createTime']

    def createTable(self):
        success = self.query.exec(f"""
            CREATE TABLE IF NOT EXISTS {self.table}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fileName TEXT,
                saveFolder TEXT,
                size TEXT,
                command TEXT,
                status INTEGER,
                createTime TEXT
            )
        """)
        return success
