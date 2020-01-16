#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import wx
from unit import id as uid
from unit.monitor_db import MonitorDatabase
from gui.process_page import ProcessPageSW
from gui.process_update_page import ProcessUpdatePageSW
from gui.client_upate_page import ClientUpdatePageSW
from gui.toolbar import ToolBar, ToolBarTwo


class WorkSpaceNB(wx.Notebook):
    def __init__(self, parent=None):
        super(WorkSpaceNB, self).__init__(parent=parent, id=uid.WORKSPACE, size=parent.GetMinSize(),
                                          style=wx.NB_TOP | wx.NB_FIXEDWIDTH | wx.NB_FLAT, name=u'工作面板')
        self.parent = parent
        self.__settings__()
        self.__bind__()

    # TODO: 添加子工作区
    def __settings__(self):
        self.AddPage(ProcessPageSW(self), u'进程管理')
        # self.AddPage(ProcessUpdatePageSW(self), u'应用更新')
        # self.AddPage(ClientUpdatePageSW(self), u'客户端更新')

        # 后台运行线程，检查进程情况
        self.deamon = MonitorDatabase()
        wx.CallAfter(self.deamon.start)

    # TODO: 事件监听
    def __bind__(self):
        self.Bind(event=wx.EVT_NOTEBOOK_PAGE_CHANGED, handler=self.TogglePage)

    def UnSwitch(self, e):
        self.Unbind(wx.EVT_NOTEBOOK_PAGE_CHANGED)
        self.SetSelection(e.GetOldSelection())
        self.Bind(event=wx.EVT_NOTEBOOK_PAGE_CHANGED, handler=self.TogglePage)

    def TogglePage(self, e):
        curPage = self.GetCurrentPage()
        curPageId = curPage.GetId()
        oldTB = self.parent.GetToolBar()
        if not oldTB.switch():
            return self.UnSwitch(e)
        if (curPageId == uid.PROCESS_PAGE_SW):
            newTB = ToolBar(self.parent)
        if (curPageId == uid.PROCESS_UPDATE_PAGE_SW):
            newTB = ToolBar(self.parent)
        if (curPageId == uid.CLIENT_UPDATE_PAGE_SW):
            newTB = ToolBarTwo(self.parent)
        self.parent.SetToolBar(newTB)
        oldTB.Destroy()
        newTB.Show()


if __name__ == '__main__':
    pass
