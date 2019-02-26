#!/usr/bin/env python
# encoding: utf-8

import win32com, win32con
import win32api, win32gui
import win32process


def switch_to_window_by_pid(pid):
    def find_window_by_pid(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, fpid = win32process.GetWindowThreadProcessId(hwnd)
            if int(fpid) == int(pid):
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(find_window_by_pid, hwnds)
    return hwnds


def set_foregroundwindow(hwnd):
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
    if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnds, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)


if __name__ == '__main__':
    hwnds = switch_to_window_by_pid(1372)[0]
    print(win32gui.IsWindowEnabled(hwnds))
    print(win32gui.IsIconic(hwnds))
    win32gui.ShowWindow(hwnds, win32con.SW_RESTORE)
    # print(win32gui.IsIconic(hwnds))
    win32gui.SetForegroundWindow(hwnds)
    win32gui.SetActiveWindow(hwnds)
    set_foregroundwindow(hwnds)
