#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import wx
import pandas as pd
from unit import id as uid
from unit import functions as func
from unit import dialog
from unit.monitor_db import MonitorDatabase
from config import settings
from db.read_sql import ReadSqlDB
from db.to_sql import ToSqliteDB
from db.models import ProcessType, ProcessList


# TODO: 菜单栏
class MenuBar(wx.MenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__()
        self.parent = parent
        self.dialog = dialog.DialogBox(self.parent)
        self.__settings__()
        self.__bind__()

    # TODO: 添加菜单项
    def __settings__(self):
        FileMenu = wx.Menu()
        FileMenu.Append(uid.MENUBAR_MENU_0, u"打开目录(&O)\tCtrl+O", u"打开目录")
        FileMenu.Append(uid.MENUBAR_MENU_S, u"设置(&S)...\tCtrl+S", u"设置")
        FileMenu.Append(uid.MENUBAR_MENU_E, u"导出数据(&E)\tCtrl+E", u"导出数据")
        FileMenu.Append(uid.MENUBAR_MENU_I, u"导入数据(&I)\tCtrl+I", u"导入数据")
        FileMenu.AppendSeparator()
        FileMenu.Append(uid.MENUBAR_MENU_X, u"退出(&Q)...\tCtrl+Q", u"退出")

        OptionMenu = wx.Menu()
        OptionMenu.Append(uid.MENUBAR_MENU_PRE, u"环境准备脚本", u"执行环境准备脚本", kind=wx.ITEM_CHECK)
        OptionMenu.Append(uid.MENUBAR_MENU_REDIS, u"备份Redis脚本", u"执行Redis备份脚本", kind=wx.ITEM_CHECK)
        OptionMenu.Append(uid.MENUBAR_MENU_MONGO, u"备份Mongo脚本", u"执行Mongo备份脚本", kind=wx.ITEM_CHECK)
        OptionMenu.Append(uid.MENUBAR_MENU_RESET, u"环境恢复脚本", u"执行环境恢复脚本", kind=wx.ITEM_CHECK)
        OptionMenu.AppendSeparator()
        OptionMenu.Append(uid.MENUBAR_MENU_DEAMON, u"检查进程状态", u"后台线程自动刷新数据库", kind=wx.ITEM_CHECK).Check(
            settings.FRESH_DB)
        OptionMenu.AppendSeparator()
        OptionMenu.Append(uid.MENUBAR_MENU_JUMP, u"自动跳过", u"自动跳过已启动项", kind=wx.ITEM_CHECK).Check()
        OptionMenu.AppendSeparator()
        OptionMenu.Append(uid.MENUBAR_MENU_DEBUG, u"DEBUG模式", u"不校验界面方式开关进程", kind=wx.ITEM_CHECK)

        ViewMenu = wx.Menu()
        self.Tools = ViewMenu.Append(uid.MENUBAR_MENU_TB, u'工具栏(&T)', u'工具栏', kind=wx.ITEM_CHECK)
        self.Tools.Check(True)
        self.Status = ViewMenu.Append(uid.MENUBAR_MENU_SB, u'状态栏(&S)', u'状态栏', kind=wx.ITEM_CHECK)
        self.Status.Check(True)

        HelpMenu = wx.Menu()
        HelpMenu.Append(uid.MENUBAR_MENU_H, u"说明(&H)", u"工具帮助信息")
        HelpMenu.Append(uid.MENUBAR_MENU_A, u"关于(&A)", u"作者@senlian")

        self.Append(FileMenu, u'文件(&F)')
        self.Append(OptionMenu, u'选项(&O)')
        self.Append(ViewMenu, u'视图(&V)')
        self.Append(HelpMenu, u'帮助(&H)')

    # TODO: 菜单栏监听事件
    def __bind__(self):
        self.Bind(wx.EVT_MENU, self.OnSet, id=uid.MENUBAR_MENU_S)
        self.Bind(wx.EVT_MENU, self.ExportData, id=uid.MENUBAR_MENU_E)
        self.Bind(wx.EVT_MENU, self.ImportData, id=uid.MENUBAR_MENU_I)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=uid.MENUBAR_MENU_0)
        self.Bind(wx.EVT_MENU, self.parent.OnExit, id=uid.MENUBAR_MENU_X)

        self.Bind(wx.EVT_MENU, self.SetDeamonFlag, id=uid.MENUBAR_MENU_DEAMON)

        self.Bind(wx.EVT_MENU, self.ToggleTB, id=uid.MENUBAR_MENU_TB)
        self.Bind(wx.EVT_MENU, self.ToggleSB, id=uid.MENUBAR_MENU_SB)
        self.Bind(wx.EVT_MENU, self.About, id=uid.MENUBAR_MENU_A)

        self.Bind(wx.EVT_MENU, self.OnScript, id=uid.MENUBAR_MENU_PRE)
        self.Bind(wx.EVT_MENU, self.OnScript, id=uid.MENUBAR_MENU_REDIS)
        self.Bind(wx.EVT_MENU, self.OnScript, id=uid.MENUBAR_MENU_MONGO)
        self.Bind(wx.EVT_MENU, self.OnScript, id=uid.MENUBAR_MENU_RESET)

    # TODO: 脚本选项
    def OnScript(self, e):
        eId = e.GetId()
        checked = e.IsChecked()
        if eId == uid.MENUBAR_MENU_PRE:
            settings.DO_PREPARE = checked
        if eId == uid.MENUBAR_MENU_REDIS:
            settings.DO_REDIS = checked
        if eId == uid.MENUBAR_MENU_MONGO:
            settings.DO_MONGO = checked
        if eId == uid.MENUBAR_MENU_RESET:
            settings.DO_AFTER = checked
        if e:
            e.Skip()

    # TODO: 打开工作路径
    def OnOpen(self, e):
        func.select(settings.ROOT_DIR)
        e.Skip()

    # TODO: 设置面板
    def OnSet(self, e):
        setDialog = SetBasicDialog(self.parent, u'设置面板')
        if setDialog.ShowModal() == wx.ID_OK:
            setDialog.SetGlobal()
        if e:
            e.Skip()

    # TODO: 导出数据
    def ExportData(self, e):
        excel = dialog.FileDialog(self, defaultDir='', message='导出数据到文件', defaultFile='',
                                  wildcard=settings.EXCEL_WLIDCARD)
        if not excel:
            return
        try:
            excel_writer = pd.ExcelWriter(excel)
            f = ReadSqlDB(model=ProcessType)
            f.export_type(excel_writer)
            f = ReadSqlDB(model=ProcessList, index_col='id')
            f.export_process(excel_writer)
            excel_writer.close()
            self.dialog.info('导出数据成功!')
        except Exception as error:
            self.dialog.danger('导出数据失败!', caption=u'警告')
        if e:
            e.Skip()

    # TODO: 导入数据
    def ImportData(self, e):
        excel = dialog.FileDialog(self, defaultDir='', message='导入文件中数据',
                                  defaultFile='', wildcard=settings.EXCEL_WLIDCARD)
        if not excel:
            return
        try:
            sql = ToSqliteDB(excel=excel)
            up_type = sql.update_type()
            sql = ToSqliteDB(excel=excel, sheet_name=1)
            up_process = sql.update_process()
            up_args = sql.update_args()
            if up_type or up_process or up_args:
                self.dialog.danger(u'导入数据失败,请检查数据源!', caption=u'警告')
            else:
                if self.dialog.warn(u'导入数据成功, 是否刷新页面?') == wx.ID_OK:
                    grid = self.FindWindowById(uid.PROCESS_PAGE_GRID)
                    tree = self.FindWindowById(uid.PROCESS_PAGE_TREE)
                    try:
                        grid.ReLoad()
                        tree.ReLoadTree()
                    except Exception as error:
                        self.dialog.warn(u'页面刷新失败！')
        except Exception as error:
            self.dialog.danger(u'导入数据失败!', caption=u'警告')
        if e:
            e.Skip()

    # TODO: 自动检测数据库
    def SetDeamonFlag(self, e):
        workspace = self.parent.FindWindowById(uid.WORKSPACE)
        dbthred = workspace.deamon
        if e.IsChecked():
            if dbthred and dbthred.isAlive():
                if dbthred.isPaused and dbthred.locked:
                    dbthred.restart()
                else:
                    dbthred.pause()
            else:
                settings.FRESH_DB = True
                workspace.deamon = MonitorDatabase()
                wx.CallAfter(workspace.deamon.start)
        else:
            settings.FRESH_DB = False
        if e:
            return e.Skip()

    # TODO: 工具栏显隐
    def ToggleTB(self, e):
        TBar = self.parent.GetToolBar()
        if self.Tools.IsChecked():
            TBar.Show()
        else:
            TBar.Hide()
        TBar.Realize()
        if e:
            e.Skip()

    # TODO: 状态栏显隐
    def ToggleSB(self, e):
        SBar = self.parent.GetStatusBar()
        if self.Status.IsChecked():
            SBar.Show()
            self.parent.SetSize((900, 680))
        else:
            SBar.Hide()
            self.parent.SetSize(self.parent.GetMinSize())
        if e:
            e.Skip()

    # TODO: 关于
    def About(self, e):
        self.dialog.msg()
        if e:
            e.Skip()


# TODO: 设置面板
class SetBasicDialog(wx.Dialog):
    def __init__(self, parent=None, title='设置面板'):
        super(SetBasicDialog, self).__init__(parent, title=title, size=(620, 360))
        self.__settings__()
        self.__bind__()

    def __settings__(self):
        vbs = wx.BoxSizer(wx.VERTICAL)
        fgs = wx.FlexGridSizer(6, 3, 20, 5)

        PrePyLabel = wx.StaticText(self, label=u'环境准备脚本')
        PrePyText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_PREPARE, value=settings.PRE_PY_SCRIPT)
        PrePyBTN = wx.Button(self, id=uid.SET_DIALOG_BTN_PREPARE, label="...", size=(40, 25))
        fgs.AddMany(((PrePyLabel), (PrePyText, 1, wx.EXPAND), (PrePyBTN)))

        AfterPyLabel = wx.StaticText(self, label=u'环境恢复脚本')
        AfterPyText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_AFTER, value=settings.AFTER_PY_SCRIPT)
        AfterPyBTN = wx.Button(self, id=uid.SET_DIALOG_BTN_AFTER, label="...", size=(40, 25))
        fgs.AddMany(((AfterPyLabel), (AfterPyText, 1, wx.EXPAND), (AfterPyBTN)))

        RedisPathLabel = wx.StaticText(self, label=u'Redis备份脚本')
        RedisPathText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_REDIS, value=settings.REDIS_PY_SCRIPT)
        RedisPathBTN = wx.Button(self, id=uid.SET_DIALOG_BTN_REDIS, label="...", size=(40, 25))
        fgs.AddMany(((RedisPathLabel), (RedisPathText, 1, wx.EXPAND), (RedisPathBTN)))

        MongoPathLabel = wx.StaticText(self, label=u'Mongo备份脚本')
        MongoPathText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_MONGO, value=settings.MONGO_PY_SCRIPT)
        MongoPathBTN = wx.Button(self, id=uid.SET_DIALOG_BTN_MONGO, label="...", size=(40, 25))
        fgs.AddMany(((MongoPathLabel), (MongoPathText, 1, wx.EXPAND), (MongoPathBTN)))

        TimeSleepLabel = wx.StaticText(self, label=u'任务停顿')
        TimeSleepText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_HOLD, value=str(settings.HOLD))
        TimeSleepUnit = wx.StaticText(self, label=u'秒', size=(40, 25))
        fgs.AddMany(((TimeSleepLabel), (TimeSleepText, 1, wx.EXPAND), (TimeSleepUnit)))

        FrequencyLabel = wx.StaticText(self, label=u'刷新停顿')
        FrequencyText = wx.TextCtrl(self, id=uid.SET_DIALOG_TEXT_FREQUENCY, value=str(settings.FREQUENCY))
        FrequencyUnit = wx.StaticText(self, label=u'秒', size=(40, 25))
        fgs.AddMany(((FrequencyLabel), (FrequencyText, 1, wx.EXPAND), (FrequencyUnit)))
        fgs.AddGrowableCol(1, 1)

        fgs2 = wx.FlexGridSizer(1, 4, 20, 5)
        btn_ok = wx.Button(self, wx.ID_OK, label=u"确认")
        btn_cancel = wx.Button(self, wx.ID_CANCEL, label=u"取消")
        btn_cancel.SetFocus()
        fgs2.AddStretchSpacer()
        fgs2.Add(btn_ok, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        fgs2.Add(btn_cancel, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        fgs2.AddStretchSpacer()

        fgs2.AddGrowableCol(0, 1)
        fgs2.AddGrowableCol(1, 0)
        fgs2.AddGrowableCol(2, 0)
        fgs2.AddGrowableCol(3, 1)

        vbs.Add(fgs, proportion=2, flag=wx.ALL | wx.EXPAND, border=10)
        vbs.Add(fgs2, proportion=2, flag=wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(vbs)

    def __bind__(self):
        self.Bind(wx.EVT_BUTTON, self.SetTextValue, uid.SET_DIALOG_BTN_PREPARE)
        self.Bind(wx.EVT_BUTTON, self.SetTextValue, uid.SET_DIALOG_BTN_AFTER)
        self.Bind(wx.EVT_BUTTON, self.SetTextValue, uid.SET_DIALOG_BTN_REDIS)
        self.Bind(wx.EVT_BUTTON, self.SetTextValue, uid.SET_DIALOG_BTN_MONGO)

    def SetTextValue(self, e):
        eId = e.GetId()
        if eId not in [uid.SET_DIALOG_BTN_PREPARE, uid.SET_DIALOG_BTN_AFTER,
                       uid.SET_DIALOG_BTN_REDIS, uid.SET_DIALOG_BTN_MONGO]:
            return e.Skip()
        wildcard = u"py files (*.py)|*.py|" \
                   "All files (*.*)|*.*"

        if eId == uid.SET_DIALOG_BTN_PREPARE:
            defaultFile = settings.PRE_PY_SCRIPT
            textCtrl = self.FindWindowById(uid.SET_DIALOG_TEXT_PREPARE)
        if eId == uid.SET_DIALOG_BTN_AFTER:
            defaultFile = settings.AFTER_PY_SCRIPT
            textCtrl = self.FindWindowById(uid.SET_DIALOG_TEXT_AFTER)
        if eId == uid.SET_DIALOG_BTN_REDIS:
            defaultFile = settings.REDIS_PY_SCRIPT
            textCtrl = self.FindWindowById(uid.SET_DIALOG_TEXT_REDIS)
        if eId == uid.SET_DIALOG_BTN_MONGO:
            defaultFile = settings.MONGO_PY_SCRIPT
            textCtrl = self.FindWindowById(uid.SET_DIALOG_TEXT_MONGO)
        if not textCtrl:
            return e.Skip()
        newTextValue = dialog.FileDialog(parent=self, message=u"选择文件", defaultFile=defaultFile, wildcard=wildcard)
        textCtrl.SetValue(newTextValue)
        if e:
            e.Skip()

    def SetGlobal(self):
        settings.PRE_PY_SCRIPT = self.FindWindowById(uid.SET_DIALOG_TEXT_PREPARE).GetValue()
        settings.AFTER_PY_SCRIPT = self.FindWindowById(uid.SET_DIALOG_TEXT_AFTER).GetValue()
        settings.REDIS_PY_SCRIPT = self.FindWindowById(uid.SET_DIALOG_TEXT_REDIS).GetValue()
        settings.MONGO_PY_SCRIPT = self.FindWindowById(uid.SET_DIALOG_TEXT_MONGO).GetValue()
        settings.HOLD = int(self.FindWindowById(uid.SET_DIALOG_TEXT_HOLD).GetValue())
        settings.FREQUENCY = int(self.FindWindowById(uid.SET_DIALOG_TEXT_FREQUENCY).GetValue())


if __name__ == '__main__':
    pass
