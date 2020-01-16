#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

APP_NAME = '游戏管理器'
APP_VERSION = ''

CUR_DIR = sys.executable if not sys.executable.endswith('python.exe') else os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CUR_DIR)

# 是否监控和刷新DB
FRESH_DB = False

# 是否执行准备脚本
DO_PREPARE = False
# 是否执行环境恢复脚本
DO_AFTER = False
# 是否执行redis脚本
DO_REDIS = False
# 是否执行mongo脚本
DO_MONGO = False

# =====================控制面板设置=====================
# 数据库地址
SQLLITE3 = os.path.join(ROOT_DIR, 'sqlite3.db')

# 刷新频率
FREQUENCY = 1
# 线程任务暂停时长
HOLD = 1

AFTER_PY_SCRIPT = os.path.abspath("./after.py")
PRE_PY_SCRIPT = os.path.abspath("./prepare.py")

MONGO_PY_SCRIPT = os.path.abspath("./mongo_backup.py")
REDIS_PY_SCRIPT = os.path.abspath("./redis_backup.py")

WILDCARD = u"py files (*.py)|*.py|" \
           "bat files (*.bat)|*.bat|" \
           "All files (*.*)|*.*"

EXCEL_WLIDCARD = u"excel files (*.xlsx)|*.xlsx|" \
                 "excel files (*.xls)|*.xls|" \
                 "All files (*.*)|*.*"

if __name__ == '__main__':
    pass
