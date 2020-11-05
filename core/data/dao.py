from typing import List, Optional, Tuple

import mysql.connector as cn

from core.utils.db import enquote_all
from core.utils.singleton import singleton


@singleton
class Dao:

    def __init__(self, user: str = None, database: str = None, host: str = None, password: str = None):
        self._user = user if user is not None else "DeviceControl"
        self._database = database if database is not None else "device_control"
        self._host = host if host is not None else "127.0.0.1"
        self._password = password if password is not None else "&Bioarineo1"

        self.tables = {'events': ['dev_id', 'event_type', 'time', 'args', 'command', 'response'],
                       'values': ['time', 'value', 'dev_id', 'var_id', 'channel', 'note'],
                       'experiments': ['dev_id', 'start', 'description'],
                       'devices': ['id', 'class', 'type', 'address'],
                       'variables': ['code', 'type']}

    def _connect(self):
        """
        Establish connection to the database.
        :return: mysql.connector.connect object
        """
        return cn.connect(host=self._host,
                          user=self._user,
                          password=self._password,
                          db=self._database)

    def _execute_query(self, query):
        con = self._connect()
        cursor = con.cursor()
        cursor.execute(query)
        try:
            result = cursor.fetchall()
        except cn.errors.InterfaceError:
            result = None

        con.commit()
        cursor.close()
        con.close()

        return result

    def select_all(self, table: str) -> str:
        query = "SELECT * FROM {}".format(table)

        return self._execute_query(query)

    def select(self, table: str, columns: List[str], where: Optional[List[str]] = None) -> str:

        if where:
            where = " WHERE " + " AND ".join(where)
        else:
            where = ""

        query = "SELECT %s FROM %s %s" % (", ".join(columns), table, where)

        return self._execute_query(query)

    def insert(self, table: str, values: list):
        # enquote_all(values)

        columns = ", ".join(self.tables[table])
        values = ", ".join(values)

        query = f"""INSERT INTO {table} ({columns}) VALUES ({values})"""

        self._execute_query(query)

    def _drop(self, table: str):
        query = f"DROP TABLE {table}"
        self._execute_query(query)


Dao = Dao()
