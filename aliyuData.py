#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: aliyuData.py

@time: 2018/6/22 9:22

@module:python -m pip install wxpython

@desc:
'''
import wx
import wx.adv

# TODO: 主体结构
class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent=parent, id=-1)
        self.SetTitle('阿里云数据')
        # self.Position = (800, 300)
        self.Centre()
        self.SetSize(360, 440)
        # self.SetMinSize(360, 420)
        # self.SetMaxSize((480, 720))
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        self.SetName('topFrame')
        self.SetIcon(wx.Icon('./icon/favicon.ico'))
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)

    # 点击关闭时，隐藏界面，到托盘
    def OnClose(self, event):
        # 此处监听到最小化事件，执行self.OnIconfiy
        self.Iconize(True)

    # 点击最小化时，隐藏界面，到托盘
    def OnIconfiy(self, event):
        self.TaskBarIcon = TaskBarIcon(self)
        self.Hide()

    def Restore(self, event):
        # 消除最小化
        if self.IsIconized():
            self.Iconize(False)
        # 面板展示
        if not self.IsShown():
            self.Show()
        # 至于窗口最上方
        self.Raise()


# TODO: 最小化托盘
class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super(TaskBarIcon, self).__init__()
        self.MainFrame = frame
        self.MainFrame.Hide()
        self.SetIcon(wx.Icon('./icon/favicon.ico', wx.BITMAP_TYPE_ICO), '阿里云数据')

        self.ViewID = wx.NewId()
        self.ExitID = wx.NewId()

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDclick)
        # 监听菜单栏中的退出选项
        self.Bind(wx.EVT_MENU, self.OnDclick, id=self.ViewID)
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.ExitID)

    # 生成最小化菜单, 默认右键单击调用PopupMenu方法呼出菜单
    def CreatePopupMenu(self):
        self.TaskBarIconMenu = wx.Menu()
        self.ViewMenuItem = wx.MenuItem(self.TaskBarIconMenu, self.ViewID, "显示主界面(M)")
        # self.ExitMenuItem = wx.MenuItem(self.TaskBarIconMenu, self.ExitID, "退出(X)")
        # self.ViewMenuItem.SetBitmap(wx.Bitmap('./icon/favicon.ico'))
        self.ExitMenu = wx.Menu()
        self.ExitMenu.Append(self.ExitID, "退出(X)")
        self.TaskBarIconMenu.Append(self.ViewMenuItem)
        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(wx.NewId(), 'quit', self.ExitMenu)

        return self.TaskBarIconMenu

    # 单机, 当前没有使用
    def OnClick(self, event):
        print(self.MainFrame.IsIconized())

    # 双击展示主面板
    def OnDclick(self, event):
        # Destroy删除元素，无法恢复创建
        self.Destroy()
        self.MainFrame.Restore(event)

    # 退出
    def OnExit(self, event):
        # 托盘图标销毁
        self.Destroy()
        # 主面板销毁
        self.MainFrame.Destroy()
        # 退出wx进程
        # wx.Exit()

# TODO: App创建
class NewApp(wx.App):
    def OnInit(self):
        window = MainFrame()
        window.Show()
        # 返回 False则退出
        return True


if __name__ == '__main__':
    app = NewApp()
    app.MainLoop()
