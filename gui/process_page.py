#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import wx
import wx.grid
import threading
import pandas as pd
from win32 import win32api
from wx.lib.agw import customtreectrl as ct

from config import settings
from unit import icon
from unit import id as uid

from unit import functions as func
from unit import dialog
from unit.do_tasks import DoTask
from unit.monitor_db import ProcessNode
from unit import systemd

from db.models import ProcessType, ProcessList, ProcessArgs, db
from db.read_sql import ReadSqlDB


# TODO: 开关服分页界面
class ProcessPageSW(wx.SplitterWindow):
    def __init__(self, parent=None):
        super(ProcessPageSW, self).__init__(parent=parent, id=uid.PROCESS_PAGE_SW, style=wx.SP_NOBORDER,
                                            size=parent.GetSize())
        self.parent = parent

        self.__settings__()

    # TODO: 添加子界面
    def __settings__(self):
        self.SetMinimumPaneSize(320)
        self.SplitVertically(ProcessTree(self), ProcessGrid(self), 100)


# TODO: 表格结构
class ProcessGrid(wx.grid.Grid):
    def __init__(self, parent=None):
        super(ProcessGrid, self).__init__(parent=parent, id=uid.PROCESS_PAGE_GRID, style=wx.WANTS_CHARS)
        self.root = self.FindWindowById(id=uid.ROOT_FRAME)
        self.dialog = dialog.DialogBox(self.root)
        self.table = None
        self.select = False
        self.__settings__()
        self.__bind__()

    # TODO: 初始化表单
    def __settings__(self):
        self.columns = ['id', 'process_id', 'alias', 'exe', 'parameter', 'pid', 'port', 'status', 'dirpath', 'intro']
        self.header = ['ID', 'eID', '项目', '进程名', '参数', 'Pid', '端口号', '状态', '目录', '备注']
        wx.CallAfter(self.__readsql__)

    # TODO: 表单事件监听
    def __bind__(self):
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)

        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClick)

    # TODO: 读取数据库并展示到表单
    def __readsql__(self, redo=False):
        self.db = ReadSqlDB(ProcessList, index_col='id').get_process()
        if self.db.empty or not set(self.columns).issubset(set(self.db.columns.tolist())):
            return
        self.table = GridTableBase(self.db, self.columns, self.header)
        self.SetRowLabelSize(30)
        self.SetTable(self.table, True)
        # 隐藏参数ID栏和进程ID栏
        self.HideCol(self.table.db.columns.get_loc('id'))
        self.HideCol(self.table.db.columns.get_loc('process_id'))
        # self.HideCol(self.table.db.columns.get_loc('alias'))
        self.HideCol(self.table.db.columns.get_loc('dirpath'))
        if not redo:
            self.AutoSize()
        self.AutoSizeColumns(True)
        # 不可手动编辑
        self.EnableEditing(False)
        # 不可拖动高度
        self.EnableDragRowSize(False)

    # TODO: 获取一行数据
    def GetValueByRow(self, row):
        return self.table.db.iloc[row]

    # TODO: 获取数据所在行
    def GetRowsByValue(self, **kwargs):
        if self.table:
            db = self.table.db
            flag = (db['exe'] != None)
            for key in kwargs:
                flag = flag & (db[key] == kwargs.get(key))
            if not db[flag].empty:
                return db[flag].index
        return pd.Series([])

    # TODO: 选中并跳转到指定行
    def ScrollToRow(self, row):
        self.SelectRow(row)
        self.select = True
        pos_y = 0 if (row < self.GetScrollLineY()) else \
            (row if row < (self.GetNumberRows() / 2) else (2 * row - self.GetNumberRows() / 2))
        self.Scroll(0, pos_y)

    # TODO: 判断进程是否是在线状态
    def isOnRuning(self, rows=[]):
        for row in rows:
            pid = self.table.GetValue(row, self.table.db.columns.get_loc('pid'))
            if pid and int(pid) > 0:
                return True
        return False

    # TODO: 判断是否下架
    def isOnline(self, rows=[]):
        for row in rows:
            status = self.table.db.iloc[row, self.table.db.columns.get_loc('status')]
            if str(status).isdigit() and int(status) > -1:
                return True
        return False

    # TODO: 按行设置表格数据
    def SetRowsValue(self, rows=[], **kwargs):
        for row in rows:
            for key in kwargs:
                col = self.table.db.columns.get_loc(key)
                value = kwargs.get(key)
                self.table.SetValue(row, col, value)
            self.SelectRow(row)
        self.AutoSizeColumns(True)
        self.table.ReSetData()
        return self.table

    # TODO: 表格右键单击事件
    def OnRightClick(self, e):
        curRow = e.GetRow()
        # 与树形结构联动标记
        self.select = True
        # self.ClearSelection()
        self.SelectRow(curRow)
        toolBar = self.root.GetToolBar()
        if not (e.GetRow() < 0):
            if not (toolBar.NowJob and toolBar.NowJob.isAlive()):
                self.PopupMenu(GridRightPopupMenu(self, e), e.GetPosition())
            else:
                if not toolBar.NowJob.isPaused:
                    toolBar.StartThread(uid.TOOLBAR_PAUSE)
                    if self.dialog.warn('触发暂停，是否继续任务？') == wx.ID_OK:
                        toolBar.StartThread(uid.TOOLBAR_PAUSE)
        if e:
            e.Skip()

    # TODO: 表格左键单击事件
    def OnLeftClick(self, e):
        toolBar = self.root.GetToolBar()
        if (toolBar.NowJob and toolBar.NowJob.isAlive()):
            if not toolBar.NowJob.isPaused:
                toolBar.StartThread(uid.TOOLBAR_PAUSE)
                if self.dialog.warn('触发暂停，是否继续任务？') == wx.ID_OK:
                    toolBar.StartThread(uid.TOOLBAR_PAUSE)
                    if e:
                        e.Skip()
                    return
        # 与树形结构联动标记
        self.select = True
        curRow = e.GetRow()
        curRowValue = self.GetValueByRow(curRow)
        tree = self.FindWindowById(id=uid.PROCESS_PAGE_TREE)
        if isinstance(tree, ProcessTree) and not curRowValue.empty:
            treeNodeData = os.path.normpath(os.path.join(curRowValue['dirpath'], curRowValue['exe']))
            treeNode = tree.FindItemByData(treeNodeData)
            if treeNode:
                tree.SelectItem(treeNode)
            else:
                # 节点不存在处理
                tree.UnselectAll()
                self.root.SetStatusText('?', 0)
                self.root.SetStatusText('?', 1)
        self.root.SetStatusText('第 ' + str(curRow) + ' 行', 2)
        if e:
            e.Skip()

    # TODO: 数据库检测
    def FreshDB(self):
        df = ReadSqlDB(ProcessList, index_col='id').get_process()
        for index, series in df.iterrows():
            node = ProcessNode(series)
            node.update()

    # TODO: 刷新数据
    def ReLoad(self):
        if threading.activeCount() < 2:
            t = threading.Thread(target=self.FreshDB)
            t.setDaemon(True)
            t.start()
        self.ClearGrid()
        self.__readsql__(True)


# TODO: 表格右键弹出菜单
class GridRightPopupMenu(wx.Menu):
    def __init__(self, parent=None, e=None):
        super(GridRightPopupMenu, self).__init__()
        self.parent = parent
        self.event = e
        self.__settings__()
        self.__bind__()

    # TODO: 初始化弹出菜单
    def __settings__(self):
        self.curRow = self.parent.GetSelectedRows()[0] if not self.event else self.event.GetRow()
        self.cValues = self.parent.GetValueByRow(self.curRow)
        enable = True if int(self.cValues['pid']) > 0 else False
        self.Append(uid.GRID_POPUPMENU_OPEN, "打开目录(&O)")
        if int(self.cValues['status']) != -1 or int(self.cValues['pid']) > 0:
            self.AppendSeparator()
            self.Append(uid.GRID_POPUPMENU_SWITCH, "转至界面(&P)").Enable(enable)
            self.Append(uid.GRID_POPUPMENU_START, "启动(&S)").Enable(not enable)
            self.Append(uid.GRID_POPUPMENU_CLOSE, "关闭(&C)").Enable(enable)
        self.AppendSeparator()
        self.Append(uid.GRID_POPUPMENU_COPY, "复制(&C)")
        self.Append(uid.GRID_POPUPMENU_INSERT, "插入(&I)")
        self.AppendSeparator()
        if int(self.cValues['status']) != -1:
            newItem = wx.MenuItem(self, uid.GRID_POPUPMENU_OFFLINE, "下架(&D)")
        else:
            newItem = wx.MenuItem(self, uid.GRID_POPUPMENU_ONLINE, "上线(&U)")
        newItem.SetBitmap(icon.GRID_DANGER.GetBitmap())
        newItem.SetTextColour(wx.RED)
        newItem.Enable(threading.activeCount() < 2)
        self.Append(newItem)
        self.Append(uid.GRID_POPUPMENU_REFRESH, "刷新(&F)")
        return self

    # TODO: 弹出菜单事件监听
    def __bind__(self):
        self.Bind(event=wx.EVT_MENU, handler=self.OnOpen, id=uid.GRID_POPUPMENU_OPEN)
        self.Bind(event=wx.EVT_MENU, handler=self.OnSwitch, id=uid.GRID_POPUPMENU_SWITCH)
        self.Bind(event=wx.EVT_MENU, handler=self.OnWork, id=uid.GRID_POPUPMENU_START)
        self.Bind(event=wx.EVT_MENU, handler=self.OnWork, id=uid.GRID_POPUPMENU_CLOSE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnCopy, id=uid.GRID_POPUPMENU_COPY)
        self.Bind(event=wx.EVT_MENU, handler=self.OnInsert, id=uid.GRID_POPUPMENU_INSERT)
        self.Bind(event=wx.EVT_MENU, handler=self.OffLine, id=uid.GRID_POPUPMENU_OFFLINE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnLine, id=uid.GRID_POPUPMENU_ONLINE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnRefresh, id=uid.GRID_POPUPMENU_REFRESH)

    # TODO: 打开文件所在目录
    def OnOpen(self, e):
        func.select(os.path.join(self.cValues['dirpath'], self.cValues['exe']))
        if e:
            e.Skip()

    # TODO: 切换至进程界面
    def OnSwitch(self, e):
        window = systemd.Window()
        window.SetForegroundByPid(self.cValues['pid'])
        if e:
            e.Skip()

    # TODO: 开关服
    def OnWork(self, e):
        self.NowJob = DoTask(taskId=e.GetId())
        self.NowJob.setData([ProcessItem(dir=self.cValues['dirpath'], exe=self.cValues['exe'], row=self.curRow)])
        self.NowJob.start()
        if e:
            e.Skip()

    # TODO: 复制一行
    def OnCopy(self, e):
        print('copy')
        if e:
            e.Skip()

    # TODO: 插入一行
    def OnInsert(self, e):
        print('insert')
        if e:
            e.Skip()

    # TODO: 上线
    def OnLine(self, e):
        STATUS = 0
        self.parent.SetRowsValue([self.curRow], status=STATUS)
        self.EnableTreeNode(True)
        if e:
            e.Skip()

    # TODO: 下架
    def OffLine(self, e):
        if self.parent.isOnRuning([self.curRow]):
            self.parent.dialog.warn('进程尚在运行，下架失败！', style=wx.OK | wx.ICON_EXCLAMATION)
            if e:
                e.Skip()
            return False
        STATUS = -1
        self.parent.SetRowsValue([self.curRow], status=STATUS)
        rows = self.parent.GetRowsByValue(dirpath=self.cValues['dirpath'], exe=self.cValues['exe'])
        self.EnableTreeNode(self.parent.isOnline(rows))
        if e:
            e.Skip()

    # TODO: 与树形结构联动，刷新节点状态
    def EnableTreeNode(self, enable=False):
        tree = wx.FindWindowById(id=uid.PROCESS_PAGE_TREE)
        if isinstance(tree, ProcessTree) and not self.cValues.empty:
            treeNodeData = os.path.normpath(os.path.join(self.cValues['dirpath'], self.cValues['exe']))
            treeNode = tree.FindItemByData(treeNodeData)
            if treeNode:
                treeNode.Check(enable)
                treeNode.Enable(enable)
                tree.AutoCheckParent(treeNode, enable)
                if enable:
                    tree.checkedNodes.update({treeNode: tree.GetNodePriority(treeNode)})
                else:
                    if treeNode in tree.checkedNodes:
                        tree.checkedNodes.pop(treeNode)
                tree.ReLoadItem(treeNode)

    # TODO: 刷新表格
    def OnRefresh(self, e):
        self.parent.ReLoad()
        if e:
            e.Skip()


# TODO: 表格数据
class GridTableBase(wx.grid.GridTableBase):
    def __init__(self, db=None,
                 columns=['id', 'process_id', 'dirpath', 'exe', 'parameter', 'pid', 'port', 'status', 'intro'],
                 header=['ID', 'eID', '目录', '进程名', '参数', 'Pid', '端口号', '状态', '备注']):
        super(GridTableBase, self).__init__()
        self.sql = db
        if not isinstance(self.sql, pd.DataFrame):
            self.sql = ReadSqlDB(ProcessList, index_col='id').get_process()
        self.status_dict = {
            '-1': '下架',
            '0': '关服',
            '1': '开服',
        }
        self.columns = columns
        self.header = header
        self.db = self.sql.loc[:, self.columns]

    # TODO: 设置单元格属性
    def GetAttr(self, row, col, kind):
        attr = wx.grid.GridCellAttr()
        # 开服色
        colour = wx.GREEN
        # 状态：{0: '关服', -1: '下架', 1: '开服'}
        if 'status' in self.db.columns.tolist():
            status = -1 if not str(self.db.iloc[row]['status']).isdigit() else int(self.db.iloc[row]['status'])
            pid = -1 if not str(self.db.iloc[row]['pid']).isdigit() else int(self.db.iloc[row]['pid'])
            # 异常色
            # 关服或者下架状态进程还存在，开服状态进程不存在, 多开，多关, 设置为异常色
            if (status < 1 and pid >= 0) or (status == 1 and pid < 0) or (status < -1 or status > 1):
                colour = wx.RED
            else:
                # 关服色
                if (status == 0):
                    colour = wx.BLACK
                # 下架色
                if (status == -1):
                    colour = wx.LIGHT_GREY
        attr.SetTextColour(colour)
        # 超过单元格长度不覆盖其他单元格
        attr.SetOverflow(False)
        return attr

    # TODO: 设置表头
    def GetColLabelValue(self, col):
        return str(self.header[col])

    # TODO: 设置行头
    def GetRowLabelValue(self, row):
        return str(self.db.index[row])

    # TODO: 设置表格行数
    def GetNumberRows(self):
        return self.db.count()[0]

    # TODO: 设置表格列数
    def GetNumberCols(self):
        return self.db.count(1)[0]

    # TODO: 初始化数据方式
    def GetValue(self, row, col):
        value = self.db.iloc[row, col]
        # 浮点数整数化
        if self.db.columns[col] in ['pid', 'process_id', 'pid', 'port', 'status']:
            value = str(int(value))
        # 进程文件不存在
        if not os.path.exists(os.path.join(self.db.loc[row, 'dirpath'], self.db.loc[row, 'exe'])):
            if self.db.columns[col] in ['pid', 'port', 'status']:
                value = '-1'
        # 进程文件不存在，重新赋值
        if self.db.iloc[row, col] != value:
            self.db.iloc[row, col] = value
        if self.db.columns[col] == 'status':
            status = int(value)
            pid = int(self.db.iloc[row]['pid'])
            if (status < 1 and pid >= 0) or (status == 1 and pid < 0):
                value = '异常'
            value = self.status_dict.get(str(status), '异常')
        return value

    # TODO: 改变值的方法
    @db.atomic()
    def SetValue(self, row, col, value):
        eID = self.db['process_id'].iloc[row]
        arg_id = int(self.db['id'].iloc[row])
        eID = row + 1 if not eID else int(eID)
        if arg_id > 0:
            query = ProcessArgs.update({self.db.columns[col]: value}).where(
                (ProcessArgs.id == arg_id) & (ProcessArgs.process == eID))
        else:
            data = {
                'process': eID,
                self.db.columns[col]: value
            }
            if self.db.columns[col] != 'exe':
                data.update({'exe': self.db['exe'].iloc[row]})
            query = ProcessArgs.insert(data)
        query.execute()

    # TODO: 改变数据库后需要重新加载数据
    def ReSetData(self):
        self.sql = ReadSqlDB(ProcessList, index_col='id').get_process()
        self.db = self.sql.loc[:, self.columns]
        return self.db


# TODO: 生成表格进程对象
class ProcessItem(object):
    def __init__(self, dir, exe, row):
        self.dir = dir
        self.exe = exe
        self.row = row
        self.grid = wx.FindWindowById(id=uid.PROCESS_PAGE_GRID)

    # TODO: 进程路径
    def GetDirPath(self):
        return os.path.normpath(os.path.join(self.dir, self.exe))

    # TODO: 进程工作路径
    def GetDirName(self):
        return os.path.normpath(self.dir)

    # TODO: 进程名
    def GetExe(self):
        return self.exe

    # TODO: 获取进程所在行
    def GetRow(self):
        return int(self.row)

    # TODO: 获取进程pid
    def GetPid(self):
        return int(self.grid.GetValueByRow(self.GetRow())['pid'])

    # TODO: 获取进程端口
    def GetPort(self):
        return int(self.grid.GetValueByRow(self.GetRow())['port'])

    # TODO: 获取进程状态
    def GetStatus(self):
        print(self.GetRow())
        return int(self.grid.GetValueByRow(self.GetRow())['status'])

    # TODO: 获取进程参数
    def GetArg(self):
        return str(self.grid.GetValueByRow(self.GetRow())['parameter'])

    # TODO: 获取自定义进程名称
    def GetName(self):
        return str(self.grid.GetValueByRow(self.GetRow())['alias'])

    # TODO: 更改表格名称
    def SetGridValue(self, **kwargs):
        self.grid.ScrollToRow(self.GetRow())
        return self.grid.SetRowsValue([self.GetRow()], **kwargs)


# TODO: 树形结构
class ProcessTree(ct.CustomTreeCtrl):
    def __init__(self, parent=None):
        agwStyle = ct.TR_DEFAULT_STYLE + ct.TR_AUTO_CHECK_CHILD + ct.TR_AUTO_CHECK_PARENT + ct.TR_HIDE_ROOT
        super(ProcessTree, self).__init__(parent=parent, id=uid.PROCESS_PAGE_TREE, agwStyle=agwStyle)
        self.parent = parent
        self.root = self.FindWindowById(id=uid.ROOT_FRAME)
        self.dialog = dialog.DialogBox(self.root)
        self.items = ReadSqlDB(ProcessType).get_types()
        self.exes = ReadSqlDB(ProcessList, index_col='id').get_process()
        # 用于保存树形结构的节点
        self.treeNodes = {}
        self.checkedNodes = {}
        self.__settings__()
        self.__bind__()

    # TODO: 初始化树形结构
    def __settings__(self):
        self.SetBackgroundColour(wx.WHITE)
        # 注册图标
        self.AssignImageList(ImageList(16, 16))
        self.rootNode = self.GetRootItem()
        if not self.rootNode:
            self.rootNode = self.AddRoot(text=u"计算机", data=None, ct_type=0)
        for index in self.items.index:
            item = self.items.loc[index]
            itemDir = os.path.normpath(item['dirpath'])
            wx.CallAfter(self.AddFolder, itemDir)
            wx.CallLater(50, self.AddFolderFiles, itemDir)

    # TODO: 树形结构事件监听
    def __bind__(self):
        self.Bind(ct.EVT_TREE_ITEM_CHECKED, self.OnSelect)
        self.Bind(ct.EVT_TREE_SEL_CHANGED, self.OnSelect)
        self.Bind(ct.EVT_TREE_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.Bind(ct.EVT_TREE_DELETE_ITEM, self.OnDelete)

    # TODO: 获取选择项路径
    def GetSelectPath(self):
        return str(self.GetSelection().GetData())

    # TODO: 获取满足路径的节点
    def FindItemByData(self, data):
        return self.treeNodes.get(data, None)

    # TODO: 添加文件夹节点
    def AddFolder(self, itemDir):
        dirSplit = os.path.realpath(itemDir).split(os.sep)
        for index, subDir in enumerate(dirSplit):
            preDir = os.sep.join(dirSplit[0:index])
            if preDir.endswith(':'):
                preDir += os.sep
            preNode = self.GetRootItem() if not preDir else self.FindItemByData(preDir)
            newNodeText = subDir if preDir else os.path.normpath(u"本地磁盘 (%s)" % subDir)
            newNodeData = os.path.normpath(os.path.join(preDir, subDir)) if preDir else os.path.normpath(
                subDir + os.sep)
            newNodeImage = 0 if not preDir else (1 if os.path.isdir(newNodeData) else 4)
            newNodeType = 1 if preDir else 0
            newNode = self.FindItemByData(newNodeData)
            if not newNode:
                newNode = self.AppendItem(preNode, text=newNodeText, data=newNodeData,
                                          image=newNodeImage, ct_type=newNodeType)
            self.treeNodes.update({newNodeData: newNode})
            if newNodeImage == 4:
                newNode.Enable(False)
                return newNode
            self.Expand(newNode)
        return newNode

    # TODO: 添加文件节点
    def AddFolderFiles(self, folder=None):
        if os.path.isfile(folder):
            subItems = [os.path.basename(folder)]
            folder = os.path.dirname(folder)
        else:
            if not os.path.isdir(folder):
                return self.AddFolder(folder)
            subItems = sorted(os.listdir(folder), key=lambda key: os.path.isdir(os.path.join(folder, key)),
                              reverse=True)
        for newNodeText in subItems:
            newNodeData = os.path.join(folder, newNodeText)
            # 文件夹添加
            if os.path.isdir(newNodeData):
                self.AddFolderFiles(newNodeData)
            else:
                # 隐藏文件自动跳过
                if int(win32api.GetFileAttributes(newNodeData)) == 22:
                    continue
                # 仅添加exe文件
                newNodeImage = 3 if newNodeText.endswith('.exe') else 2
                if newNodeImage == 3:
                    folderNode = self.FindItemByData(folder)
                    if not folderNode:
                        folderNode = self.AddFolder(folder)
                    newNode = self.FindItemByData(newNodeData)
                    if not newNode:
                        newNode = self.AppendItem(folderNode, text=newNodeText, data=newNodeData,
                                                  image=newNodeImage, ct_type=1)
                    self.treeNodes.update({newNodeData: newNode})

                    if not self.exes[(self.exes['exe'] == newNodeText) & \
                                     (self.exes['dirpath'] == folder) & \
                                     (self.exes.applymap(str)['status'] != '-1')].empty:
                        newNode.Check(True)
                        self.AutoCheckParent(newNode, True)
                        # 记录勾选项
                        self.checkedNodes.update({newNode: self.GetNodePriority(newNode)})
                    else:
                        newNode.Enable(False)

    # TODO: 删除节点时清除节点状态记录
    def OnDelete(self, e):
        if e:
            item = e.GetItem()
            if (item in self.checkedNodes):
                self.checkedNodes.pop(item)
            if (item.GetData() in self.treeNodes):
                self.treeNodes.pop(item.GetData())
            e.Skip()

    # TODO: 重载树形结构
    def ReLoadTree(self):
        self.items = ReadSqlDB(ProcessType).get_types()
        self.exes = ReadSqlDB(ProcessList, index_col='id').get_process()
        self.treeNodes = {}
        self.checkedNodes = {}
        self.DeleteAllItems()
        self.Refresh()
        self.__settings__()

    # TODO: 重载节点
    def ReLoadItem(self, item=None):
        item = item if isinstance(item, wx.lib.agw.customtreectrl.GenericTreeItem) else self.GetSelection()
        if not item:
            return
        self.items = ReadSqlDB(ProcessType).get_types()
        self.exes = ReadSqlDB(ProcessList, index_col='id').get_process()
        folder = item.GetData()
        self.DeleteChildren(item)
        # 清除勾选状态
        if item.IsChecked:
            item.Check(False)
        if item in self.checkedNodes:
            self.checkedNodes.pop(item)
        wx.CallAfter(self.AddFolderFiles, folder)
        self.Refresh()

    # TODO: 折叠节点及其子节点
    def CollapseAllChildren(self, item=None):
        if not item:
            return
        if isinstance(item, wx.lib.agw.customtreectrl.TreeEvent):
            item = item.GetItem()
        if item is not self.GetRootItem():
            item.Collapse()
        (child, cookie) = self.GetFirstChild(item)
        while child:
            child.Collapse()
            self.CollapseAllChildren(child)
            (child, cookie) = self.GetNextChild(item, cookie)

    # TODO: 重定义自动勾选子节点方法
    def AutoCheckChild(self, item, checked):
        if checked and item.GetData().lower().endswith('.exe') and item.IsEnabled():
            # 记录勾选项
            self.checkedNodes.update({item: self.GetNodePriority(item)})
        else:
            if item in self.checkedNodes:
                # 删除勾选项
                self.checkedNodes.pop(item)
        super(ProcessTree, self).AutoCheckChild(item, checked)
        self.CheckItem2(item, bool(self.GetAllCheckedChilds([], item)), torefresh=True)

    # TODO: 重定义自动勾选父节点方法
    def AutoCheckParent(self, item, checked):
        parent = item.GetParent()
        if not parent or parent.GetType() != 1:
            return
        # 有勾选，父节点一定勾选，全部无勾选，父节点取消勾选
        if not checked:
            (child, cookie) = self.GetFirstChild(parent)
            while child:
                if child.GetType() == 1 and child.IsEnabled():
                    if child.IsChecked():
                        checked = True
                (child, cookie) = self.GetNextChild(parent, cookie)
        self.CheckItem2(parent, checked, torefresh=True)
        self.AutoCheckParent(parent, checked)

    # TODO: 获取节点的数据库平台类型
    def GetNodeType(self, node):
        condition = self.items['dirpath'].apply(lambda x: x in node.GetData())
        types = self.items[condition]['type_id']
        if not types.empty:
            return int(types.values[0])

    # TODO: 获取开关服优先级
    def GetNodePriority(self, node):
        nodeData = node.GetData()
        nodeText = node.GetText()
        condition = self.items['dirpath'].apply(lambda x: x in nodeData)
        level = self.items[condition]['level']
        priority = self.exes[(self.exes['exe'] == nodeText) & \
                             (self.exes['dirpath'] == os.path.dirname(nodeData))]['priority']
        if level.empty or priority.empty:
            return 9999 * 10000
        return int(level.values[0]) * 10000 + int(priority.values[0])

    # TODO: 设置工具栏状态
    def SetToolBar(self, item=None):
        if not item:
            return False
        toolBar = self.root.GetToolBar()
        if (toolBar.NowJob and toolBar.NowJob.isAlive()):
            if not toolBar.NowJob.isPaused:
                toolBar.StartThread(uid.TOOLBAR_PAUSE)
                if self.dialog.warn('触发暂停，是否继续任务？') == wx.ID_OK:
                    toolBar.StartThread(uid.TOOLBAR_PAUSE)
            return True
        hasChecked = True if self.GetAllCheckedChilds([], item) else False
        toolBar.EnableTool(uid.TOOLBAR_START, hasChecked)
        toolBar.EnableTool(uid.TOOLBAR_PAUSE, False)
        toolBar.EnableTool(uid.TOOLBAR_CLOSE, hasChecked)
        toolBar.Realize()

    # TODO: 节点选中事件监听
    def OnSelect(self, e):
        item = e.GetItem()
        if (item == self.GetRootItem()):
            if e:
                e.Skip()
            return False
        self.SelectItem(item, True)
        self.Expand(item)
        if item.IsChecked():
            # 勾选父节点
            self.CheckItem2(item.GetParent(), True, torefresh=True)
        self.root.SetStatusText(item.GetData(), 0)
        self.root.SetStatusText(item.GetText(), 1)

        # 必须在监听时候再获取，因为表格对象有可能未初始化完成
        grid = self.FindWindowById(id=uid.PROCESS_PAGE_GRID)
        if isinstance(grid, ProcessGrid):
            grid_rows = grid.GetRowsByValue(dirpath=os.path.dirname(item.GetData()), exe=item.GetText())
            if isinstance(grid_rows, pd.core.indexes.numeric.Int64Index):
                # 表格选择
                grid.ScrollToRow(grid_rows[0])
                if not grid.select:
                    grid.ClearSelection()
                for row in grid_rows:
                    grid.SelectRow(row, grid_rows.size > 1)
                self.root.SetStatusText('第 ' + str(grid_rows[0]) + ' 行', 2)
            else:
                grid.ClearSelection()
                self.root.SetStatusText('?', 2)
            # 树形结构多选
            grid.select = False
            self.SetToolBar(item)
        if e:
            e.Skip()

    # TODO: 右键事件监听
    def OnRightClick(self, e):
        toolBar = self.root.GetToolBar()
        if not (toolBar.NowJob and toolBar.NowJob.isAlive()):
            self.PopupMenu(TreeRightPopupMenu(self, e))
        if e:
            e.Skip()

    # TODO: 获取选择项下边的子勾选项
    def GetAllCheckedChilds(self, checkList=[], item=None, reverse=False):
        if (not item) or (not item.GetData()):
            return checkList
        if os.path.isfile(item.GetData()):
            if item.IsChecked():
                checkList.append(item)
        for child in item.GetChildren():
            self.GetAllCheckedChilds(checkList, child)
        # 按照优先级排序,默认升序
        return [node for node in sorted(checkList, key=lambda key: self.checkedNodes[key], reverse=reverse)]

    def GetAllCheckedGridItems(self, item=None, reverse=False):
        nodes = self.GetAllCheckedChilds([], item=item, reverse=reverse)
        grid = wx.FindWindowById(id=uid.PROCESS_PAGE_GRID)
        for node in nodes:
            nodeData = os.path.dirname(node.GetData())
            nodeText = node.GetText()
            rows = grid.GetRowsByValue(dirpath=nodeData, exe=nodeText).to_list()
            if reverse:
                rows.reverse()
            for row in rows:
                yield ProcessItem(nodeData, nodeText, row)


# TODO: 树形结构右键弹出菜单
class TreeRightPopupMenu(wx.Menu):
    def __init__(self, parent=None, e=None):
        super(TreeRightPopupMenu, self).__init__()
        self.parent = parent
        self.event = e
        self.item = e.GetItem()
        self.__settings__()
        self.__bind__()

    # TODO: 初始化弹出菜单
    def __settings__(self):
        if os.path.exists(self.item.GetData()):
            self.Append(uid.TREE_POPUPMENU_OPEN, "打开目录(&O)")
            self.Append(uid.TREE_POPUPMENU_ADD, "加入选项(&A)").Enable(self.item.IsEnabled() and not self.item.IsChecked())
            self.Append(uid.TREE_POPUPMENU_SUB, "移出选项(&R)").Enable(self.item.IsEnabled() and self.item.IsChecked())
            self.AppendSeparator()
        if os.path.isdir(self.item.GetData()):
            self.Append(uid.TREE_POPUPMENU_EXPAND, "展开(&E)").Enable(not self.item.IsExpanded())
            self.Append(uid.TREE_POPUPMENU_COLLAPSE, "折叠(&C)").Enable(self.item.IsExpanded())
            self.AppendSeparator()
        if os.path.isfile(self.item.GetData()):
            if self.item.IsEnabled():
                newItem = wx.MenuItem(self, uid.TREE_POPUPMENU_OFFLINE, "下架(&D)")
            else:
                newItem = wx.MenuItem(self, uid.TREE_POPUPMENU_ONLINE, "上线(&U)")
            newItem.SetBitmap(icon.GRID_DANGER.GetBitmap())
            newItem.SetTextColour(wx.RED)
            newItem.Enable(threading.activeCount() < 2)
            self.Append(newItem)
        self.Append(uid.TREE_POPUPMENU_DELETE, "删除(&X)").Enable(not self.item.IsEnabled())
        self.Append(uid.TREE_POPUPMENU_RELOAD, "重载(&L)")
        return self

    # TODO: 弹出菜单事件监听
    def __bind__(self):
        self.Bind(event=wx.EVT_MENU, handler=self.OnOpen, id=uid.TREE_POPUPMENU_OPEN)
        self.Bind(event=wx.EVT_MENU, handler=self.OnChecked, id=uid.TREE_POPUPMENU_ADD)
        self.Bind(event=wx.EVT_MENU, handler=self.OnChecked, id=uid.TREE_POPUPMENU_SUB)
        self.Bind(event=wx.EVT_MENU, handler=self.OnExpand, id=uid.TREE_POPUPMENU_EXPAND)
        self.Bind(event=wx.EVT_MENU, handler=self.OnExpand, id=uid.TREE_POPUPMENU_COLLAPSE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnLine, id=uid.TREE_POPUPMENU_ONLINE)
        self.Bind(event=wx.EVT_MENU, handler=self.OffLine, id=uid.TREE_POPUPMENU_OFFLINE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnDelete, id=uid.TREE_POPUPMENU_DELETE)
        self.Bind(event=wx.EVT_MENU, handler=self.OnReload, id=uid.TREE_POPUPMENU_RELOAD)

    # TODO: 打开节点关联目录或文件
    def OnOpen(self, e):
        func.select(self.item.GetData())
        if e:
            e.Skip()

    # TODO: 通过右键菜单勾选/取消勾选节点
    def OnChecked(self, e):
        self.parent.AutoCheckChild(self.item, not self.item.IsChecked())
        self.parent.Refresh()
        if e:
            e.Skip()

    # TODO: 通过右键菜单展开/收拢节点
    def OnExpand(self, e):
        if self.item.IsExpanded():
            self.parent.CollapseAllChildren(self.item)
        else:
            self.item.Expand()
        self.parent.Refresh()
        if e:
            e.Skip()

    # TODO: 删除树节点
    def OnDelete(self, e):
        if (self.parent.dialog.warn('再检查哈!') == wx.ID_OK):
            self.parent.treeNodes.pop(self.item.GetData())
            self.parent.Delete(self.item)
        self.parent.Refresh()
        if e:
            e.Skip()

    # TODO: 重载节点
    def OnReload(self, e):
        if (self.parent.dialog.warn('确定要重新加载目录？') == wx.ID_OK):
            if (self.parent.items['dirpath'].apply(lambda x: x in self.item.GetData()).any()):
                wx.CallAfter(self.parent.ReLoadItem, self.item)
            else:
                wx.CallAfter(self.parent.ReLoadTree)
        if e:
            e.Skip()

    # TODO: 上线进程，多参数进程全体上线
    def OnLine(self, e):
        '''
        上线游戏，判断数据库是否存在，存在则更新，不存在则创建
        '''
        nodeType = self.parent.GetNodeType(self.item)
        nodeText = self.item.GetText()
        nodeData = os.path.dirname(self.item.GetData())
        STATUS = 0
        process = ProcessList.get_or_none(
            ProcessList.type == nodeType,
            ProcessList.exe == nodeText,
            ProcessList.dirpath == nodeData
        )
        grid = wx.FindWindowById(id=uid.PROCESS_PAGE_GRID)
        if process:
            if (self.parent.dialog.danger('哥们，确认要把进程上线吗？', caption='罚款操作！！') == wx.ID_OK):
                if isinstance(grid, ProcessGrid):
                    rows = grid.GetRowsByValue(dirpath=nodeData, exe=nodeText)
                    grid.SetRowsValue(rows, status=STATUS)

                reRows = grid.GetRowsByValue(dirpath=nodeData, exe=nodeText)
                # 数据库死锁造成下架失败
                if not grid.isOnline(reRows):
                    if e:
                        e.Skip()
                    return False
                grid.ScrollToRow(reRows[0])
                self.item.Enable(True)
                self.item.Check(True)
                self.parent.AutoCheckParent(self.item, True)
                self.parent.checkedNodes.update({self.item: self.parent.GetNodePriority(self.item)})
        else:
            self.parent.dialog.warn('大兄弟，请核对数据库！', caption='搞锤子！！')
        if e:
            e.Skip()

    # TODO: 下线进程，多参数进程全体下线
    def OffLine(self, e):
        nodeType = self.parent.GetNodeType(self.item)
        nodeText = self.item.GetText()
        nodeData = os.path.dirname(self.item.GetData())
        STATUS = -1
        process = ProcessList.get_or_none(
            ProcessList.type == nodeType,
            ProcessList.exe == nodeText,
            ProcessList.dirpath == nodeData
        )
        grid = wx.FindWindowById(id=uid.PROCESS_PAGE_GRID)
        if isinstance(grid, ProcessGrid):
            rows = grid.GetRowsByValue(dirpath=nodeData, exe=nodeText)

        # 进程在运行中不允许做下架操作
        if grid.isOnRuning(rows):
            self.parent.dialog.warn('进程尚在运行，下架失败！', style=wx.OK | wx.ICON_EXCLAMATION)
            if e:
                e.Skip()
            return False
        if process:
            if (self.parent.dialog.danger('想清楚哈！', caption='罚款操作！！') == wx.ID_OK):
                # 刷新表格
                if not rows.empty:
                    grid.SetRowsValue(rows, status=STATUS)
                reRows = grid.GetRowsByValue(dirpath=nodeData, exe=nodeText)
                # 数据库死锁造成下架失败
                if grid.isOnline(reRows):
                    if e:
                        e.Skip()
                    return False
                grid.ScrollToRow(reRows[0])
                self.item.Enable(False)
                self.item.Check(False)
                self.parent.AutoCheckParent(self.item, False)
                if self.item in self.parent.checkedNodes:
                    self.parent.checkedNodes.pop(self.item)
        else:
            self.parent.dialog.warn('大兄弟，请核对数据库！', caption='搞锤子！！')
        if e:
            e.Skip()


# TODO：添加图标
class ImageList(wx.ImageList):
    def __init__(self, width=16, height=16, mask=True, initialCount=1):
        super(ImageList, self).__init__(width=width, height=height, mask=mask, initialCount=initialCount)
        self.__settings__()

    def __settings__(self):
        # 盘符图标 0
        self.Add(wx.ArtProvider.GetBitmap(wx.ART_HARDDISK, wx.ART_OTHER, size=(16, 16)))
        # 文件夹图标 1
        self.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, size=(16, 16)))
        # 普通文件图标 2
        self.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, size=(16, 16)))
        # 可执行文件图标 3
        self.Add(wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_OTHER, size=(16, 16)))
        # 错误文件图标 4
        self.Add(wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_OTHER, size=(16, 16)))


if __name__ == '__main__':
    pass
