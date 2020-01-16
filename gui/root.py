#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gc

import wx
import wx.adv
import multiprocessing

from unit import icon
from unit import id as uid
from config import settings
from unit.dialog import DialogBox
from gui.taskbar import TaskBarIcon
from gui.menubar import MenuBar
from gui.statusbar import StatusBar
from gui.toolbar import ToolBar
from gui.workspace import WorkSpaceNB


class RootFrame(wx.Frame):
    def __init__(self, parent=None):
        super(RootFrame, self).__init__(parent=parent, id=uid.ROOT_FRAME, style=wx.DEFAULT_FRAME_STYLE)
        self.__settings__()
        self.__bind__()
        wx.CallAfter(self.__load__)

    # TODO: 初始化主界面
    def __settings__(self):
        # 设置窗口标题
        self.SetTitle(settings.APP_NAME)
        # 设置窗口大小
        self.SetMinSize((880, 640))
        self.SetSize((900, 680))
        # 透明度设置
        self.SetTransparent(230)
        # 设置最小化托盘图标
        self.TaskBarIcon = None
        # 设置窗口样式
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        # 设置窗口图标
        self.SetIcon(icon.LOGO.GetIcon())
        # 窗口居中
        self.Center()
        # 初始化消息对话框
        self.dialog = DialogBox(self)

    # TODO: 事件监听
    def __bind__(self):
        # 监听关闭事件
        self.Bind(event=wx.EVT_CLOSE, handler=self.OnExit)
        # 监听最小化事件
        self.Bind(event=wx.EVT_ICONIZE, handler=self.OnIconfiy)

    # TODO: 子界面加载
    def __load__(self):
        self.SetMenuBar(MenuBar(self))
        self.SetStatusBar(StatusBar(self))
        self.SetToolBar(ToolBar(self))
        wx.CallAfter(WorkSpaceNB, self)

    # TODO: 最小化与还原
    def OnIconfiy(self, e):
        if self.IsIconized():
            if self.IsShown():
                self.Hide()
            self.TaskBarIcon = TaskBarIcon(self)
        else:
            if not self.IsShown():
                self.Show()
                self.Raise()
        return e.Skip()

    # TODO: 退出
    def OnExit(self, e):
        return wx.GetApp().ExitMainLoop()


# TODO: 主进程
class NewApp(wx.App):
    def OnInit(self):
        window = RootFrame()
        window.Show()
        return True


if __name__ == '__main__':
    # 多进程打包支持
    # pyinstaller -w -F -p "E:\Git\wxPython\common;C:\Python27" -i E:\Git\wxPython\icons\poker.ico ProcessManager.py
    multiprocessing.freeze_support()
    app = NewApp()
    app.MainLoop()
    gc.collect()
