#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx

########## 主界面 ##########
ROOT_FRAME = wx.NewIdRef()

########## 托盘区 ##########
TASKBAR_MENU_M = wx.NewIdRef()
TASKBAR_MENU_O = wx.NewIdRef()
TASKBAR_MENU_X = wx.ID_EXIT

########## 菜单栏 ##########
MENUBAR_MENU_A = wx.ID_ABOUT
MENUBAR_MENU_E = wx.NewIdRef()
MENUBAR_MENU_H = wx.ID_HELP
MENUBAR_MENU_I = wx.NewIdRef()
MENUBAR_MENU_0 = TASKBAR_MENU_O
MENUBAR_MENU_S = wx.ID_FILE
MENUBAR_MENU_X = TASKBAR_MENU_X

MENUBAR_MENU_PRE = wx.NewIdRef()
MENUBAR_MENU_REDIS = wx.NewIdRef()
MENUBAR_MENU_MONGO = wx.NewIdRef()
MENUBAR_MENU_RESET = wx.NewIdRef()
MENUBAR_MENU_DEAMON = wx.NewIdRef()
MENUBAR_MENU_JUMP = wx.NewIdRef()
MENUBAR_MENU_DEBUG = wx.NewIdRef()

MENUBAR_MENU_TB = wx.NewIdRef()
MENUBAR_MENU_SB = wx.NewIdRef()
########## 设置面板 ##########
SET_DIALOG_BTN_PREPARE = wx.NewIdRef()
SET_DIALOG_TEXT_PREPARE = wx.NewIdRef()
SET_DIALOG_BTN_AFTER = wx.NewIdRef()
SET_DIALOG_TEXT_AFTER = wx.NewIdRef()
SET_DIALOG_BTN_REDIS = wx.NewIdRef()
SET_DIALOG_TEXT_REDIS = wx.NewIdRef()
SET_DIALOG_BTN_MONGO = wx.NewIdRef()
SET_DIALOG_TEXT_MONGO = wx.NewIdRef()
SET_DIALOG_TEXT_HOLD = wx.NewIdRef()
SET_DIALOG_TEXT_FREQUENCY = wx.NewIdRef()

########## 状态栏 ##########
STATUSBAR = wx.NewIdRef()

########## 工具栏 ##########
TOOLBAR = wx.NewIdRef()
TOOLBAR_TWO = wx.NewIdRef()
TOOLBAR_START = wx.NewIdRef()
TOOLBAR_STOP = wx.NewIdRef()
TOOLBAR_PAUSE = wx.NewIdRef()
TOOLBAR_CLOSE = wx.NewIdRef()
TOOLBAR_REFRESH = wx.NewIdRef()

TOOLBAR_REDIS = wx.NewIdRef()
TOOLBAR_MONGO = wx.NewIdRef()

########## 工作面板 ##########
WORKSPACE = wx.NewIdRef()
PROCESS_PAGE_SW = wx.NewIdRef()
PROCESS_PAGE_GRID = wx.NewIdRef()
PROCESS_PAGE_TREE = wx.NewIdRef()

PROCESS_UPDATE_PAGE_SW = wx.NewIdRef()
CLIENT_UPDATE_PAGE_SW = wx.NewIdRef()

########## 工作面板-表格 ##########
GRID_POPUPMENU_OPEN = wx.NewIdRef()
GRID_POPUPMENU_SWITCH = wx.NewIdRef()
GRID_POPUPMENU_START = wx.NewIdRef()
GRID_POPUPMENU_CLOSE = wx.NewIdRef()
GRID_POPUPMENU_COPY = wx.NewIdRef()
GRID_POPUPMENU_INSERT = wx.NewIdRef()
GRID_POPUPMENU_ONLINE = wx.NewIdRef()
GRID_POPUPMENU_OFFLINE = wx.NewIdRef()
GRID_POPUPMENU_REFRESH = wx.NewIdRef()

########## 工作面板-树形结构 ##########
TREE_POPUPMENU_OPEN = wx.NewIdRef()
TREE_POPUPMENU_ADD = wx.NewIdRef()
TREE_POPUPMENU_SUB = wx.NewIdRef()
TREE_POPUPMENU_ONLINE = wx.NewIdRef()
TREE_POPUPMENU_OFFLINE = wx.NewIdRef()
TREE_POPUPMENU_DELETE = wx.NewIdRef()
TREE_POPUPMENU_EXPAND = wx.NewIdRef()
TREE_POPUPMENU_COLLAPSE = wx.NewIdRef()
TREE_POPUPMENU_RELOAD = wx.NewIdRef()

if __name__ == '__main__':
    pass
