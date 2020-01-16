#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import wx
import wx.adv

from unit import icon
from unit import dialog
from unit import id as uid
from unit import functions as func
from config import settings
from unit.do_tasks import DoTask
from unit import systemd


# TODO: 工具栏
class ToolBar(wx.ToolBar):
    def __init__(self, parent=None, id=uid.TOOLBAR):
        super(ToolBar, self).__init__(parent=parent, id=id, style=wx.TB_NODIVIDER | wx.TB_FLAT, name=u'工具栏')
        self.parent = parent
        self.NowJob = None
        self.dialog = dialog.DialogBox(self.parent)
        self.__settings__()
        self.__bind__()

    # TODO: 添加工具项
    def __settings__(self):
        self.AddTool(uid.TOOLBAR_START, 'start', icon.TB_START.GetBitmap(), u'开服').SetClientData(True)
        self.AddTool(uid.TOOLBAR_PAUSE, 'pause', icon.TB_PAUSE.GetBitmap(), u'暂停').SetClientData(True)
        self.AddTool(uid.TOOLBAR_CLOSE, 'close', icon.TB_CLOSE.GetBitmap(), u'关服').SetClientData(True)
        self.AddTool(uid.TOOLBAR_REFRESH, 'refresh', icon.TB_REFRESH.GetBitmap(), u'刷新')
        self.AddStretchableSpace()
        self.AddTool(uid.TOOLBAR_REDIS, 'redis', icon.TB_REDIS.GetBitmap(), u'Redis备份').SetClientData(True)
        # self.AddSeparator()
        self.AddTool(uid.TOOLBAR_MONGO, 'mongo', icon.TB_MONGO.GetBitmap(), u'Mongo备份').SetClientData(True)

        self.tree = self.FindWindowById(uid.PROCESS_PAGE_TREE)
        enable = False if (not self.tree) else bool(self.tree.GetAllCheckedChilds([], self.tree.GetSelection()))
        # 没有勾选进程树，默认不可用
        self.EnableTool(uid.TOOLBAR_START, enable)
        self.EnableTool(uid.TOOLBAR_PAUSE, False)
        self.EnableTool(uid.TOOLBAR_CLOSE, enable)
        self.Realize()

    # TODO: 工具栏监听事件
    def __bind__(self):
        self.Bind(wx.EVT_TOOL, self.StartThread, id=uid.TOOLBAR_START)
        self.Bind(wx.EVT_TOOL, self.StartThread, id=uid.TOOLBAR_PAUSE)
        self.Bind(wx.EVT_TOOL, self.StartThread, id=uid.TOOLBAR_CLOSE)
        self.Bind(wx.EVT_TOOL, self.OnFresh, id=uid.TOOLBAR_REFRESH)
        self.Bind(wx.EVT_TOOL, self.OnScript, id=uid.TOOLBAR_REDIS)
        self.Bind(wx.EVT_TOOL, self.OnScript, id=uid.TOOLBAR_MONGO)

    def OnScript(self, e):
        eId = e.GetId()
        if self.dialog.danger('该动作可能会造成不可逆的数据丢失，确定要执行吗？') == wx.ID_OK:
            if eId == uid.TOOLBAR_REDIS:
                if os.path.isfile(settings.REDIS_PY_SCRIPT) and settings.REDIS_PY_SCRIPT.lower().endswith('.py'):
                    systemd.ShellCommond("python {0}".format(settings.REDIS_PY_SCRIPT))
                else:
                    self.dialog.warn('Redis操作脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)
            if eId == uid.TOOLBAR_MONGO:
                if os.path.isfile(settings.MONGO_PY_SCRIPT) and settings.MONGO_PY_SCRIPT.lower().endswith('.py'):
                    systemd.ShellCommond("python {0}".format(settings.MONGO_PY_SCRIPT))
                else:
                    self.dialog.warn('MongoDB操作脚本不正确！', style=wx.OK | wx.ICON_EXCLAMATION)
        if e:
            return e.Skip()

    # TODO: 刷新
    def OnFresh(self, e):
        if self.NowJob and self.NowJob.isAlive() and not self.NowJob.isPaused:
            return False
        grid = wx.FindWindowById(uid.PROCESS_PAGE_GRID)
        tree = wx.FindWindowById(uid.PROCESS_PAGE_TREE)
        wx.CallAfter(grid.ReLoad)
        wx.CallAfter(tree.ReLoadTree)
        return True

    # TODO: 按钮形态切换
    def ToggleButton(self, e):
        eId = e if not isinstance(e, wx._core.CommandEvent) else e.GetId()
        if not self.GetToolEnabled(eId):
            return False
        eItem = self.FindById(eId)
        eHelp = eItem.GetShortHelp()
        eData = eItem.GetClientData()
        # 设置状态栏显示内容
        self.parent.SetStatusText(eHelp, 2)
        if eId not in [uid.TOOLBAR_START, uid.TOOLBAR_PAUSE, uid.TOOLBAR_CLOSE]:
            return False
        # 切换按钮标识
        self.SetToolClientData(eId, not eData)
        if eId == uid.TOOLBAR_START:
            self.ToggleStartTool(eData)
        if eId == uid.TOOLBAR_PAUSE:
            self.TogglePauseTool(eData)
        if eId == uid.TOOLBAR_CLOSE:
            self.ToggleCloseTool(eData)
        self.Realize()
        if isinstance(e, wx._core.CommandEvent):
            e.Skip()
        return True

    # TODO: 开服/停止按钮
    def ToggleStartTool(self, eData):
        help = '停止' if eData else '开服'
        b64 = icon.TB_STOP if eData else icon.TB_START
        # 切换图标
        self.SetToolNormalBitmap(uid.TOOLBAR_START, b64.GetBitmap())
        # 切换帮助
        self.SetToolShortHelp(uid.TOOLBAR_START, help)

        # 切换关闭按钮状态
        self.EnableTool(uid.TOOLBAR_CLOSE, not eData)
        # 暂停按钮恢复
        if not self.FindById(uid.TOOLBAR_PAUSE).GetClientData():
            self.ToggleButton(uid.TOOLBAR_PAUSE)
        self.EnableTool(uid.TOOLBAR_PAUSE, eData)

    # TODO: 暂停/继续按钮
    def TogglePauseTool(self, eData=True):
        help = '继续' if eData else '暂停'
        b64 = icon.TB_CONTINUE if eData else icon.TB_PAUSE
        # 切换图标
        self.SetToolNormalBitmap(uid.TOOLBAR_PAUSE, b64.GetBitmap())
        # 切换帮助
        self.SetToolShortHelp(uid.TOOLBAR_PAUSE, help)

    # TODO: 关服/停止按钮
    def ToggleCloseTool(self, eData=True):
        help = '停止' if eData else '关服'
        b64 = icon.TB_STOP if eData else icon.TB_CLOSE
        # 切换图标
        self.SetToolNormalBitmap(uid.TOOLBAR_CLOSE, b64.GetBitmap())
        # 切换帮助
        self.SetToolShortHelp(uid.TOOLBAR_CLOSE, help)

        # 切换开服按钮状态
        self.EnableTool(uid.TOOLBAR_START, not eData)
        # 切换暂停按钮状态
        if not self.FindById(uid.TOOLBAR_PAUSE).GetClientData():
            self.ToggleButton(uid.TOOLBAR_PAUSE)
        self.EnableTool(uid.TOOLBAR_PAUSE, eData)

    # TODO: 开始任务线程
    def StartThread(self, e):
        if not e:
            return True
        eId = e if not (isinstance(e, wx._core.CommandEvent)) else e.GetId()
        self.ToggleButton(eId)

        # 暂停任务
        if eId == uid.TOOLBAR_PAUSE and self.NowJob:
            if self.NowJob.isPaused:
                self.NowJob.restart()
            else:
                self.NowJob.pause()

        if eId in [uid.TOOLBAR_START, uid.TOOLBAR_CLOSE]:
            prePause = False
            if self.NowJob:
                # 获取之前的暂停状态以便状态恢复
                prePause = self.NowJob.isPaused
                # 暂停当前任务，等待确认
                self.NowJob.pause()

            if self.dialog.warn() == wx.ID_CANCEL:
                # 如果任务存在且之前非暂停，继续执行
                if not prePause and self.NowJob:
                    self.NowJob.restart()
                # 切换按钮形态
                self.ToggleButton(eId)
                # 如果之前是暂停态，其他按钮切换状态时已经重置了暂停按钮，需要恢复
                if prePause:
                    self.ToggleButton(uid.TOOLBAR_PAUSE)
                return e.Skip()

            if self.NowJob and self.NowJob.isAlive():
                self.NowJob.stop()
                self.NowJob = None
            else:
                del self.NowJob
                self.NowJob = DoTask(ToolBar=self, taskId=e.GetId())
                self.tree = self.FindWindowById(uid.PROCESS_PAGE_TREE)
                # 获取数据，关服将数据逆序
                nodes = self.tree.GetAllCheckedGridItems(self.tree.GetSelection(), eId == uid.TOOLBAR_CLOSE)
                self.NowJob.setData(nodes)
                self.NowJob.start()
        if isinstance(e, wx._core.CommandEvent):
            e.Skip()

    # TODO: 标识是否可以切换分页
    def switch(self):
        start = self.FindById(uid.TOOLBAR_START).GetClientData()
        pause = self.FindById(uid.TOOLBAR_PAUSE).GetClientData()
        close = self.FindById(uid.TOOLBAR_CLOSE).GetClientData()
        return (start and pause and close)


class ToolBarTwo(wx.ToolBar):
    def __init__(self, parent=None, id=uid.TOOLBAR_TWO):
        super(ToolBarTwo, self).__init__(parent=parent, id=id, style=wx.TB_NODIVIDER | wx.TB_FLAT, name=u'工具栏')
        self.parent = parent

    def switch(self):
        return True
