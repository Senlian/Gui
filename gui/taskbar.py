#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import wx
import wx.adv

from unit import icon
from unit import id as uid
from unit import functions as func
from config import settings

# TODO: 最小化托盘
class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, parent):
        self.parent = parent
        super(TaskBarIcon, self).__init__()
        self.__settings__()
        self.__bind__()

    # TODO: 初始化主界面
    def __settings__(self):
        if self.parent.IsShown():
            self.parent.Hide()
        self.SetIcon(icon.LOGO.GetIcon(), settings.APP_NAME)

    # TODO: 事件监控
    def __bind__(self):
        # 图标左键双击事件
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDclick)
        # 菜单 显示主面板
        self.Bind(wx.EVT_MENU, self.OnDclick, id=uid.TASKBAR_MENU_M)
        # 打开工作路径
        self.Bind(wx.EVT_MENU, self.OnOpen, id=uid.TASKBAR_MENU_O)
        # 退出主程序
        self.Bind(wx.EVT_MENU, self.OnExit, id=uid.TASKBAR_MENU_X)

    # TODO: 生成最小化菜单, 默认右键单击调用PopupMenu方法呼出菜单
    def CreatePopupMenu(self):
        self.TaskBarIconMenu = wx.Menu()

        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(uid.TASKBAR_MENU_M, u"显示主界面(&M)")
        self.TaskBarIconMenu.Append(uid.TASKBAR_MENU_O, u"打开目录(&O)", u"打开目录")
        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(uid.TASKBAR_MENU_X, u"退出(&X)")

        return self.TaskBarIconMenu

    # TODO: 单击, 当前没有使用
    def OnClick(self, e):
        self.parent.IsIconized()
        if e:
            e.Skip()

    # TODO: 双击展示主面板
    def OnDclick(self, e):
        # Destroy删除元素，无法恢复创建
        self.Destroy()
        self.parent.Restore()
        self.parent.Raise()
        if e:
            e.Skip()

    # TODO: 打开工作路径
    def OnOpen(self, e):
        func.select(settings.ROOT_DIR)
        if e:
            e.Skip()

    # TODO: 退出主程序
    def OnExit(self, e):
        # 托盘图标销毁
        self.Destroy()
        # 退出主程序
        self.parent.OnExit(e)
        if e:
            e.Skip()


if __name__ == '__main__':
    pass