#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: Senlian_Win32.py

@time: 2018/8/27 14:38

@module:python -m pip install 

@desc:
'''
import win32con, win32gui, win32api, win32process
import time, psutil, os, wx
from common.SenLian_Process import WinLock


# 设备锁
SystemDevice = WinLock()


# TODO: 窗口操作
class Window(object):
    # 获取句柄pid
    def GetHwndPid(self, hwnd):
        fpid = -1
        if win32gui.IsWindow(hwnd):
            _, fpid = win32process.GetWindowThreadProcessId(hwnd)
        return fpid

    def GetMsgBox(self, parent):
        hwnd = 0
        while hwnd == parent or hwnd == 0:
            hwnd = win32gui.GetForegroundWindow()
        return hwnd

    # 获取句柄的子窗口句柄
    def GetChlidWindows(self, parent):
        hwnds = []
        if win32gui.IsWindowVisible(parent) and win32gui.IsWindowEnabled(parent):
            try:
                win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd), hwnds)
            except Exception as e:
                print(e)
        return hwnds

    # 通过pid获取窗口句柄
    def FindWindowByPid(self, pid):
        def CallBack(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                fpid = self.GetHwndPid(hwnd)
                if int(fpid) == int(pid):
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(CallBack, hwnds)
        return hwnds

    # 通过标题获取窗口句柄
    def FindWindowByText(self, text):
        def CallBack(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                ftext = win32gui.GetWindowText(hwnd).decode('gb2312').encode('utf-8')
                if str(ftext) == str(text):
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(CallBack, hwnds)
        return hwnds

    # 重复nums次获取窗口句柄，有等待进程退出的作用
    def ReFindWindowByPid(self, pid=-1, nums=3):
        hwnds = []
        t = 0
        while not hwnds:
            if not psutil.pid_exists(int(pid)):
                return hwnds
            hwnds = self.FindWindowByPid(pid)
            t += 1
            # time.sleep(0.1 * t * t)
            time.sleep(0.1 * t)
            if t == nums:
                return hwnds
        return hwnds

    def ReFindWindowByText(self, text, nums=5):
        hwnds = []
        t = 0
        while not hwnds:
            hwnds = self.FindWindowByText(text)
            # time.sleep(0.1 * t * t)
            t += 1
            time.sleep(0.2 * t)
            if t == nums:
                return hwnds
        return hwnds

    # 窗口置顶
    def SetForeground(self, hwnd):
        '''
        # SW_HIDE：隐藏窗口并激活其他窗口。nCmdShow=0。
        # SW_MAXIMIZE：最大化指定的窗口。nCmdShow=3。
        # SW_MINIMIZE：最小化指定的窗口并且激活在Z序中的下一个顶层窗口。nCmdShow=6。
        # SW_RESTORE：激活并显示窗口。如果窗口最小化或最大化，则系统将窗口恢复到原来的尺寸和位置。在恢复最小化窗口时，应用程序应该指定这个标志。nCmdShow=9。
        # SW_SHOW：在窗口原来的位置以原来的尺寸激活和显示窗口。nCmdShow=5。
        # SW_SHOWDEFAULT：依据在STARTUPINFO结构中指定的SW_FLAG标志设定显示状态，STARTUPINFO 结构是由启动应用程序的程序传递给CreateProcess函数的。nCmdShow=10。
        # SW_SHOWMAXIMIZED：激活窗口并将其最大化。nCmdShow=3。
        # SW_SHOWMINIMIZED：激活窗口并将其最小化。nCmdShow=2。
        # SW_SHOWMINNOACTIVE：窗口最小化，激活窗口仍然维持激活状态。nCmdShow=7。
        # SW_SHOWNA：以窗口原来的状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=8。
        # SW_SHOWNOACTIVATE：以窗口最近一次的大小和状态显示窗口。激活窗口仍然维持激活状态。nCmdShow=4。
        # SW_SHOWNORMAL：激活并显示一个窗口。如果窗口被最小化或最大化，系统将其恢复到原来的尺寸和大小。应用程序在第一次显示窗口的时候应该指定此标志。nCmdShow=1。
        '''

        if not win32gui.IsWindow(hwnd):
            return
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)

    # 置顶指定pid的窗口
    def SetForegroundByPid(self, pid):
        hwnds = self.FindWindowByPid(pid)
        for hwnd in hwnds:
            self.SetForeground(hwnd)

    # 开服
    def StartServer(self, pid, wxFrame=None):
        self.LeftDclick()
        SystemDevice.Lock()
        if not psutil.pid_exists(int(pid)):
            return -1
        hwnds = self.ReFindWindowByPid(pid)
        for hwnd in hwnds:
            if not win32gui.IsWindowEnabled(hwnd):
                continue
            self.SetForeground(hwnd)
            subHwnds = self.GetChlidWindows(hwnd)
            for subHwnd in subHwnds:
                if not win32gui.IsWindowVisible(subHwnd):
                    continue
                className = win32gui.GetClassName(subHwnd)
                hwndText = win32gui.GetWindowText(subHwnd).decode('gb2312').encode('utf-8')
                if (className == 'Button') or (className == u'Button'):
                    if hwndText.upper() in ['启动服务', '启动', '开始服务', '开始', u'启动服务', u'启动', u'开始服务', u'开始']:
                        while win32gui.IsWindowEnabled(subHwnd):
                            self.SetForeground(hwnd)
                            self.DclickButton(subHwnd)
                            if wxFrame and win32gui.IsWindowEnabled(subHwnd):
                                BoxID = wxFrame.errorBox("程序启动异常，是否重试?", wx.YES_NO | wx.ICON_ERROR)
                                if BoxID != wx.ID_YES:
                                    break
                            else:
                                break
                        return pid
                else:
                    continue
        SystemDevice.Release()
        return pid

    # 关服
    def CloseWindow(self, hwnd, text):
        while (win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd)):
            pid = self.GetHwndPid(hwnd)
            self.SetForeground(hwnd)
            try:
                # win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                win32gui.SendMessageTimeout(hwnd, win32con.WM_CLOSE, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000)
            except Exception as e:
                print(e)
            if not psutil.pid_exists(int(pid)):
                return True
            newHwnds = self.ReFindWindowByText(text, 5)
            # AI服特殊操作
            if not newHwnds and win32gui.IsWindowVisible(hwnd):
                newHwnds = self.ReFindWindowByText('提示', 5)
            if not newHwnds and win32gui.IsWindowVisible(hwnd):
                newHwnds = self.ReFindWindowByText('错误', 5)
            for newHwnd in newHwnds:
                if not win32gui.IsWindow(newHwnd):
                    continue
                subHwnds = self.GetChlidWindows(newHwnd)
                for subHwnd in subHwnds:
                    if not win32gui.IsWindowVisible(subHwnd):
                        continue
                    className = win32gui.GetClassName(subHwnd)
                    hwndText = win32gui.GetWindowText(subHwnd).decode('gb2312').encode('utf-8')
                    if (className == 'Button') or (className == u'Button'):
                        if (hwndText == '是(&Y)' or hwndText.upper() == 'YES(&Y)'):
                            while win32gui.IsWindowEnabled(subHwnd):
                                self.SetForeground(newHwnd)
                                self.DclickButton(subHwnd)
                                if not psutil.pid_exists(int(pid)):
                                    return True
                            break

    # 关系统弹出
    def CloseErrorBox(self, text):
        # 32770
        hwnds = self.ReFindWindowByText(text, 5)
        for hwnd in hwnds:
            if not win32gui.IsWindowVisible(hwnd):
                continue
            ftext = win32gui.GetWindowText(hwnd).decode('gb2312').encode('utf-8')
            className = win32gui.GetClassName(hwnd).decode('gb2312').encode('utf-8')
            if className == '#32770' and ftext == text:
                pid = self.GetHwndPid(hwnd)
                subHwnds = self.GetChlidWindows(hwnd)
                for subHwnd in subHwnds:
                    if not win32gui.IsWindowVisible(subHwnd):
                        continue
                    subClassName = win32gui.GetClassName(subHwnd)
                    subText = win32gui.GetWindowText(subHwnd).decode('gb2312').encode('utf-8')
                    if subClassName == 'Button':
                        if subText == '关闭程序':
                            while win32gui.IsWindowEnabled(subHwnd):
                                self.SetForeground(hwnd)
                                self.DclickButton(subHwnd)
                                if not psutil.pid_exists(int(pid)):
                                    return True
                            break
                        if subText == '重新启动程序' and win32gui.IsWindow(hwnd):
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                if win32gui.IsWindowEnabled(hwnd):
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    # 关服
    def CloseWindowByPid(self, pid):
        self.LeftDclick()
        SystemDevice.Lock()
        if not psutil.pid_exists(int(pid)):
            return False
        text = os.path.splitext(psutil.Process(int(pid)).name())[0]
        hwnds = self.FindWindowByPid(pid)
        for hwnd in hwnds:
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                self.CloseWindow(hwnd, text)
        # 暂停
        self.CloseErrorBox(text)
        self.ReFindWindowByPid(pid, 5)
        self.TaskKillPid(pid)
        SystemDevice.Release()
        return True

    # 杀进程
    def TaskKillPid(self, pid):
        if psutil.pid_exists(int(pid)):
            try:
                # print("taskkill /PID:{0} /F /T, {1}".format(pid, psutil.Process(int(pid)).name()))
                os.popen("taskkill /PID:{0} /F /T".format(pid)).read().decode('gbk')
            except psutil.NoSuchProcess as e:
                print(e)
        return True

    # 模拟双击
    def DclickButton(self, btn):
        if not win32gui.IsWindowEnabled(btn):
            return
        SystemDevice.Lock()
        self.SetForeground(btn)
        win32gui.SendMessage(btn, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
        win32gui.SendMessage(btn, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 0)
        time.sleep(0.2)
        SystemDevice.Release()

    def LeftDclick(self):
        win32api.SetCursorPos((win32api.GetSystemMetrics(0) * 2 / 3, win32api.GetSystemMetrics(1)))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)


if __name__ == '__main__':
    window = Window()

    SystemDevice.Release()
    # win32gui.EnableMenuItem(win32gui.GetSystemMenu())
    print(window.ReFindWindowByPid(8920))

    # print(window.ReFindWindowByPid(8024))
    # window.SetForeground(4523612L)
    # win32gui.ShowWindow(4523612L, win32con.SW_RESTORE)
    # win32gui.SetForegroundWindow(4523612L)
    # win32gui.ShowWindow(6555182L, win32con.SW_SHOW)
    t = 0



    # print win32gui.SendMessage(6555182L, win32con.WM_CLOSE, 0, 0)
    # print(win32gui.SendMessageTimeout(4523612L, win32con.WM_COMMAND, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000))
    # print(win32gui.IsIconic(6555182L))
    # print(win32gui.IsWindow(6555182L))
    # print(win32gui.IsWindowEnabled(6555182L))
    # print(win32gui.IsWindowVisible(6555182L))
    # # print(window.ReFindWindowByText('提示', 5))
    # print(win32gui.GetWindowText(4851038L).decode('gb2312').encode('utf-8'))
    # for hwnd in (window.GetChlidWindows(5375252L)):
    #     print(win32gui.GetWindowText(hwnd).decode('gb2312').encode('utf-8'))
    # print win32gui.PostMessage(1839576L, win32con.WM_CLOSE, 0, 0)
    # time.sleep(0.2)
    # hwnd = (win32gui.GetForegroundWindow())
    # print(hwnd)
    # hwnd1 = (win32gui.GetActiveWindow())
    # print(hwnd1)
    # print(win32gui.GetWindowText(hwnd).decode('gb2312').encode('utf-8'))
    # print(win32gui.GetWindowText(hwnd1).decode('gb2312').encode('utf-8'))
