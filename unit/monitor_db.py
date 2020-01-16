#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import wx
import gc
import time
import threading
from playhouse.sqlite_ext import SqliteExtDatabase

from config import settings
from db.models import ProcessList, ProcessArgs, db
from db.read_sql import ReadSqlDB
from unit import systemd


# db = SqliteExtDatabase(database=settings.SQLLITE3,
#                        pragmas={'journal_mode': 'wal', 'foreign_keys': 'ON'})

class ProcessNode(object):
    def __init__(self, series):
        self.series = series

    @property
    def process_id(self):
        return int(self.series['process_id'])

    @property
    def arg_id(self):
        return int(self.series['id'])

    @property
    def workdir(self):
        return self.series['dirpath']

    @property
    def exe(self):
        return self.series['exe']

    @property
    def workpath(self):
        return os.path.join(self.workdir, self.exe)

    @property
    def arg(self):
        args = self.series['parameter']
        return None if not args else str(args).strip()

    def GetPid(self):
        return int(self.series['pid'])

    def GetPort(self):
        return int(self.series['port'])

    def GetStatus(self):
        return int(self.series['status'])

    def FindPid(self):
        fpid = systemd.FindPids(self.workdir, self.exe, self.arg)
        return fpid if fpid else -1

    @db.atomic()
    def update(self):
        pid = self.GetPid()
        port = self.GetPort()
        status = self.GetStatus()

        if not os.path.exists(self.workpath):
            pid = None
            port = None
            status = -1
        else:
            newPid = self.FindPid()

            if pid != newPid:
                pid = newPid

            if systemd.IsAlivePid(pid):
                newPort = systemd.GetPortByPid(pid)
                if port != newPort:
                    port = newPort
                if status > -1:
                    status = 1
            else:
                pid = None
                port = None
                if status > -1:
                    status = 0

        if self.GetPid() == pid and self.GetPort() == port and self.GetStatus() == status:
            return False

        data = {'pid': pid, 'port': port, 'status': status}
        if self.arg_id > 0:
            sql = ProcessArgs.update(data).where(
                (ProcessArgs.id == self.arg_id) & (ProcessArgs.process == self.process_id))
        else:
            data.update({'process_id': self.process_id})
            data.update({'exe': self.exe})
            data.update({'parameter': self.arg})
            sql = ProcessArgs.insert(data)
        sql.execute()
        return True


class MonitorDatabase(threading.Thread):
    def __init__(self):
        super(MonitorDatabase, self).__init__()
        self.setDaemon(True)
        self.__pause = threading.Event()
        self.__pause.set()
        # 数据库是否有锁
        self.locked = True

    @property
    def isPaused(self):
        return not self.__pause.isSet()

    # TODO: 暂停
    def pause(self):
        self.__pause.clear()
        return gc.collect()

    # TODO: 继续
    def restart(self):
        self.__pause.set()
        return gc.collect()

    def monitor(self):
        df = ReadSqlDB(ProcessList, index_col='id').get_process()
        for index, series in df.iterrows():
            yield ProcessNode(series)

    def run(self):
        while settings.FRESH_DB:
            # 暂停控制
            self.__pause.wait()
            for node in self.monitor():
                self.__pause.wait()
                node.update()
            time.sleep(settings.FREQUENCY)
            gc.collect()


if __name__ == '__main__':
    t = MonitorDatabase()
    t.run()
