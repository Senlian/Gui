#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import wx
import gc
import time
import threading
from unit import id as uid
from unit import systemd
from unit import dialog
from config import settings


class DoTask(threading.Thread):
    def __init__(self, **kwargs):
        super(DoTask, self).__init__()
        # 跟随主线程一起退出
        self.setDaemon(True)
        # 标识线程是否停止
        self.__runing = threading.Event()
        # 标识线程是否暂停
        self.__pause = threading.Event()
        # 数据
        self.nodes = []

        self.root = wx.FindWindowById(uid.ROOT_FRAME)
        self.dialog = dialog.DialogBox(self.root)

        self.Device = systemd.DeviceLock()
        self.SystemWindow = systemd.Window(self.dialog)

        self.MenuBar = self.root.GetMenuBar()
        self.ToolBar = kwargs.get('ToolBar', None)
        self.taskId = kwargs.get('taskId', None)

    # TODO: 设置数据
    def setData(self, nodes=[]):
        self.nodes = nodes
        return self.nodes

    @property
    def isStoped(self):
        return not self.__runing.isSet()

    @property
    def isPaused(self):
        return not self.__pause.isSet()

    # TODO: 重构线程开始方法，设置标志位
    def start(self):
        self.__runing.set()
        self.__pause.set()
        return super(DoTask, self).start()

    # TODO: 停止
    def stop(self):
        # 释放锁
        self.dbLock()
        self.__runing.clear()
        self.__pause.set()
        self.Device.Release()
        return gc.collect()

    # TODO: 暂停
    def pause(self):
        self.__pause.clear()
        self.Device.Release()
        return gc.collect()

    # TODO: 继续
    def restart(self):
        self.__pause.set()
        return gc.collect()

    # TODO: 准备动作
    def prepare(self):
        # 获得锁
        self.dbLock()
        if settings.DO_PREPARE:
            if os.path.isfile(settings.PRE_PY_SCRIPT) and settings.PRE_PY_SCRIPT.lower().endswith('.py'):
                systemd.ShellCommond("python {0}".format(settings.PRE_PY_SCRIPT))
            else:
                self.dialog.warn('环境准备脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)

    # TODO: 解决后台刷新任务开启，数据库死锁问题
    def dbLock(self):
        self.workspace = wx.FindWindowById(uid.WORKSPACE)
        self.dbthread = self.workspace.deamon
        if self.dbthread and self.dbthread.isAlive():
            if not self.dbthread.isPaused:
                self.dbthread.pause()
                self.dbthread.locked = False
            else:
                if not self.dbthread.locked:
                    self.dbthread.restart()
                    self.dbthread.locked = True

    # TODO: 恢复动作
    def restore(self):
        if self.ToolBar:
            self.ToolBar.ToggleButton(self.taskId)
        if settings.DO_AFTER:
            if os.path.isfile(settings.AFTER_PY_SCRIPT) and settings.AFTER_PY_SCRIPT.lower().endswith('.py'):
                systemd.ShellCommond("python {0}".format(settings.AFTER_PY_SCRIPT))
            else:
                self.dialog.warn('环境恢复脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)
        if settings.DO_REDIS:
            if os.path.isfile(settings.REDIS_PY_SCRIPT) and settings.REDIS_PY_SCRIPT.lower().endswith('.py'):
                systemd.ShellCommond("python {0}".format(settings.REDIS_PY_SCRIPT))
            else:
                self.dialog.warn('Redis操作脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)
        if settings.DO_MONGO:
            if os.path.isfile(settings.MONGO_PY_SCRIPT) and settings.MONGO_PY_SCRIPT.lower().endswith('.py'):
                systemd.ShellCommond("python {0}".format(settings.MONGO_PY_SCRIPT))
            else:
                self.dialog.warn('MongoDB操作脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)
        return gc.collect()

    # TODO: 开服操作
    def openJob(self, node):
        if node.GetStatus() == -1:
            return False
        # 首先判断进程是否存在
        workdir = node.GetDirName()
        exe = node.GetExe()
        arg = node.GetArg()
        pid = systemd.FindPids(workdir, exe, arg)
        status = node.GetStatus() + 1 if node.GetStatus() < 1 else 1
        DEBUG = self.MenuBar.FindItemById(uid.MENUBAR_MENU_DEBUG).IsChecked()
        # 进程存在
        if systemd.IsAlivePid(pid):
            # 自动跳过
            if self.MenuBar.FindItemById(uid.MENUBAR_MENU_JUMP).IsChecked():
                IGNORE = wx.ID_OK
            else:
                self.Device.Release()
                IGNORE = self.dialog.warn("进程{0}已开启，PID为‘{1}’，点击‘确定’跳过本次操作！".format(node.GetDirPath(), pid))

            # 跳过操作
            if IGNORE == wx.ID_OK:
                # 非DEBUG模式，做界面操作
                if not DEBUG:
                    if not self.SystemWindow.CheckGuiByPid(pid):
                        self.Device.Release()
                        self.dialog.danger('程序窗口可能未正常打开！', caption='风险提示', style=wx.OK | wx.ICON_AUTH_NEEDED)
                        status = 2
                port = systemd.GetPortByPid(pid, 3)
                node.SetGridValue(pid=pid, port=port, status=status)
                return (status == 1 and not DEBUG)

        # 进程不存在，进程开服操作
        newPid, newPort = systemd.ExecuteExe(workdir, exe, arg)
        # 判断进程是否开启正确
        if not systemd.IsRightProcess(newPid, workdir, exe, arg):
            oldPid = systemd.FindPids(workdir, exe, arg)
            if not oldPid or (oldPid == newPid):
                self.Device.Release()
                self.dialog.error('开服操作异常，进程未正确开启！', caption='未知错误', style=wx.OK | wx.ICON_ERROR)
                node.SetGridValue(pid=None, port=None, status=2)
                return (status == 1 and not DEBUG)
            else:
                if not self.MenuBar.FindItemById(uid.MENUBAR_MENU_JUMP).IsChecked():
                    self.Device.Release()
                    self.dialog.warn('开服操作异常，但进程已开启！', caption='警告')
                newPid = oldPid
                newPort = systemd.GetPortByPid(newPid)

        # 非DEBUG模式，做界面操作
        if not DEBUG:
            if not self.SystemWindow.CheckGuiByPid(newPid):
                self.Device.Release()
                self.dialog.danger('程序窗口可能未正常打开！', caption='风险提示', style=wx.OK | wx.ICON_AUTH_NEEDED)
                status = 2
        self.Device.Release()
        node.SetGridValue(pid=newPid, port=newPort, status=status)
        return (status == 1 and not DEBUG)

    # TODO: 关服操作
    def killJob(self, node):
        workdir = node.GetDirName()
        exe = node.GetExe()
        arg = node.GetArg()
        pid = node.GetPid()
        status = 0
        DEBUG = self.MenuBar.FindItemById(uid.MENUBAR_MENU_DEBUG).IsChecked()
        # pid不正确，修正pid
        if not systemd.IsRightProcess(pid, workdir, exe, arg):
            pid = systemd.FindPids(workdir, exe, arg)
        # pid不存在
        if not systemd.IsAlivePid(pid):
            node.SetGridValue(pid=None, port=None, status=status)
            return (status == 0 and not DEBUG)
        pid = int(pid)
        # DEBUG模式
        if DEBUG:
            systemd.TaskKillByPid(pid)
        else:
            if not self.SystemWindow.CloseWindowByPid(pid):
                systemd.TaskKillByPid(pid)
        if not DEBUG and systemd.IsAlivePid(pid):
            self.Device.Release()
            self.dialog.danger('大哥，实在是关不掉！', caption='没搞定', style=wx.OK | wx.ICON_AUTH_NEEDED)
            node.SetGridValue(status=2)
            return (status == 0 and not DEBUG)
        if node.GetStatus() == -1:
            status = -1
        self.Device.Release()
        node.SetGridValue(pid=None, port=None, status=status)
        return (status == 0 and not DEBUG)

    # TODO: 重构run方法
    def run(self):
        self.prepare()
        for node in self.nodes:
            self.__pause.wait()
            if self.isStoped:
                return True
            ifwait = False
            if self.taskId in [uid.GRID_POPUPMENU_START, uid.TOOLBAR_START]:
                ifwait = self.openJob(node)
            else:
                ifwait = self.killJob(node)

            if ifwait:
                time.sleep(settings.HOLD)
        self.stop()
        self.restore()


if __name__ == '__main__':
    pass
