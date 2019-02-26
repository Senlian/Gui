#!/usr/bin/env python
# encoding: utf-8

'''
@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: SenLian_Process.py

@time: 2018/8/31 11:18

@module:python -m pip install 

@desc:
'''
import os, subprocess
import psutil
from ctypes import windll


# 切到指定路径并返回系统编码路径
def GetChdir(dirpath):
    # pwd = os.getcwd()
    if not os.path.isdir(dirpath) and not isinstance(dirpath, unicode):
        dirpath = unicode(dirpath, 'utf-8')
    try:
        os.chdir(dirpath)
        return os.getcwd().lower()
        # os.chdir(pwd)
    except:
        return dirpath


# 判断路径是否相同
def IsSameDir(dir1, dir2):
    pwd = os.getcwd()
    dir1 = GetChdir(os.path.normpath(dir1)).lower()
    os.chdir(pwd)
    dir2 = GetChdir(os.path.normpath(dir2)).lower()
    os.chdir(pwd)
    return dir1 == dir2


# 通过进程名查找
def FindProcessByName(exeName):
    # tasklist = os.popen('tasklist /fi "IMAGENAME eq {0}"'.format(exeName)).read().split('\n')[3:-1]
    cmdline = 'tasklist /fi "IMAGENAME eq {0}"'.format(exeName)
    tasklist = ShellCommond(cmdline).read().split('\n')[3:-1]
    for p in tasklist:
        yield p.split()[1]


# 查找指定工作路径的进程
def FindProcessByPath(workdir, exeName):
    pids = FindProcessByName(exeName)
    for pid in pids:
        if not psutil.pid_exists(int(pid)):
            continue
        try:
            cwd = os.path.normpath(psutil.Process(int(pid)).cwd()).lower()
        except Exception as e:
            print(e)
            continue
        if IsSameDir(cwd, workdir):
            yield str(pid)


# 查找指定进程
def FindProcess(workdir, exeName, parameter):
    pids = FindProcessByPath(workdir, exeName)
    for pid in pids:
        try:
            if psutil.Process(int(pid)).cmdline()[1:] == parameter.strip().split():
                return pid
        except:
            continue
    return -1


# 判断是否为查找的进程
def IsRightProcess(pid, parameter):
    try:
        if not psutil.pid_exists(int(pid)):
            return False
        elif psutil.Process(int(pid)).cmdline()[1:] == parameter.strip().split():
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


# 执行命令
def ShellCommond(cmdline):
    try:
        # p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        # p.wait()
        # stdout, stderro = p.communicate()
        # p = os.popen(cmdline)
        return os.popen(cmdline)
    except Exception as e:
        print(e)
        return ''


# 设备锁
class WinLock(object):
    def __init__(self, dll='user32.dll'):
        self.dlltype = windll.LoadLibrary(dll)
        self.Locked = False

    def Lock(self):
        if not self.Locked:
            self.dlltype.BlockInput(True)
        self.Locked = True
        pass

    def Release(self):
        if self.Locked:
            self.dlltype.BlockInput(False)
        self.Locked = False
        pass


if __name__ == '__main__':
    # os.chdir(r'D:\WR-GameServer\ptserver')
    # print ShellCommond('start CorrespondServer.exe')
    # print ShellCommond('tasklist /fi "IMAGENAME eq CorrespondServer.exe')
    pass
