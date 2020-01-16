#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import wx
import time
import psutil
import win32con
import win32gui
import win32api
import win32process

from ctypes import windll
from config import settings


# TODO: 判断两个路径是否相同
def IsSamePath(dir1, dir2):
    if not os.path.isdir(dir1) or not os.path.isdir(dir2):
        return False
    return os.path.normpath(dir1).lower() == os.path.normpath(dir2).lower()


# TODO: 执行命令
def ShellCommond(cmdline):
    try:
        return os.popen(cmdline)
    except Exception as e:
        print(e)
        return ''


# TODO: 通过进程名筛选pid值
def FindPidsByName(exe=None):
    cmdline = 'tasklist /fi "IMAGENAME eq {0}"'.format(exe)
    stdouts = ShellCommond(cmdline).read().split('\n')[3:-1]
    for stdout in stdouts:
        yield stdout.split()[1]


# TODO: 通过路径+进程名筛选pid值
def FindPidsByPath(workdir, exe):
    pids = FindPidsByName(exe)
    for pid in pids:
        try:
            if not psutil.pid_exists(int(pid)):
                continue
            cwd = os.path.normpath(psutil.Process(int(pid)).cwd()).lower()
        except Exception as e:
            continue
        if IsSamePath(cwd, workdir):
            yield str(pid)


# TODO: 通过路径+进程名+参数筛选pid值
def FindPids(workdir, exe, arg):
    pids = FindPidsByPath(workdir, exe)
    arg = [] if not arg else arg.strip().split()
    for pid in pids:
        try:
            if psutil.Process(int(pid)).cmdline()[1:] == arg:
                return pid
        except Exception as e:
            continue
    return None


# TODO: 通过PID查找进程监听端口
def GetPortByPid(pid, retry=5):
    if not IsAlivePid(pid):
        return None
    cmdline = 'netstat -ano -p TCP | findstr  "{0}"'.format(pid)
    stdouts = ShellCommond(cmdline).read().strip()
    if not stdouts:
        if retry == 0:
            time.sleep(1)
            return None
        retry -= 1
        return GetPortByPid(pid, retry)
    retry = 0
    return stdouts.split()[1].split(':')[1]


# TODO: 判断进程是否存在
def IsAlivePid(pid):
    if not pid or not str(pid).isdigit():
        return False
    return psutil.pid_exists(int(pid))


def IsRightProcess(pid, workdir, exe, arg):
    if not IsAlivePid(pid):
        return False
    args = [] if not arg else str(arg).strip().split()
    try:
        process = psutil.Process(int(pid))
        dirname = os.path.normpath(process.cwd()).lower()
        workArgs = process.cmdline()[1:]
        name = process.name().lower()
        if IsSamePath(workdir, dirname) and (name == exe.lower()) and args == workArgs:
            return True
    except Exception as e:
        return False
    return False


# TODO: 开启进程
def ExecuteExe(workdir, exe, arg):
    preDir = os.getcwd()
    arg = " ".join(arg.split()).strip()
    cmdline = "start {0} {1}".format(exe, arg)
    os.chdir(workdir)
    ShellCommond(cmdline)
    os.chdir(preDir)
    time.sleep(settings.HOLD)
    pid = FindPids(workdir, exe, arg)
    port = GetPortByPid(pid, 3)
    retry = 5
    while not pid and retry != 0:
        pid = FindPids(workdir, exe, arg)
        port = GetPortByPid(pid, 3)
        retry -= 1
        time.sleep(0.2 * retry)
    return pid, port


def TaskKillByPid(pid):
    if not IsAlivePid(pid):
        return True
    cmdline = "taskkill /PID:{0} /F /T".format(pid)
    ShellCommond(cmdline)
    return not IsAlivePid(pid)


# TODO: 设备锁
class DeviceLock(object):
    def __init__(self, dll='user32.dll'):
        self.dlltype = windll.LoadLibrary(dll)
        self.Locked = False

    def Lock(self):
        print('lock')
        if not self.Locked:
            self.dlltype.BlockInput(True)
        self.Locked = True
        return self.Locked

    def Release(self):
        print('Release')
        if self.Locked:
            self.dlltype.BlockInput(False)
        self.Locked = False
        return self.Locked


class Window(object):
    def __init__(self, dialog=None, pos=None):
        self.dialog = dialog
        self.device = DeviceLock()
        self.pos = pos if pos else (int(win32api.GetSystemMetrics(0) * 2 / 3), win32api.GetSystemMetrics(1))

    # TODO: 模拟点击按钮
    def DclickButton(self, btn):
        if not win32gui.IsWindowEnabled(btn):
            return
        self.device.Lock()
        self.SetForeground(btn)
        win32gui.SendMessage(btn, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
        win32gui.SendMessage(btn, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 0)
        time.sleep(0.2)
        self.device.Release()

    # TODO: 移动鼠标到指定位置
    def LeftDclick(self):
        win32api.SetCursorPos(self.pos)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    # TODO: 获取句柄的子窗口句柄
    def GetChlidWindows(self, pHwnd):
        hwnds = []
        if win32gui.IsWindowVisible(pHwnd) and win32gui.IsWindowEnabled(pHwnd):
            try:
                win32gui.EnumChildWindows(pHwnd, lambda hwnd, param: param.append(hwnd), hwnds)
            except Exception as e:
                print(e)
        return hwnds

    # TODO: 获取句柄的Pid值
    def GetPidByHwnd(self, hwnd):
        fpid = None
        if win32gui.IsWindow(hwnd):
            _, fpid = win32process.GetWindowThreadProcessId(hwnd)
        return fpid

    # TODO: 通过Pid获取进程窗口句柄
    def FindWindowsByPid(self, pid=None, retry=3, iswait=False):
        def CallBack(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                fpid = self.GetPidByHwnd(hwnd)
                if int(fpid) == int(pid):
                    hwnds.append(hwnd)
            return True

        hwnds = []
        if not IsAlivePid(pid):
            return hwnds

        # 至少重试retry次
        while (not hwnds) and (retry > 0):
            # 遍历窗口，找出符合pid的窗口
            win32gui.EnumWindows(CallBack, hwnds)
            if not hwnds and iswait:
                return hwnds
            time.sleep(0.1 * retry)
            retry -= 1
        return hwnds

    # 通过标题获取窗口句柄
    def FindWindowByText(self, text, retry=3):
        def CallBack(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                ftext = win32gui.GetWindowText(hwnd)
                if str(ftext) == str(text):
                    hwnds.append(hwnd)
            return True

        hwnds = []
        if not text:
            return hwnds
        # 至少重试retry次
        while (not hwnds) and (retry > 0):
            # 遍历窗口，找出符合pid的窗口
            win32gui.EnumWindows(CallBack, hwnds)
            time.sleep(0.1 * retry)
            retry -= 1
        return hwnds

    # TODO: 窗口置顶
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

    # TODO: 置顶指定pid的窗口
    def SetForegroundByPid(self, pid):
        hwnds = self.FindWindowsByPid(pid)
        for hwnd in hwnds:
            self.SetForeground(hwnd)

    # TODO: 检查程序窗口句柄
    def CheckGuiByPid(self, pid):
        if not IsAlivePid(pid):
            return False
        # 固定鼠标
        self.LeftDclick()
        # 锁定键鼠，防误触
        self.device.Lock()
        try:
            hwnds = self.FindWindowsByPid(pid)
            btnTexts = ['启动服务', '启动', '开始服务', '开始', u'启动服务', u'启动', u'开始服务', u'开始']
            # 未捕获窗口句柄
            if not hwnds:
                # 释放键鼠
                self.device.Release()
                if self.dialog and self.dialog.warn("未捕获程序窗口句柄，是否重试?",
                                                    style=wx.YES_NO | wx.ICON_EXCLAMATION) == wx.ID_NO:
                    return False
                return self.CheckGuiByPid(pid)

            for hwnd in hwnds:
                # 窗口是否正常
                if not win32gui.IsWindowEnabled(hwnd):
                    continue
                # 窗口置顶
                self.SetForeground(hwnd)
                # 获取窗口的子部件
                subHwnds = self.GetChlidWindows(hwnd)
                for subHwnd in subHwnds:
                    # 部件可视
                    if not win32gui.IsWindowVisible(subHwnd):
                        continue
                    # 部件类型
                    className = win32gui.GetClassName(subHwnd)
                    # 部件文本信息
                    hwndText = win32gui.GetWindowText(subHwnd)
                    if (className in ['Button', u'Button']):
                        if hwndText.upper() in btnTexts:
                            # 按钮可用
                            while win32gui.IsWindowEnabled(subHwnd):
                                # 窗口置顶
                                self.SetForeground(hwnd)
                                # 点击按钮
                                self.DclickButton(subHwnd)
                                # 如果点击后按钮仍然可点击，则弹窗提醒
                                if self.dialog and win32gui.IsWindowEnabled(subHwnd):
                                    if self.dialog.error("程序按钮点击异常，是否重试?", style=wx.YES_NO | wx.ICON_ERROR) == wx.ID_NO:
                                        break
                                else:
                                    break
            self.device.Release()
            return IsAlivePid(pid)
        except Exception as e:
            print(e)
        self.device.Release()
        return False

    # TODO: 正常关闭
    def CloseWindowByHwnd(self, hwnd, text):
        pid = self.GetPidByHwnd(hwnd)
        if not IsAlivePid(pid):
            return True
        while (win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd)):
            self.SetForeground(hwnd)
            try:
                # win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                # 向进程句柄发出关闭消息
                win32gui.SendMessageTimeout(hwnd, win32con.WM_CLOSE, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000)
            except Exception as e:
                print(e)
            # 根据进程接收消息后的弹出框做出相应操作
            # 以进程名为标题弹出
            if not self.CloseWindowsByText(text, pid):
                # 以'提示'为标题弹出
                if not self.CloseWindowsByText('提示', pid):
                    # 以'错误'为标题弹出
                    self.CloseWindowsByText('错误', pid)
        return not IsAlivePid(pid)

    # TODO: 通过标题关闭
    def CloseWindowsByText(self, text, pid):
        if not IsAlivePid(pid):
            return True
        hwnds = self.FindWindowByText(text, 5)
        for hwnd in hwnds:
            if not win32gui.IsWindow(hwnd):
                continue
            subHwnds = self.GetChlidWindows(hwnd)
            for subHwnd in subHwnds:
                if not win32gui.IsWindowVisible(subHwnd):
                    continue
                className = win32gui.GetClassName(subHwnd)
                hwndText = win32gui.GetWindowText(subHwnd)
                if (className in ['Button', u'Button']):
                    if (hwndText.upper() in ['是(&Y)', 'YES(&Y)']):
                        # 点击按钮，直到进程退出或按钮不可用
                        while win32gui.IsWindowEnabled(subHwnd):
                            self.SetForeground(hwnd)
                            self.DclickButton(subHwnd)
                            if not IsAlivePid(pid):
                                return True
                        # 找到预定按钮，跳出子句柄遍历
                        break
        return not IsAlivePid(pid)

    # TODO: 关系统弹出，#32770
    def CloseErrorBox(self, text):
        hwnds = self.FindWindowByText(text, 5)
        for hwnd in hwnds:
            if not win32gui.IsWindowVisible(hwnd):
                continue
            pid = self.GetPidByHwnd(hwnd)
            className = win32gui.GetClassName(hwnd)
            ftext = win32gui.GetWindowText(hwnd)
            if className == '#32770' and ftext == text:
                subHwnds = self.GetChlidWindows(hwnd)
                for subHwnd in subHwnds:
                    if not win32gui.IsWindowVisible(subHwnd):
                        continue
                    subClassName = win32gui.GetClassName(subHwnd)
                    subText = win32gui.GetWindowText(subHwnd)
                    if (subClassName in ['Button', u'Button']):
                        if subText == '关闭程序':
                            while win32gui.IsWindowEnabled(subHwnd):
                                self.SetForeground(hwnd)
                                self.DclickButton(subHwnd)
                                if not IsAlivePid(pid):
                                    return True
                            break
                        if subText == '重新启动程序' and win32gui.IsWindow(hwnd):
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                if win32gui.IsWindowEnabled(hwnd):
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True

    # TODO: 退出进程
    def CloseWindowByPid(self, pid):
        self.LeftDclick()
        self.device.Lock()
        # 进程不存在，直接退出
        if not IsAlivePid(pid):
            return True
        try:
            process = psutil.Process(int(pid))
            text = os.path.splitext(process.name())[0]
            hwnds = self.FindWindowsByPid(pid)
            for hwnd in hwnds:
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    # 发起关闭命令
                    self.CloseWindowByHwnd(hwnd, text)
            # 关闭系统弹窗
            self.CloseErrorBox(text)
        except Exception as e:
            return not IsAlivePid(pid)
        finally:
            self.device.Release()
        # 此处作用，等待进程退出
        self.FindWindowsByPid(pid, 5, True)
        return not IsAlivePid(pid)


if __name__ == '__main__':
    # pids = FindPids(r'E:\WR-GameServer\ptserver', 'TeamServer.exe', None)
    # port = IsRightProcess(4528, r'E:\WR-GameServer\ptserver', 'TeamServer.exe', 20001)
    # print(port)
    SystemWindow = Window()
    close = SystemWindow.CloseWindowByPid(7552)
    print(close)
