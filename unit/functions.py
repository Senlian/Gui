#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


########## 进程管理 ##########
def command(cmd):
    try:
        return os.popen(cmd)
    except Exception as e:
        print(e)
        return e


########## 文件管理 ##########
def select(filepath):
    if os.path.isfile(filepath):
        command('explorer.exe /e,/select, "{0}"'.format(filepath))
    elif os.path.isdir(filepath):
        os.startfile(filepath, "explore")
    else:
        return


if __name__ == '__main__':
    pass
