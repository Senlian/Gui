# !/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: ProcessManager.py

@time: 2018/8/13 9:03

@module:python -m pip install wxpython

@desc:To start Game processes and Record the pid.
'''

import re, glob
import time, gc, psutil, subprocess
import threading, multiprocessing
import os, sys, json, csv, win32file, chardet
import wx.stc as STC
import wx, wx.adv, wx.grid, wx.ribbon
import wx.lib.agw.customtreectrl as CT

from common import frozen
from common.B64data import *
from common.SenLian_FLID import *
from common.SenLian_Process import *
from common.Senlian_Win32 import Window, SystemDevice

reload(sys)
sys.setdefaultencoding('utf-8')

AFTER_PY_SCRIPT = os.path.abspath("./after.py")
LOG_FILE_PATH = os.path.abspath("./ProcessManager.log")
MONGO_PY_SCRIPT = os.path.abspath("./mongo_backup.py")
PRE_PY_SCRIPT = os.path.abspath("./prepare.py")
REDIS_PY_SCRIPT = os.path.abspath("./redis_backup.py")

scriptPath = os.path.normpath(os.path.abspath(__file__))
scriptDir = os.path.dirname(scriptPath)

TIME_SLEEP = 1
SystemWindow = Window()

wildcard = u"py files (*.py)|*.py|" \
           "bat files (*.bat)|*.bat|" \
           "All files (*.*)|*.*"


def wait_time(seconds):
    time.sleep(int(seconds))


def get_code(item):
    return chardet.detect(item).get("encoding", "utf-8")


# TODO: 打开资源管理器打开路径或文件
def explorer_select_file(filepath):
    if os.path.isfile(filepath):
        cmdline = 'explorer.exe /select, "{0}"'.format(filepath)
        ShellCommond(cmdline)
    elif os.path.isdir(filepath):
        os.startfile(filepath, "explore")
    else:
        return


# TODO: 打开路径
def OpenDirDialog(defaultDir='', parent=None):
    if not parent:
        return False

    dlg = wx.DirDialog(parent, message=u"打开路径",
                       defaultPath=defaultDir,
                       style=wx.DD_DEFAULT_STYLE)
    targetDir = defaultDir
    if dlg.ShowModal() == wx.ID_OK:
        targetDir = dlg.GetPath()
    dlg.Destroy()
    return targetDir


# TODO: 打开文件
def OpenFileDialog(defaultDir='', defaultFile='', parent=None):
    if not defaultDir:
        defaultDir = defaultFile
    if not parent:
        return False

    dlg = wx.FileDialog(parent, message=u"另存为",
                        defaultDir=defaultDir,
                        defaultFile=defaultFile,
                        wildcard=wildcard,
                        style=wx.FD_OPEN)
    targetFile = defaultFile
    if dlg.ShowModal() == wx.ID_OK:
        targetFile = dlg.GetPath()
    dlg.Destroy()
    return targetFile


# TODO: 主框架
class RootFrame(wx.Frame):
    def __init__(self, parent=None):
        super(RootFrame, self).__init__(parent=parent, id=ID_RootFrame, style=wx.DEFAULT_FRAME_STYLE)
        self.settings()
        wx.CallAfter(self.initUI)

    def settings(self):
        self.SetTitle(u'游戏进程管理器--v.2019.01.18.01')
        self.SetSize((1080, 720))
        self.SetTransparent(230)
        self.TaskBarIcon = None
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(PyEmbeddedImage(B64_POKER128).GetIcon())
        self.Center()
        # self.JsonObj = json.loads(open('./startApp.json', 'r').read().replace('\\', '/'))

    @property
    def JsonObj(self):
        _curDir = os.getcwd()
        os.chdir(scriptDir)
        fp = open('./startApp.json', 'r')
        data = fp.read().replace('\\', '/')
        fp.close()
        os.chdir(_curDir)
        return json.loads(data)

    def initUI(self):
        MenuBar(self)
        ToolBar(self)
        StatusBar(self)
        wx.CallAfter(MidWindow, self)

        self.Bind(wx.EVT_CLOSE, self.OnExit, self)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)

    def infoBox(self, msg="页面加载中...", style=wx.ICON_INFORMATION):
        # 释放鼠标
        SystemDevice.Release()
        infoDialog = wx.MessageDialog(parent=self, message=msg, caption="提示", style=style)
        return infoDialog.ShowModal()

    def warnBox(self, msg="确认要继续操作吗?", style=wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION):
        SystemDevice.Release()
        warnDialog = wx.MessageDialog(parent=self, message=msg, caption="警告", style=style)
        return warnDialog.ShowModal()

    def errorBox(self, msg="操作失败,请排查原因！", style=wx.OK | wx.CANCEL | wx.ICON_ERROR):
        SystemDevice.Release()
        errorDialog = wx.MessageDialog(parent=self, message=msg, caption="错误", style=style)
        return errorDialog.ShowModal()

    def OnIconfiy(self, e):
        if not self.IsIconized():
            if not self.IsShown():
                self.Show()
                self.Raise()
        else:
            if self.IsShown():
                self.Hide()
            self.TaskBarIcon = TaskBarIcon(self)
        return e.Skip()

    def OnExit(self, e):
        self.SetStatusText('正在退出...', 1)
        try:
            MidWindow = self.FindWindowById(ID_MidWindow, self)
            self.SetStatusText('线程退出...', 2)
            MidWindow.PageOne.RightPanel.ReSetJob()
            self.SetStatusText('数据保存...', 2)
            MidWindow.PageOne.RightPanel.SaveToCsv()
            self.SetStatusText('日志保存...', 2)
            MidWindow.PageTwo.SaveToFile(e)
        except Exception as e:
            print(e)
        finally:
            SystemDevice.Release()
        self.Destroy()
        if e:
            e.Skip()
        wait_time(TIME_SLEEP)
        return wx.GetApp().ExitMainLoop()


# TODO: 菜单栏
class MenuBar(wx.MenuBar):
    def __init__(self, parent=None, id=ID_MenuBar):
        super(MenuBar, self).__init__()
        if parent:
            self.parent = parent
            self.setItems()
            self.parent.SetMenuBar(self)

    def setItems(self):
        FileMenu = wx.Menu()
        OptionMenu = wx.Menu()
        ViewMenu = wx.Menu()
        HelpMenu = wx.Menu()

        FileMenu.Append(ID_OpenDir, u"打开目录(&O)\tCtrl+O", u"打开目录")
        FileMenu.Append(wx.ID_FILE, u"设置(&S)...\tCtrl+S", u"设置")
        FileMenu.AppendSeparator()
        FileMenu.Append(wx.ID_EXIT, u"退出(&Q)...\tCtrl+Q", u"退出")

        OptionMenu.Append(ID_PREPARE, u"环境准备脚本", u"执行环境准备脚本", kind=wx.ITEM_CHECK).Check()
        OptionMenu.Append(ID_REDIS, u"备份Redis脚本", u"执行Redis备份脚本", kind=wx.ITEM_CHECK).Check()
        OptionMenu.Append(ID_MONGO, u"备份Mongo脚本", u"执行Mongo备份脚本", kind=wx.ITEM_CHECK).Check()
        OptionMenu.Append(ID_AFTER, u"环境恢复脚本", u"执行环境恢复脚本", kind=wx.ITEM_CHECK).Check()
        OptionMenu.AppendSeparator()
        OptionMenu.Append(wx.ID_JUMP_TO, u"自动跳过", u"自动跳过已启动项", kind=wx.ITEM_CHECK).Check()
        OptionMenu.AppendSeparator()
        OptionMenu.Append(ID_TEST, u"测试服使用", u"不校验界面方式开关进程", kind=wx.ITEM_CHECK)

        self.Tools = ViewMenu.Append(ID_ToolBar, u'工具栏(&T)', u'工具栏', kind=wx.ITEM_CHECK)
        self.Tools.Check(True)
        self.Status = ViewMenu.Append(ID_StatusBar, u'状态栏(&S)', u'状态栏', kind=wx.ITEM_CHECK)
        self.Status.Check(True)

        HelpMenu.Append(wx.ID_HELP, u"说明(&H)", u"工具帮助信息")
        HelpMenu.Append(wx.ID_ABOUT, u"关于(&A)", u"作者@senlian")

        self.Append(FileMenu, u'文件(&F)')
        self.Append(OptionMenu, u'选项(&O)')
        self.Append(ViewMenu, u'查看(&H)')
        self.Append(HelpMenu, u'帮助(&H)')

        FileMenu.Bind(wx.EVT_MENU, self.OpenWorkDir, id=ID_OpenDir)
        FileMenu.Bind(wx.EVT_MENU, self.FileMenuEvt, id=wx.ID_FILE)
        FileMenu.Bind(wx.EVT_MENU, self.parent.OnExit, id=wx.ID_EXIT)

        ViewMenu.Bind(wx.EVT_MENU, self.ToggleToolBar, id=ID_ToolBar)
        ViewMenu.Bind(wx.EVT_MENU, self.ToggleStatusBar, id=ID_StatusBar)

    # 打开工作目录
    def OpenWorkDir(self, e):
        toolpath = os.path.splitext(scriptPath)[0] + '.exe'
        toolpath = toolpath if os.path.isfile(toolpath) else scriptPath
        explorer_select_file(toolpath)
        e.Skip()

    # 文件菜单事件
    def FileMenuEvt(self, e):
        setDialog = SetBasicDialog(self.parent, u'设置面板')
        if setDialog.ShowModal() == wx.ID_OK:
            setDialog.SetGlobal()
        e.Skip()

    # 工具栏显隐
    def ToggleToolBar(self, e):
        ToolBar = self.parent.GetToolBar()
        if self.Tools.IsChecked():
            ToolBar.Show()
        else:
            ToolBar.Hide()
        ToolBar.Realize()
        if e:
            e.Skip()

    # 状态栏显隐
    def ToggleStatusBar(self, e):
        BtmStatusBar = self.parent.GetStatusBar()
        if self.Status.IsChecked():
            StatusBar(self.parent)
            curPath = self.FindWindowById(ID_MidWindow, self.parent).PageOne.LeftPanel.GetPath()
            self.parent.SetStatusText(curPath, 0)
        else:
            BtmStatusBar.Destroy()
        if e:
            e.Skip()


# TODO: 工具栏
class ToolBar(wx.ToolBar):
    def __init__(self, parent=None, id=ID_ToolBar):
        super(ToolBar, self).__init__(parent=parent, id=id, style=wx.TB_NODIVIDER | wx.TB_FLAT, name=u'工具栏')
        self.root = parent
        if self.root:
            self.setItems()
            self.Realize()
            self.root.SetToolBar(self)
            # self.Bind(wx.EVT_TOOL, self.ToggleBitmap)

    def setItems(self):
        self.AddTool(ID_Start, 'start', GetBitmap(B64_START24), u'开服').SetClientData(True)
        self.AddTool(ID_Pause, 'pause', GetBitmap(B64_PAUSE24), u'暂停').SetClientData(True)
        self.AddTool(ID_Close, 'close', GetBitmap(B64_CLOSE24), u'关服').SetClientData(True)
        self.AddTool(wx.ID_REFRESH, 'refresh', GetBitmap(B64_REFRESH24), u'刷新').SetClientData(True)
        self.AddStretchableSpace()
        self.AddTool(ID_REDIS, 'redis', GetBitmap(B64_REDIS24), u'Redis').SetClientData(True)
        self.AddTool(ID_MONGO, 'mongo', GetBitmap(B64_MONGO24), u'Mongo').SetClientData(True)
        # self.FindById(ID_REDIS).GetPosition()
        # self.InsertSeparator(pos=4)
        self.EnableTool(ID_Start, False)
        self.EnableTool(ID_Pause, False)
        self.EnableTool(ID_Close, False)

    def ToggleBitmap(self, curId):
        # curId = e.GetId()
        curItem = self.FindById(curId)

        preHelp = curItem.GetShortHelp()
        preData = curItem.GetClientData()
        self.root.SetStatusText(preHelp, 2)

        if curId != ID_Pause:
            if curId == ID_Start:
                self.EnableTool(ID_Close, not preData)
            if curId == ID_Close:
                self.EnableTool(ID_Start, not preData)
            if not preData:
                self.SetPauseToolStyle(preData)
            self.EnableTool(ID_Pause, preData)
            self.SetStartToolStyle(preData)
            self.SetCloseToolStyle(preData)
        else:
            self.SetPauseToolStyle(preData)

        self.Realize()

    def SetStartToolStyle(self, flag=True):
        if not self.GetToolEnabled(ID_Start):
            return
        bitmap = B64_STOP24 if flag else B64_START24
        help = u"停止" if flag else u"开服"

        self.SetToolNormalBitmap(ID_Start, GetBitmap(bitmap))
        self.SetToolShortHelp(ID_Start, help)
        self.SetToolClientData(ID_Start, not flag)

    def SetPauseToolStyle(self, flag=True):
        if not self.GetToolEnabled(ID_Pause):
            return
        bitmap = B64_GOON24 if flag else B64_PAUSE24
        help = u"继续" if flag else u"暂停"

        self.SetToolNormalBitmap(ID_Pause, GetBitmap(bitmap))
        self.SetToolShortHelp(ID_Pause, help)
        self.SetToolClientData(ID_Pause, not flag)

    def SetCloseToolStyle(self, flag=True):
        if not self.GetToolEnabled(ID_Close):
            return
        bitmap = B64_STOP24 if flag else B64_CLOSE24
        help = u"停止" if flag else u"关服"

        self.SetToolNormalBitmap(ID_Close, GetBitmap(bitmap))
        self.SetToolShortHelp(ID_Close, help)
        self.SetToolClientData(ID_Close, not flag)


# TODO: 状态栏
class StatusBar(wx.StatusBar):
    def __init__(self, parent=None, id=ID_StatusBar):
        super(StatusBar, self).__init__(parent=parent, id=id, style=65840, name=u'状态栏')
        self.SetFieldsCount(3)
        self.SetStatusWidths([-2, -2, -1])
        self.Show()
        if parent:
            parent.SetStatusBar(self)


# TODO: 设置面板
class SetBasicDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SetBasicDialog, self).__init__(parent, title=title, size=(480, 260))
        self.root = parent
        self.initUI()
        self.GetSettings()

    def initUI(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        gridBox = wx.FlexGridSizer(5, 3, 18, 5)

        PrePyLabel = wx.StaticText(self, label=u'环境准备脚本', size=(120, 20))
        self.PrePyText = wx.TextCtrl(self, size=(240, 20), value=PRE_PY_SCRIPT)
        PrePyBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        RedisPathLabel = wx.StaticText(self, label=u'Redis备份脚本', size=(120, 20))
        self.RedisPathText = wx.TextCtrl(self, size=(240, 20), value=REDIS_PY_SCRIPT)
        RedisPathBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        MongoPathLabel = wx.StaticText(self, label=u'Mongo备份脚本', size=(120, 20))
        self.MongoPathText = wx.TextCtrl(self, size=(240, 20), value=MONGO_PY_SCRIPT)
        MongoPathBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        AfterPyLabel = wx.StaticText(self, label=u'环境恢复脚本', size=(120, 20))
        self.AfterPyText = wx.TextCtrl(self, size=(240, 20), value=AFTER_PY_SCRIPT)
        AfterPyBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        TimeSleepLabel = wx.StaticText(self, label=u'停顿时间', size=(120, 20))
        self.TimeSleepText = wx.TextCtrl(self, size=(240, 20), value=str(TIME_SLEEP))
        TimeSleepUnit = wx.StaticText(self, label=u'秒', size=(120, 20))

        gridBox.Add(PrePyLabel)
        gridBox.Add(self.PrePyText, 1, wx.EXPAND)
        gridBox.Add(PrePyBTN)

        gridBox.Add(RedisPathLabel)
        gridBox.Add(self.RedisPathText, 1, wx.EXPAND)
        gridBox.Add(RedisPathBTN)

        gridBox.Add(MongoPathLabel)
        gridBox.Add(self.MongoPathText, 1, wx.EXPAND)
        gridBox.Add(MongoPathBTN)

        gridBox.Add(AfterPyLabel)
        gridBox.Add(self.AfterPyText, 1, wx.EXPAND)
        gridBox.Add(AfterPyBTN)

        gridBox.Add(TimeSleepLabel)
        gridBox.Add(self.TimeSleepText, 1, wx.EXPAND)
        gridBox.Add(TimeSleepUnit)

        wx.Button(self, wx.ID_OK, label=u"确认", size=(50, 20), pos=(180, 200))
        wx.Button(self, wx.ID_CANCEL, label=u"取消", size=(50, 20), pos=(260, 200))

        vBox.Add(gridBox, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)
        self.SetSizer(vBox)

        self.Bind(wx.EVT_BUTTON, self.SetRrePyPath, PrePyBTN)
        self.Bind(wx.EVT_BUTTON, self.SetRedisPath, RedisPathBTN)
        self.Bind(wx.EVT_BUTTON, self.SetMongoPath, MongoPathBTN)
        self.Bind(wx.EVT_BUTTON, self.SetAfterPyPath, AfterPyBTN)

    def GetSettings(self):
        self.prepareScript = self.PrePyText.GetValue()
        self.redisScript = self.RedisPathText.GetValue()
        self.mongoScript = self.MongoPathText.GetValue()
        self.afterScript = self.AfterPyText.GetValue()
        self.timeSleep = self.TimeSleepText.GetValue()

    def SetRrePyPath(self, e):
        _newpath = OpenFileDialog(PRE_PY_SCRIPT, PRE_PY_SCRIPT, self)
        self.PrePyText.SetValue(_newpath)
        self.GetTemplate()
        if e:
            e.Skip()

    def SetRedisPath(self, e):
        _newpath = OpenFileDialog(REDIS_PY_SCRIPT, REDIS_PY_SCRIPT, self)
        self.RedisPathText.SetValue(_newpath)
        self.GetTemplate()
        if e:
            e.Skip()

    def SetMongoPath(self, e):
        _newpath = OpenFileDialog(MONGO_PY_SCRIPT, MONGO_PY_SCRIPT, self)
        self.MongoPathText.SetValue(_newpath)
        self.GetTemplate()
        if e:
            e.Skip()

    def SetAfterPyPath(self, e):
        _newpath = OpenFileDialog(AFTER_PY_SCRIPT, AFTER_PY_SCRIPT, self)
        self.AfterPyText.SetValue(_newpath)
        self.GetTemplate()
        if e:
            e.Skip()

    def SetGlobal(self):
        global PRE_PY_SCRIPT, REDIS_PY_SCRIPT, MONGO_PY_SCRIPT, AFTER_PY_SCRIPT, TIME_SLEEP
        PRE_PY_SCRIPT = self.prepareScript
        REDIS_PY_SCRIPT = self.redisScript
        MONGO_PY_SCRIPT = self.mongoScript
        AFTER_PY_SCRIPT = self.afterScript
        TIME_SLEEP = int(self.TimeSleepText.GetValue())


# TODO: 主界面
class MidWindow(wx.Notebook):
    def __init__(self, parent=None, id=ID_MidWindow):
        super(MidWindow, self).__init__(parent=parent, id=id, name='Main',
                                        style=wx.NB_TOP | wx.NB_FIXEDWIDTH | wx.NB_FLAT, size=parent.GetSize())
        self.root = parent
        # self.JsonObj = self.root.JsonObj
        self.NowJob = None

        self.PageOne = FirstPage(self)
        self.PageTwo = SecondPage(self)

        self.AddPage(self.PageOne, u'主页')
        self.AddPage(self.PageTwo, u'操作日志')

        self.PageOneLeft = self.PageOne.LeftPanel
        self.PageOneRight = self.PageOne.RightPanel

        self.ToolBar = self.root.GetToolBar()
        self.ToolBar.Bind(wx.EVT_TOOL, self.BindToolEvt)
        self.ToolBar.Bind(wx.EVT_TOOL, self.SaveRedis, id=ID_REDIS)
        self.ToolBar.Bind(wx.EVT_TOOL, self.SaveMongo, id=ID_MONGO)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.PageChangeEvt)

    @property
    def JsonObj(self):
        return self.root.JsonObj

    def BindToolEvt(self, e):
        BindId = e.GetId()
        # 获取暂停键之前的状态信息
        pauseTool = self.ToolBar.FindById(ID_Pause)
        prePauseBitmap = pauseTool.GetNormalBitmap()
        prePauseShortHelp = pauseTool.GetShortHelp()
        prePauseClientData = pauseTool.GetClientData()
        if BindId in [ID_Start, ID_Close, ID_Pause]:
            self.ToolBar.ToggleBitmap(BindId)

        if BindId == ID_Pause:
            if self.NowJob:
                if self.NowJob.isPaused():
                    self.NowJob.pause()
                else:
                    self.NowJob.restart()

        if BindId in [ID_Start, ID_Close]:
            ProcessList = self.GetProcessList()
            preFlag = False if not self.NowJob else self.NowJob.isPaused()

            # 任务暂停
            if self.NowJob:
                self.NowJob.pause()

            # 取消操作
            if self.root.warnBox() == wx.ID_CANCEL:
                if self.NowJob and preFlag:
                    self.NowJob.restart()

                self.ToolBar.ToggleBitmap(BindId)
                pauseTool.SetNormalBitmap(prePauseBitmap)
                pauseTool.SetShortHelp(prePauseShortHelp)
                pauseTool.SetClientData(prePauseClientData)
                self.ToolBar.Realize()
                return e.Skip()

            if BindId is not ID_Pause:
                if self.NowJob and self.NowJob.isAlive():
                    self.NowJob.stop()
                    self.NowJob = None
                else:
                    del self.NowJob
                    self.PageTwo.AppendInfo("选择列表：\n{0}".format(",\n\r\t".join(ProcessList)))
                    self.NowJob = ThreadTask(ProcessList=ProcessList, parent=self, BindId=BindId)
                    self.NowJob.start()
        e.Skip()

    def PageChangeEvt(self, e):
        wx.CallAfter(self.SetToolBar)
        if e:
            e.Skip()

    def SetToolBar(self):
        if (self.GetCurrentPage() == self.PageTwo):
            self.ToolBar.InsertSeparator(4)
            # saveTool = self.ToolBar.CreateTool(wx.ID_SAVE, 'save', GetBitmap(B64_SAVE24), shortHelp=u'保存日志').SetClientData(True)
            # InsertTool(pos, toolId, label, bitmap, bmpDisabled=NullBitmap, kind=ITEM_NORMAL, shortHelp=EmptyString, longHelp=EmptyString, clientData=None) -> ToolBarToolBase
            self.ToolBar.InsertTool(pos=5, toolId=wx.ID_SAVE, label='save', bitmap=GetBitmap(B64_SAVE24),
                                    shortHelp=u'保存日志', clientData=True)
            self.ToolBar.InsertTool(pos=6, toolId=wx.ID_CLEAR, label='refresh', bitmap=GetBitmap(B64_CLEAR24),
                                    shortHelp=u'清空日志', clientData=True)
            self.ToolBar.InsertSeparator(7)
            # self.ToolBar.AddTool(wx.ID_CLEAR, 'refresh', GetBitmap(B64_CLEAR24), u'清空日志').SetClientData(True)
        else:
            self.ToolBar.DeleteToolByPos(7)
            self.ToolBar.DeleteToolByPos(4)
            self.ToolBar.RemoveTool(wx.ID_SEPARATOR)
            self.ToolBar.RemoveTool(wx.ID_SAVE)
            self.ToolBar.RemoveTool(wx.ID_CLEAR)
        self.ToolBar.Realize()

    def GetProcessList(self):
        return self.PageOneLeft.GetCheckedItems([], self.PageOneLeft.GetSelection())

    def GetParameters(self, exe):
        for key in self.JsonObj.keys():
            curJson = self.JsonObj.get(key, {})
            if curJson.has_key(exe):
                return curJson.get(exe, {}).get("parameters", None)
        return []

    def SaveRedis(self, e=None):
        if os.path.isfile(REDIS_PY_SCRIPT) and os.path.splitext(REDIS_PY_SCRIPT)[1].lower() == '.py':
            self.root.SetStatusText(REDIS_PY_SCRIPT, 0)
            self.root.SetStatusText("正在执行外部脚本...", 1)
            self.PageTwo.AppendWarn('正在执行外部脚本,{0}'.format(REDIS_PY_SCRIPT))
            ShellCommond("python " + REDIS_PY_SCRIPT)
            self.root.SetStatusText("脚本调用结束", 1)
            self.PageTwo.AppendInfo('脚本调用结束')
        else:
            self.root.SetStatusText("外部redis脚本不存在", 1)
            self.PageTwo.AppendError('外部准备脚本不存在,{0}'.format(REDIS_PY_SCRIPT))
        if e:
            e.Skip()

    def SaveMongo(self, e=None):
        if os.path.isfile(MONGO_PY_SCRIPT) and os.path.splitext(MONGO_PY_SCRIPT)[1].lower() == '.py':
            self.root.SetStatusText(MONGO_PY_SCRIPT, 0)
            self.root.SetStatusText("正在执行外部脚本...", 1)
            self.PageTwo.AppendWarn('正在执行外部脚本,{0}'.format(MONGO_PY_SCRIPT))
            ShellCommond("python " + MONGO_PY_SCRIPT)
            self.root.SetStatusText("脚本调用结束", 1)
            self.PageTwo.AppendInfo('脚本调用结束')
        else:
            self.root.SetStatusText("外部mongo脚本不存在", 1)
            self.PageTwo.AppendError('外部准备脚本不存在,{0}'.format(MONGO_PY_SCRIPT))
        if e:
            e.Skip()


# TODO: 主页
class FirstPage(wx.SplitterWindow):
    def __init__(self, parent=None):
        super(FirstPage, self).__init__(parent=parent, style=wx.SP_NOBORDER, size=parent.GetSize())
        self.parent = parent
        self.root = self.parent.root

        self.initUI()

    def initUI(self):
        self.RightPanel = PidGrid(self)
        self.LeftPanel = GenerateDirTree(self)
        self.SetMinimumPaneSize(200)
        self.SplitVertically(self.LeftPanel, self.RightPanel, 100)


# TODO: 操作日志
class SecondPage(STC.StyledTextCtrl):
    def __init__(self, parent=None):
        self.parent = parent
        self.root = self.parent.root
        self.TextStyle = STC.STC_STYLE_DEFAULT

        super(SecondPage, self).__init__(parent=self.parent, id=-1, style=self.TextStyle)

        self.SetMarginWidth(2, 16)
        self.SetMarginType(1, STC.STC_MARGIN_NUMBER)

        self.root.GetToolBar().Bind(wx.EVT_TOOL, self.ClearText, id=wx.ID_CLEAR)
        self.root.GetToolBar().Bind(wx.EVT_TOOL, self.SaveToFile, id=wx.ID_SAVE)

    def SaveToFile(self, e):
        if not os.path.isdir(os.path.dirname(LOG_FILE_PATH)):
            os.makedirs(os.path.dirname(LOG_FILE_PATH))
        wx.CallAfter(self.SaveFile, filename=LOG_FILE_PATH)
        if e:
            e.Skip()

    def ClearText(self, e):
        wx.CallAfter(self.ClearAll)
        if e:
            e.Skip()

    def AppendInfo(self, text):
        text = str(time.strftime("[%y-%m-%d %H:%M:%S INFO] {0}\r\n".format(text)))
        wx.CallAfter(self.AppendText, text=text)
        # self.ScrollLines(1)
        self.ScrollToEnd()

    def AppendWarn(self, text):
        text = str(time.strftime("[%y-%m-%d %H:%M:%S WARN] {0}\r\n".format(text)))
        wx.CallAfter(self.AppendText, text=text)
        # self.ScrollLines(1)
        self.ScrollToEnd()

    def AppendError(self, text):
        text = str(time.strftime("[%y-%m-%d %H:%M:%S ERROR] {0}\r\n".format(text)))
        wx.CallAfter(self.AppendText, text=text)
        # self.ScrollLines(1)
        self.ScrollToEnd()


# TODO: 生成主页更新项树形结构
class GenerateDirTree(CT.CustomTreeCtrl):
    def __init__(self, parent=None):
        self.parent = parent
        self.root = self.parent.root
        self.RightPanel = self.parent.RightPanel
        # self.JsonObj = self.root.JsonObj

        agwStyle = CT.TR_DEFAULT_STYLE + CT.TR_AUTO_CHECK_CHILD + CT.TR_AUTO_CHECK_PARENT + CT.TR_HIDE_ROOT
        super(GenerateDirTree, self).__init__(parent=self.parent, agwStyle=agwStyle)
        self.SetBackgroundColour(wx.WHITE)
        self.addImageList()
        self.itemKeys = sorted(self.JsonObj.keys(), key=lambda key: self.JsonObj[key]['settings']['priority'])
        self.JsonExe = self.SortCheckedItem()
        wx.CallLater(3000, self.CreateTreeCtrl)

        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.BindChecked)
        self.Bind(CT.EVT_TREE_SEL_CHANGED, self.BindChecked)
        self.Bind(CT.EVT_TREE_ITEM_RIGHT_CLICK, self.RightClickEvt)
        # self.Bind(CT.EVT_TREE_BEGIN_DRAG, self.OnDrag, id=self.GetId())
        # self.Bind(CT.EVT_TREE_ITEM_COLLAPSED, self.CollapseAll)

    @property
    def JsonObj(self):
        return self.root.JsonObj

    # 右键菜单
    def RightClickEvt(self, e):
        if self.parent.parent.NowJob and not self.parent.parent.NowJob.isStoped() and self.parent.parent.NowJob.isPaused():
            return e.Skip()
        if self.parent.RightPanel.NowJob and not self.parent.RightPanel.NowJob.isStoped() and self.parent.RightPanel.NowJob.isPaused():
            return e.Skip()
        pos = e.GetPoint()
        self.PopupMenu(self.RightMenu(e), pos)
        e.Skip()

    # 创建右键菜单
    def RightMenu(self, e):
        item = self.GetSelection()
        itemData = item.GetData()
        if not os.path.exists(itemData):
            row = -1
        elif os.path.isfile(itemData):
            row, pid = self.RightPanel.FindRowByValue(list(os.path.split(itemData)), 2)
        else:
            row = -2
        subMenu = wx.Menu()
        subMenu.Append(wx.ID_OPEN, "打开目录(&O)")
        subMenu.Append(wx.ID_ADD, "加入选项(&A)").Enable(not self.IsItemChecked(item))
        subMenu.Append(wx.ID_REMOVE, "移出选项(&R)").Enable(self.IsItemChecked(item))
        subMenu.AppendSeparator()
        subMenu.Append(ID_EXPAND, "展开(&E)").Enable((row == -2 and not self.IsExpanded(item)))
        subMenu.Append(ID_COLLAPASE, "折叠(&C)").Enable((row == -2 and self.IsExpanded(item)))
        subMenu.AppendSeparator()
        subMenu.Append(wx.ID_DELETE, "删除(&D)").Enable(row == -1)
        subMenu.Bind(wx.EVT_MENU, self.PopupMenuEvt)
        e.Skip()
        return subMenu

    # 右键菜单监听事件
    def PopupMenuEvt(self, e):
        item = self.GetSelection()
        itemData = item.GetData()
        eId = e.GetId()
        if eId == wx.ID_OPEN:
            explorer_select_file(itemData)
        elif eId == wx.ID_ADD:
            self.CheckItem(item, True)
            self.AutoCheckChild(item, True)
        elif eId == wx.ID_REMOVE:
            self.CheckItem(item, False)
            self.AutoCheckChild(item, False)
        elif eId == ID_EXPAND:
            self.Expand(item)
        elif eId == ID_COLLAPASE:
            self.Collapse(item)
            self.CollapseAll(item)
        else:
            self.Delete(item)
        e.Skip()

    # Json文件中的过滤项
    def GetFilter(self, jsonObj={}):
        filterList = []
        for key in jsonObj.keys():
            curFilter = jsonObj[key].get('filter', "")
            filterList.extend(curFilter if type(curFilter) is list else [jsonObj[key].get('filter', "")])
        filterList = list(set([exe.lower() for exe in filterList if exe]))
        return filterList

    # 添加按钮图片列表
    def addImageList(self):
        self.IconList = wx.ImageList(16, 16)
        self.IconList.Add(wx.ArtProvider.GetBitmap(wx.ART_HARDDISK, wx.ART_OTHER, size=(16, 16)))
        self.IconList.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, size=(16, 16)))
        self.IconList.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, size=(16, 16)))
        self.IconList.Add(wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_OTHER, size=(16, 16)))
        self.IconList.Add(wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_OTHER, size=(16, 16)))
        self.AssignImageList(self.IconList)

    # 创建树形结构
    def CreateTreeCtrl(self):
        self.rootNode = self.AddRoot(text=u"计算机", data=None, ct_type=0)
        for key in self.itemKeys:
            serverDir = self.JsonObj[key].get("settings", dict()).get("rootdir", None)
            self.ExeList = [exe.lower() for exe in self.JsonObj[key].keys() if exe.lower() != 'settings']
            self.EexFilter = self.GetFilter(self.JsonObj[key])
            if serverDir and os.path.isdir(serverDir):
                dirSplit = os.path.realpath(serverDir).split(os.sep)
                HardDisk = dirSplit[0]
                HardDiskDir = os.path.normpath(HardDisk + os.sep)
                HardDiskText = os.path.normpath(u"本地磁盘 (%s)" % HardDisk)
                HardDiskImage = 0
                HardDiskNode = self.FindItemByPath(self.GetRootItem(), HardDiskDir)
                if not HardDiskNode:
                    HardDiskNode = self.AppendItem(self.rootNode, text=HardDiskText, data=HardDiskDir,
                                                   image=HardDiskImage,
                                                   ct_type=0)
                    self.SetItemTextColour(HardDiskNode, wx.RED)

                self.SelectItem(HardDiskNode)
                HardDiskNode.Check()
                for subdir in dirSplit:
                    curDir = os.path.normpath(os.path.join(self.GetPath(), subdir))
                    if not os.path.isdir(curDir):
                        break
                    subNode = self.FindItemByPath(self.GetRootItem(), curDir)
                    if not subNode:
                        subImage = 1 if os.path.isdir(curDir) else 3 if (
                            os.path.isfile(curDir) and os.path.splitext(subdir)[1].lower() == '.exe') else 2
                        subNode = self.AppendItem(self.GetSelection(), text=subdir, data=curDir, image=subImage,
                                                  ct_type=1)
                    self.SelectItem(subNode)
                    subNode.Check()
                self.AddItems(self.GetSelection(), serverDir)

        if self.GetSelection() is not self.GetRootItem():
            self.Expand(self.GetSelection())
            self.root.SetStatusText(self.GetSelection().GetData(), 0)
        else:
            self.root.SetStatusText(u"路径设置错误", 0)
        self.CollapseAll(self.GetSelection())
        # self.CheckChilds(self.GetRootItem(), True)
        self.EnableTools()

    # 树形结构子项添加
    def AddItems(self, rootNode, rootDir):
        if not os.path.isdir(rootDir):
            return
        rootFileList = sorted(os.listdir(rootDir), key=lambda key: os.path.isdir(os.path.join(rootDir, key)),
                              reverse=True)
        for itemText in rootFileList:
            subDir = os.path.normpath(os.path.join(rootDir, itemText))
            # 图标格式，对应imaglist
            (preName, fixName) = os.path.splitext(itemText)
            subImage = 1 if os.path.isdir(subDir) else 3 if (
                os.path.isfile(subDir) and preName.lower() in self.ExeList and fixName.lower() == '.exe') else 2
            if subImage == 2:
                continue
            if subImage == 1:
                if int(win32file.GetFileAttributesW(subDir)) == 22:
                    continue
                os.chdir(subDir)
                FindExeList = glob.glob('./*/*/*/*.exe') or glob.glob('./*/*/*.exe') or glob.glob(
                        './*/*.exe') or glob.glob('./*.exe')
                FindExeList = [os.path.splitext(os.path.basename(exe))[0].lower() for exe in FindExeList if exe]
                if not set(FindExeList).intersection(set(self.ExeList)):
                    continue
                os.chdir(scriptDir)
            try:
                subNode = self.AppendItem(rootNode, text=itemText.encode('utf-8'), data=subDir, image=subImage,
                                          ct_type=1)
            except:
                continue
            if self.RightPanel.GetNumberRows() > 1:
                row, pid = self.RightPanel.FindRowByValue([os.path.normpath(rootDir), itemText], 2)
                if row != -1:
                    subNode.Check()
                    self.AutoCheckParent(subNode, True)
            else:
                if preName.lower() not in self.EexFilter and rootNode.IsChecked():
                    subNode.Check()
                    self.AutoCheckParent(subNode, True)
            if os.path.isdir(subDir):
                self.AddItems(subNode, subDir)

    # 获得焦点的路径
    def GetPath(self):
        return self.GetSelection().GetData()

    # 获得复选框选择项
    def GetCheckedItems(self, checkList=[], item=None):
        item = item or self.GetRootItem()
        itemData = item.GetData()
        if item.IsChecked():
            if itemData and os.path.splitext(itemData)[1].lower() == '.exe':
                checkList.append(item.GetData())
                # yield item.GetData()
        (child, cookie) = self.GetFirstChild(item)
        while child:
            self.GetCheckedItems(checkList, child)
            (child, cookie) = self.GetNextChild(item, cookie)
        return sorted(checkList, key=lambda key: self.JsonExe[os.path.splitext(os.path.basename(key))[0].lower()])

    # 根据json配置定义顺序，排序复选框选择项
    def SortCheckedItem(self, checkList=[]):
        for item in self.itemKeys:
            for exe in (sorted(self.JsonObj[item], key=lambda key: self.JsonObj[item][key].get('order', 9999))):
                if exe != 'settings':
                    checkList.append(exe)
        return {key.lower(): value for value, key in enumerate(checkList)}

    # 展开指定路径
    def ExpandPath(self, path):
        rootItem = self.GetRootItem()
        self.CollapseAll(rootItem)
        item = self.FindItemByPath(rootItem, path)
        if item and item is not self.GetRootItem():
            self.ExpandUpNode(item)

    # 展开元素的所有父级元素
    def ExpandUpNode(self, item):
        itemParent = self.GetItemParent(item)
        if itemParent and itemParent is not self.GetRootItem():
            self.Expand(itemParent)
            self.ExpandUpNode(itemParent)
        self.Expand(item)
        self.SelectItem(item, True)

    # 收拢元素
    def CollapseAll(self, item=None):
        item = item or self.GetRootItem()
        if (type(item) is wx.lib.agw.customtreectrl.TreeEvent):
            item = item.GetItem()
        if item is not self.GetRootItem():
            item.Collapse()
        (child, cookie) = self.GetFirstChild(item)
        while child:
            child.Collapse()
            self.CollapseAll(child)
            (child, cookie) = self.GetNextChild(item, cookie)

    # 通过路径查找元素
    def FindItemByPath(self, parent=None, path=None):
        if not path:
            return False
        (child, cookie) = self.GetFirstChild(parent)
        while child:
            curPath = os.path.normpath(child.GetData()).lower()
            if curPath == os.path.normpath(path).lower():
                return child
            target = self.FindItemByPath(child, path)
            if target:
                return target
            (child, cookie) = self.GetNextChild(parent, cookie)
        return child

    # 复选框选择事件监听
    def BindChecked(self, e):
        item = e.GetItem()
        self.SelectItem(item, True)
        self.Expand(item)
        self.root.SetStatusText(item.GetData(), 0)
        self.EnableTools()
        wx.CallAfter(self.SelectGrid, e)
        e.Skip()

    # 定位表格
    def SelectGrid(self, e):
        item = e.GetItem()
        itemData = item.GetData()
        findRow, findPid = self.RightPanel.FindRowByValue(list(os.path.split(itemData)), 2)
        if findRow != -1:
            self.RightPanel.SelectRow(int(findRow))
        e.Skip()

    # 根据是否存在选择项，设定工具栏按钮状态
    def EnableTools(self):
        if self.parent.parent.NowJob and not self.parent.parent.NowJob.isStoped():
            return
        if self.parent.RightPanel.NowJob and not self.parent.RightPanel.NowJob.isStoped():
            return
        toolBar = self.root.GetToolBar()
        hasChecked = True if self.GetCheckedItems([], self.GetSelection()) else False

        toolBar.EnableTool(ID_Start, hasChecked)
        toolBar.EnableTool(ID_Pause, False)
        toolBar.EnableTool(ID_Close, hasChecked)

        toolBar.Realize()

    # 元素拖拽事件
    def OnDrag(self, e):
        item = e.GetItem()
        print(item.GetData())
        e.Skip()


# TODO: 进程状态列表
class PidGrid(wx.grid.Grid):
    def __init__(self, parent=None, csvFile="./ProcessList.csv"):
        super(PidGrid, self).__init__(parent=parent)
        self.parent = parent
        self.root = self.parent.root
        self.SetRowLabelSize(24)
        self.NowJob = None
        self.NewChange = False
        os.chdir(scriptDir)
        self.csvFile = os.path.normpath(os.path.abspath(csvFile))
        # wx.CallAfter(self.SetRowValueFromCsv)
        wx.CallLater(1000, self.SetRowValueFromCsv)

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.RightClickEvt)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.RightClickEvt)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.ChangeCellValue)
        self.root.GetToolBar().Bind(wx.EVT_TOOL, self.RefreshTable, id=wx.ID_REFRESH)

    # 右键弹出菜单
    def RightClickEvt(self, e):
        if self.parent.parent.NowJob and not self.parent.parent.NowJob.isStoped() and self.parent.parent.NowJob.isPaused():
            return e.Skip()
        if self.NowJob and not self.NowJob.isStoped() and self.NowJob.isPaused():
            return e.Skip()
        self.SelectRow(e.GetRow())
        if not (e.GetRow() < 0):
            pos = e.GetPosition()
            self.PopupMenu(self.RightMenu(e), pos)
        e.Skip()

    def ChangeCellValue(self, e):
        row = e.GetRow()
        cell = e.GetCol()
        # wx.grid.GridEvent.GetCol()
        rValue = list(self.GetRowValue(row))
        self.root.JsonObj.update({os.path.basename(rValue[0]): {rValue[1]: {"parameters": rValue[2]}}})
        # print(self.root.JsonObj.get(os.path.basename(rValue[0]), ""))
        # print(json.dumps(self.root.JsonObj, indent=2))
        print(cell)

    # 创建右键菜单
    def RightMenu(self, e):
        row = self.GetSelectedRows()[0]
        rValue = list(self.GetRowValue(row))
        enable = True if int(rValue[3]) != -1 else False
        subMenu = wx.Menu()
        subMenu.Append(wx.ID_OPEN, "打开目录(&O)")
        subMenu.AppendSeparator()
        subMenu.Append(ID_Switch, "切换至(&F)").Enable(enable)
        subMenu.Append(ID_Start, "启动(&S)").Enable(not enable)
        subMenu.Append(ID_Close, "关闭(&C)").Enable(enable)
        subMenu.AppendSeparator()
        subMenu.Append(wx.ID_COPY, "复制(&C)")
        subMenu.Append(ID_INSERT, "插入(&I)")
        subMenu.AppendSeparator()
        subMenu.Append(wx.ID_REMOVE, "删除(&D)")

        subMenu.Bind(wx.EVT_MENU, self.PopupMenuEvt)
        e.Skip()
        return subMenu

    # 右键菜单监听事件
    def PopupMenuEvt(self, e):
        eId = e.GetId()
        row = self.GetSelectedRows()[0]
        rValue = list(self.GetRowValue(row))
        if not rValue:
            return e.Skip()
        filePath = os.path.join(rValue[0], rValue[1])
        if eId == wx.ID_OPEN:
            explorer_select_file(filePath)
        elif eId == ID_Switch:
            SystemWindow.SetForegroundByPid(int(rValue[3]))
        elif eId == ID_Start:
            self.ReSetJob()
            self.NowJob = GridThreadTask(row=row, rValue=rValue, parent=self, BindId=eId)
            self.NowJob.start()
        elif eId == ID_Close:
            self.ReSetJob()
            pid = rValue[3]
            if pid != -1:
                self.NowJob = GridThreadTask(row=row, rValue=rValue, parent=self, BindId=eId)
                self.NowJob.start()
        elif eId == wx.ID_COPY:
            self.InsertRows(row + 1, 1, True)
            self.SetRowValue(row + 1, rValue)
            self.SelectRow(row + 1)
            self.NewChange = True
        elif eId == ID_INSERT:
            self.InsertRows(row + 1, 1, True)
            self.SelectRow(row + 1)
            self.NewChange = True
        else:
            self.ReSetJob()
            pid = rValue[3]
            if pid != -1:
                self.NowJob = GridThreadTask(row=row, rValue=rValue, parent=self, BindId=ID_Close, rmRow=True)
                self.NowJob.start()
            self.DeleteRows(row, 1)
            self.NewChange = True
            return e.Skip()
        e.Skip()

    def ReSetJob(self):
        if self.NowJob and self.NowJob.isAlive():
            self.NowJob.stop()
        del self.NowJob
        gc.collect()
        self.NowJob = None

    # 通过单元格值查找行号和pid
    def FindRowByValue(self, RowValueList, colnum=3):
        findRow = -1
        findPid = -1
        for row in range(self.GetNumberRows()):
            rValue = list(self.GetRowValue(row))
            if rValue[0:colnum] == RowValueList[0:colnum]:
                findPid = rValue[3]
                findRow = row
                line = 0 if row < 30 else row
                self.Scroll(0, line)
                # self.ScrollLines(31)
                break
        return findRow, findPid

    # 设置表格指定行的值
    def SetRowValue(self, row, RowValueList, colour=wx.BLACK, select=True):
        self.NewChange = True
        if select:
            self.SelectRow(row, False)
            line = 0 if row < 30 else row
            self.Scroll(0, line)
        self.SetRowSize(row, 18)
        for col in range(self.GetNumberCols()):
            self.SetCellTextColour(row, col, colour)
            cSize = len(str(RowValueList[col])) * 8
            if cSize > self.GetColSize(col):
                self.SetColSize(col, cSize)
            self.SetCellValue(row, col, str(RowValueList[col]))

    # 获取表格指定行的值
    def GetRowValue(self, row):
        for col in range(self.GetNumberCols()):
            yield self.GetCellValue(row=row, col=col).encode('utf-8')

    # 获取表头
    def GetRowHeader(self):
        for col in range(self.GetNumberCols()):
            yield self.GetColLabelValue(col).encode('utf-8')

    # 设置单元格值
    def AddCellValue(self, RowValueList):
        self.NewChange = True
        findRow, findPid = self.FindRowByValue(RowValueList)
        # RowValueList[4] = "正常" if (psutil.pid_exists(int(RowValueList[3])) and int(RowValueList[3]) != 0) else "异常"
        RowValueList[4] = "正常" if IsRightProcess(RowValueList[3], RowValueList[2]) else "异常"
        RowValueList[3] = RowValueList[3] if IsRightProcess(RowValueList[3], RowValueList[2]) else -1
        colour = wx.BLACK if IsRightProcess(RowValueList[3], RowValueList[2]) else wx.RED

        if int(findRow) != -1:
            self.SetRowValue(findRow, RowValueList, colour)
        else:
            self.InsertRows(self.GetNumberRows(), 1, True)
            if len(RowValueList) > self.GetNumberCols():
                self.InsertCols(self.GetNumberRows(), len(RowValueList) - self.GetNumberCols(), True)
            self.SetRowValue(self.GetNumberRows() - 1, RowValueList, colour)
            findRow = self.GetNumberRows() - 1
        return findRow

    def UpdateCellValue(self, row, RowValueList):
        self.NewChange = True
        RowValueList[4] = "正常" if IsRightProcess(RowValueList[3], RowValueList[2]) else "异常"
        RowValueList[3] = RowValueList[3] if IsRightProcess(RowValueList[3], RowValueList[2]) else -1
        colour = wx.BLACK if IsRightProcess(RowValueList[3], RowValueList[2]) else wx.RED

        if int(row) != -1:
            self.SetRowValue(row, RowValueList, colour)
        else:
            self.InsertRows(self.GetNumberRows(), 1, True)
            if len(RowValueList) > self.GetNumberCols():
                self.InsertCols(self.GetNumberRows(), len(RowValueList) - self.GetNumberCols(), True)
            self.SetRowValue(self.GetNumberRows() - 1, RowValueList, colour)

    # csv文件保存
    def SaveToCsv(self):
        if not self.NewChange:
            return
        rows = self.GetNumberRows()
        csvFP = open(os.path.realpath(self.csvFile), 'w')
        csvObj = csv.writer(csvFP)
        csvObj.writerow(list(self.GetRowHeader()))
        for row in range(rows):
            rValue = list(self.GetRowValue(row))
            if IsRightProcess(rValue[3], rValue[2]):
                csvObj.writerow(rValue)
            else:
                self.ReSetRowValue(row, rValue)
                csvObj.writerow(rValue)
        csvFP.close()
        self.NewChange = False

    # 表格刷新
    def RefreshTable(self, e):
        rows = self.GetNumberRows()
        if rows > 1:
            for row in range(rows):
                rValue = list(self.GetRowValue(row))
                if IsRightProcess(rValue[3], rValue[2]):
                    continue
                else:
                    wx.CallAfter(self.ReSetRowValue, row=row, rValue=rValue)
        else:
            self.SetRowValueFromCsv()
        if e:
            e.Skip()

    # 重新设置表格值
    def ReSetRowValue(self, row, rValue):
        self.NewChange = True
        pid = FindProcess(rValue[0], rValue[1], rValue[2])
        rValue[3] = str(pid)
        rValue[4] = "异常" if int(rValue[3]) == -1 else "正常"
        colour = wx.RED if int(rValue[3]) == -1 else wx.BLACK
        self.SetRowValue(row, rValue, colour, False)

    # 从csv初始化表格
    def SetRowValueFromCsv(self):
        self.NewChange = True
        try:
            self.CreateGrid(0, 5)
        except Exception as e:
            print(e)
        if not os.path.isfile(self.csvFile):
            for index, data in enumerate(['目录', '进程名', '参数', 'Pid', '状态']):
                self.SetColLabelValue(index, data)
            return
        with open(self.csvFile, 'rb') as csvFile:
            csvFile.seek(0)
            try:
                dialect = csv.Sniffer().sniff(csvFile.read(1024))
            except Exception as e:
                print(e)
                return
            csvFile.seek(0)
            csvreader = list(csv.reader(csvFile, dialect))
            rows = len(csvreader)
            cols = len(csvreader[0])
            for index, data in enumerate(csvreader[0]):
                self.SetColLabelValue(index, data)
            for row in range(1, rows):
                rValue = csvreader[row]
                if len(rValue) < 4:
                    continue
                if not IsRightProcess(rValue[3], rValue[2]):
                    rValue[3] = FindProcess(rValue[0], rValue[1], rValue[2])
                self.AddCellValue(rValue)


# TODO: 树形结构执行任务
class ThreadTask(threading.Thread):
    def __init__(self, **kwargs):
        super(ThreadTask, self).__init__()
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
        self.setDaemon(True)
        self.kwargs = kwargs

        self.parent = self.kwargs.get('parent', None)
        self.BindId = self.kwargs.get('BindId', None)

        self.root = self.parent.root
        self.menuBar = self.root.GetMenuBar()
        self.toolbar = self.root.GetToolBar()

        self.treectrl = self.parent.PageOne.LeftPanel
        self.gridctrl = self.parent.PageOne.RightPanel
        self.logctrl = self.parent.PageTwo

    def pause(self):
        self.__flag.clear()
        self.root.SetStatusText("暂停", 2)
        self.logctrl.AppendInfo('暂停')
        return gc.collect()

    def restart(self):
        self.__flag.set()
        self.root.SetStatusText("继续", 2)
        self.logctrl.AppendInfo('继续')
        return gc.collect()

    def isPaused(self):
        return self.__flag.isSet()

    def isStoped(self):
        return not self.__running.isSet()

    def stop(self):
        # self.treectrl.Enable(True)
        self.__running.clear()
        self.__flag.set()
        wx.CallAfter(self.gridctrl.SaveToCsv)
        if (self.menuBar.FindItemById(ID_REDIS).IsChecked()) and self.BindId == ID_Close:
            self.parent.SaveRedis()
        if (self.menuBar.FindItemById(ID_MONGO).IsChecked()) and self.BindId == ID_Close:
            self.parent.SaveMongo()
        if (self.menuBar.FindItemById(ID_AFTER).IsChecked()):
            self.after()
        self.root.SetStatusText("线程停止", 2)
        self.logctrl.AppendInfo('线程停止')
        return gc.collect()

    def before(self):
        if os.path.isfile(PRE_PY_SCRIPT) and os.path.splitext(PRE_PY_SCRIPT)[1].lower() == '.py':
            self.root.SetStatusText(PRE_PY_SCRIPT, 0)
            self.root.SetStatusText("正在执行外部脚本...", 1)
            self.logctrl.AppendWarn('正在执行外部脚本,{0}'.format(PRE_PY_SCRIPT))
            ShellCommond("python " + PRE_PY_SCRIPT)
            self.root.SetStatusText("脚本调用结束", 1)
            self.logctrl.AppendInfo('脚本调用结束')

        else:
            self.root.SetStatusText("外部准备脚本不存在", 1)
            self.logctrl.AppendError('外部准备脚本不存在,{0}'.format(PRE_PY_SCRIPT))

    def after(self):
        if os.path.isfile(AFTER_PY_SCRIPT) and os.path.splitext(AFTER_PY_SCRIPT)[1].lower() == '.py':
            self.root.SetStatusText(AFTER_PY_SCRIPT, 0)
            self.root.SetStatusText("正在执行外部脚本...", 1)
            self.logctrl.AppendWarn('正在执行外部脚本,{0}'.format(AFTER_PY_SCRIPT))
            ShellCommond("python " + AFTER_PY_SCRIPT)
            self.root.SetStatusText("脚本调用结束", 1)
            self.logctrl.AppendInfo('脚本调用结束')
        else:
            self.root.SetStatusText("外部恢复脚本不存在", 1)
            self.logctrl.AppendError('外部准备脚本不存在,{0}'.format(AFTER_PY_SCRIPT))

    def run(self):
        # self.treectrl.Enable(False)
        itemList = self.kwargs.get('ProcessList', None)
        if self.menuBar.FindItemById(ID_PREPARE).IsChecked():
            self.before()
        if not itemList:
            wx.CallAfter(self.gridctrl.SaveToCsv)
            return True
        if self.BindId == ID_Close:
            itemList.reverse()
        for index, item in enumerate(itemList):
            rtn = False
            self.__flag.wait()
            if self.isStoped():
                return True
            dirPath = os.path.dirname(item)
            exeName = os.path.basename(item)
            parameters = self.parent.GetParameters(os.path.splitext(exeName)[0])
            if parameters:
                for parameter in parameters:
                    self.__flag.wait()
                    if self.isStoped():
                        return True
                    if self.BindId == ID_Start:
                        rtn = self.openJob(exeName, parameter, dirPath)
                    else:
                        rtn = self.killJob(exeName, parameter, dirPath)
                    if rtn:
                        wait_time(TIME_SLEEP)
            else:
                if self.BindId == ID_Start:
                    rtn = self.openJob(exeName, "", dirPath)
                else:
                    rtn = self.killJob(exeName, "", dirPath)
                if rtn:
                    wait_time(TIME_SLEEP)
        self.stop()
        self.toolbar.ToggleBitmap(self.BindId)
        self.root.SetStatusText("完成", 2)

    def openJob(self, exe, arg, workdir):
        row, pid = self.gridctrl.FindRowByValue([workdir, exe, arg], 3)
        if row != -1:
            self.gridctrl.SelectRow(row)
        fpid = FindProcess(workdir, exe, arg)
        self.logctrl.AppendWarn("准备开启进程'{0} {1}',工作路径为'{1}'".format(exe, arg, workdir))
        # 查看进程是否已开启
        if psutil.pid_exists(int(fpid)):
            if self.menuBar.FindItemById(wx.ID_JUMP_TO).IsChecked():
                BoxID = wx.ID_OK
            else:
                BoxID = self.root.warnBox(
                        "'{0}'似乎已开启，检测到Pid为'{1}', \n确认是否跳过！".format(os.path.join(workdir, exe) + " " + arg, fpid))
                self.logctrl.AppendWarn(
                        "'{0}'似乎已开启，检测到Pid为'{1}', \n确认是否跳过！".format(os.path.join(workdir, exe) + " " + arg, fpid))
            if BoxID == wx.ID_OK:
                self.root.SetStatusText("跳过开启进程{0} {1}".format(exe, arg), 1)
                self.logctrl.AppendWarn("跳过开启进程{0} {1}".format(exe, arg))
                if int(pid) != int(fpid):
                    pid = fpid
                RowValueList = [workdir, exe, arg, pid, "正常"]
                if row != -1:
                    self.gridctrl.ReSetRowValue(row, RowValueList)
                else:
                    self.gridctrl.AddCellValue(RowValueList)
                return False
            else:
                self.logctrl.AppendWarn("继续开启进程{0}".format(exe))
        GetChdir(workdir)
        cmdLine = "start {0} {1}".format(exe, " ".join(arg.split(",")))
        ShellCommond(cmdLine)
        # 以下方式在gui程序被杀进程树的时候会导致开启的程序全部被关闭，慎用
        # win32api.WinExec(cmdLine, win32con.SW_SHOW)
        # win32api.ShellExecute(0, 'open', exe, " ".join(arg.split(",")), workdir, win32con.SW_SHOW)
        # 新产生pid
        newPid = FindProcess(workdir, exe, arg)
        if self.menuBar.FindItemById(ID_TEST).IsChecked():
            pid = newPid
        else:
            try:
                pid = SystemWindow.StartServer(newPid, self.root)
            except Exception as e:
                BoxID = self.root.warnBox("界面'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
                if BoxID == wx.ID_OK:
                    self.root.SetStatusText("界面'{0} {1}'操作异常,pid={2}".format(exe, arg, pid), 1)
                    self.logctrl.AppendError("界面'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
                pid = newPid
            finally:
                SystemDevice.Release()
        RowValueList = [workdir, exe, arg, pid, "正常"]
        # 执行失败
        if not IsRightProcess(pid, arg):
            BoxID = self.root.errorBox("'{0} {1}'开服失败，请排查原因！".format(os.path.join(workdir, exe), arg))
            self.logctrl.AppendError("'{0} {1}'开服失败，请排查原因！".format(os.path.join(workdir, exe), arg))
            if BoxID == wx.ID_OK:
                self.root.SetStatusText("开启进程{0} {1}失败".format(exe, arg), 1)
        else:
            self.root.SetStatusText("成功开启进程'{0} {1}',pid={2}".format(exe, arg, pid), 1)
            self.logctrl.AppendInfo("成功开启进程'{0} {1}',pid={2}".format(exe, arg, pid))
        if row != -1:
            self.gridctrl.ReSetRowValue(row, RowValueList)
        else:
            self.gridctrl.AddCellValue(RowValueList)
        GetChdir(scriptDir)
        return True if IsRightProcess(pid, arg) else False

    def killJob(self, exe, arg, workdir):
        # 查看表格中是否有相关项
        row, pid = self.gridctrl.FindRowByValue([workdir, exe, arg], 3)
        if row != -1:
            self.gridctrl.SelectRow(row)
        # 查找进程中是否有相关项
        if not psutil.pid_exists(int(pid)):
            pid = int(FindProcess(workdir, exe, arg))
        elif not psutil.Process(int(pid)).name().lower() == exe.lower():
            pid = int(FindProcess(workdir, exe, arg))
        elif not IsSameDir(psutil.Process(int(pid)).cwd(), workdir):
            pid = int(FindProcess(workdir, exe, arg))
        elif not psutil.Process(int(pid)).cmdline()[1:] == arg.strip().split():
            pid = int(FindProcess(workdir, exe, arg))
        else:
            pid = int(pid)
        self.logctrl.AppendInfo("准备关闭进程'{0} {1}',工作路径为'{2}',pid={3}".format(exe, arg, workdir, str(pid)))
        # 如果没有进程，则把信息保存到表格和csv文件，并跳过
        if not IsRightProcess(pid, arg):
            RowValueList = [workdir, exe, arg, -1, "异常"]
            if row != -1:
                self.gridctrl.ReSetRowValue(row, RowValueList)
            self.root.SetStatusText("进程'{0} {1}'不存在".format(exe, arg), 1)
            self.logctrl.AppendError("进程'{0} {1}'不存在".format(exe, arg))
            return False
        try:
            # 根据pid杀进程
            if self.menuBar.FindItemById(ID_TEST).IsChecked():
                SystemWindow.TaskKillPid(pid)
            else:
                SystemWindow.CloseWindowByPid(pid)
            self.root.SetStatusText("成功关闭进程'{0} {1}',pid={2}".format(exe, arg, pid), 1)
            self.logctrl.AppendInfo("成功关闭进程'{0} {1}',pid={2}".format(exe, arg, pid))
            pid = -1
        except Exception as e:
            BoxID = self.root.warnBox("关闭进程'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
            if BoxID == wx.ID_OK:
                self.root.SetStatusText("关闭进程'{0} {1}'操作异常,pid={2}".format(exe, arg, pid), 1)
                self.logctrl.AppendError("关闭进程'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
        finally:
            SystemDevice.Release()

        # 保存信息
        RowValueList = [workdir, exe, arg, str(pid), "异常"]
        if row != -1:
            self.gridctrl.ReSetRowValue(row, RowValueList)
        else:
            self.gridctrl.AddCellValue(RowValueList)
        return True


# TODO: 表格右键菜单执行任务
class GridThreadTask(threading.Thread):
    def __init__(self, **kwargs):
        super(GridThreadTask, self).__init__()
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
        self.setDaemon(True)
        self.kwargs = kwargs

        self.parent = self.kwargs.get('parent', None)
        self.root = self.parent.root
        self.menuBar = self.root.GetMenuBar()
        self.logctrl = self.parent.parent.parent.PageTwo

        self.BindId = self.kwargs.get('BindId', None)
        self.row = int(self.kwargs.get('row', None))
        self.rValue = self.kwargs.get('rValue', None)
        self.rmRow = self.kwargs.get('rmRow', False)

    def pause(self):
        self.__flag.clear()

    def restart(self):
        self.__flag.set()

    def isPaused(self):
        return self.__flag.isSet()

    def isStoped(self):
        return not self.__running.isSet()

    def stop(self):
        self.__running.clear()
        self.__flag.set()
        wx.CallAfter(self.parent.SaveToCsv)
        return gc.collect()

    def run(self):
        while self.__running.isSet():
            rtn = False
            self.__flag.wait()
            dirPath = self.rValue[0]
            exeName = self.rValue[1]
            arg = self.rValue[2]
            if self.BindId == ID_Start:
                rtn = self.openJob(exeName, arg, dirPath)
            else:
                rtn = self.killJob(exeName, arg, dirPath)
            if rtn:
                wait_time(TIME_SLEEP)
            self.stop()

    def openJob(self, exe, arg, workdir):
        self.parent.SelectRow(self.row)
        self.logctrl.AppendInfo("准备开启进程'{0} {1}',工作路径为'{2}'".format(exe, arg, workdir))
        pid = FindProcess(self.rValue[0], self.rValue[1], self.rValue[2])
        # 查看进程是否已开启
        if psutil.pid_exists(int(pid)):
            if self.menuBar.FindItemById(wx.ID_JUMP_TO).IsChecked():
                BoxID = wx.ID_OK
            else:
                BoxID = self.parent.root.warnBox(
                        "'{0}'似乎已开启，检测到Pid为'{1}', \n确认是否跳过！".format(os.path.join(workdir, exe) + " " + arg, pid))

                self.logctrl.AppendWarn(
                        "'{0}'似乎已开启，检测到Pid为'{1}', \n确认是否跳过！".format(os.path.join(workdir, exe) + " " + arg, pid))

            if BoxID == wx.ID_OK:
                self.root.SetStatusText("进程'{0} {1}'已开启，跳过".format(exe, arg), 1)
                self.logctrl.AppendWarn("进程'{0} {1}'已开启，跳过".format(exe, arg))
                self.rValue[3] = pid
                self.parent.ReSetRowValue(self.row, self.rValue)
                return False
            else:
                self.logctrl.AppendWarn("继续开启进程{0} {1}".format(exe, arg))
        if type(workdir) is str:
            workdir = workdir.decode('utf-8')
        GetChdir(workdir)
        cmdLine = "start {0} {1}".format(exe, " ".join(arg.split(",")))
        ShellCommond(cmdLine)

        # 新产生pid
        newPid = FindProcess(self.rValue[0], self.rValue[1], self.rValue[2])
        if self.menuBar.FindItemById(ID_TEST).IsChecked():
            pid = newPid
        else:
            try:
                pid = SystemWindow.StartServer(newPid, self.root)
            except Exception as e:
                BoxID = self.root.warnBox("界面'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
                if BoxID == wx.ID_OK:
                    self.root.SetStatusText("界面'{0} {1}'操作异常,pid={2}".format(exe, arg, pid), 1)
                    self.logctrl.AppendError("界面'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
                pid = newPid
            finally:
                SystemDevice.Release()
        # 执行失败
        if not IsRightProcess(pid, arg):
            BoxID = self.root.errorBox("'{0} {1}'开服失败，请排查原因！".format(os.path.join(workdir, exe), arg))
            self.logctrl.AppendError("'{0} {1}'开服失败，请排查原因！".format(os.path.join(workdir, exe), arg))
            if BoxID == wx.ID_OK:
                self.root.SetStatusText("开启进程{0}  {1}失败".format(exe, arg), 1)
                self.rValue[3] = -1
                self.parent.ReSetRowValue(self.row, self.rValue)
                # wx.CallAfter(self.parent.SaveToCsv)
                return -1

        self.root.SetStatusText("成功开启进程'{0} {1}',pid={2}".format(exe, arg, pid), 1)
        self.logctrl.AppendInfo("成功开启进程'{0} {1}',pid={2}".format(exe, arg, pid))
        self.rValue[3] = pid
        self.parent.ReSetRowValue(self.row, self.rValue)
        GetChdir(scriptDir)
        return pid

    def killJob(self, exe, arg, workdir):
        self.parent.SelectRow(self.row)
        # 查看表格中是否有相关项
        pid = self.rValue[3]
        if not psutil.pid_exists(int(pid)):
            pid = int(FindProcess(workdir, exe, arg))
        elif not psutil.Process(int(pid)).name().lower() == exe.lower():
            pid = int(FindProcess(workdir, exe, arg))
        elif not IsSameDir(psutil.Process(int(pid)).cwd(), workdir):
            pid = int(FindProcess(workdir, exe, arg))
        elif not psutil.Process(int(pid)).cmdline()[1:] == arg.strip().split():
            pid = int(FindProcess(workdir, exe, arg))
        else:
            pid = int(pid)
        self.logctrl.AppendInfo("准备关闭进程'{0} {1}',工作路径为'{2}',pid={3}".format(exe, arg, workdir, pid))

        # 如果没有进程，则把信息保存到表格和csv文件，并跳过
        if not IsRightProcess(pid, arg):
            self.root.SetStatusText("进程'{0} {1}'不存在".format(exe, arg), 1)
            self.logctrl.AppendError("进程'{0} {1}'不存在".format(exe, arg))
            self.rValue[3] = -1
            if not self.rmRow:
                self.parent.ReSetRowValue(self.row, self.rValue)
            return False

        try:
            # 根据pid杀进程
            if self.menuBar.FindItemById(ID_TEST).IsChecked():
                SystemWindow.TaskKillPid(pid)
            else:
                SystemWindow.CloseWindowByPid(pid)
            self.root.SetStatusText("成功关闭进程'{0} {1}',pid={2}".format(exe, arg, pid), 1)
            self.logctrl.AppendInfo("成功关闭进程'{0} {1}',pid={2}".format(exe, arg, pid))
            pid = -1
        except Exception as e:
            BoxID = self.root.warnBox("关闭进程'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
            if BoxID == wx.ID_OK:
                self.root.SetStatusText("关闭进程'{0} {1}'操作异常,pid={2}".format(exe, arg, pid), 1)
                self.logctrl.AppendError("关闭进程'{0} {1}'操作异常,pid={2}\n{3}".format(exe, arg, pid, e))
        finally:
            SystemDevice.Release()
        self.rValue[3] = pid
        # 保存信息
        if not self.rmRow:
            self.parent.ReSetRowValue(self.row, self.rValue)
        return True


# TODO: 最小化托盘
class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super(TaskBarIcon, self).__init__()
        self.MainFrame = frame
        self.initID()
        self.initUI()
        self.initBind()

    # 生成组件ID
    def initID(self):
        self.ViewID = wx.NewId()

    # 生成界面
    def initUI(self):
        self.settings()

    # 事件监控
    def initBind(self):
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDclick)
        # 监听菜单栏中的退出选项

    # 基础设置
    def settings(self):
        from wx.lib.embeddedimage import PyEmbeddedImage
        icon = PyEmbeddedImage(B64_POKER128).GetIcon()
        if self.MainFrame.IsShown():
            self.MainFrame.Hide()
        self.SetIcon(icon, u'游戏进程管理器')

    # 生成最小化菜单, 默认右键单击调用PopupMenu方法呼出菜单
    def CreatePopupMenu(self):
        self.TaskBarIconMenu = wx.Menu()
        # self.ExitMenu = wx.Menu()

        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(self.ViewID, u"显示主界面(&M)")
        self.TaskBarIconMenu.Append(ID_OpenDir, u"打开目录(&O)", u"打开目录")
        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(wx.ID_EXIT, u"退出(&X)")

        self.TaskBarIconMenu.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDclick)
        self.TaskBarIconMenu.Bind(wx.EVT_MENU, self.OnDclick, id=self.ViewID)
        self.TaskBarIconMenu.Bind(wx.EVT_MENU, self.OpenWorkDir, id=ID_OpenDir)
        self.TaskBarIconMenu.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        return self.TaskBarIconMenu

    # 单击, 当前没有使用
    def OnClick(self, e):
        self.MainFrame.IsIconized()
        if e:
            e.Skip()

    # 双击展示主面板
    def OnDclick(self, e):
        # Destroy删除元素，无法恢复创建
        self.Destroy()
        self.MainFrame.Restore()
        self.MainFrame.Raise()
        if e:
            e.Skip()

    def OpenWorkDir(self, e):
        toolpath = os.path.splitext(scriptPath)[0] + '.exe'
        toolpath = toolpath if os.path.isfile(toolpath) else scriptPath
        explorer_select_file(toolpath)
        if e:
            e.Skip()

    # 退出
    def OnExit(self, e):
        # 托盘图标销毁
        self.Destroy()
        # 主面板销毁
        # self.MainFrame.Destroy()
        self.MainFrame.OnExit(e)
        if e:
            e.Skip()


# TODO: 主进程
class NewApp(wx.App):
    def OnInit(self):
        window = RootFrame()
        window.Show()
        return True


if __name__ == '__main__':
    # 多进程打包支持
    # pyinstaller -w -F -p "E:\Git\wxPython\common;C:\Python27" -i E:\Git\wxPython\icon\poker.ico ProcessManager.py
    multiprocessing.freeze_support()

    app = NewApp()
    app.MainLoop()
    gc.collect()
    sys.exit(0)
