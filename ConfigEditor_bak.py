#!/usr/bin/env python
# encoding: utf-8

import wx, wx.adv, wx.stc, wx.grid
# import wx.lib.buttons as wxButton
import os, sys, re, time, json
import chardet, codecs
import socket, urllib
from bs4 import BeautifulSoup
from common.SenLian_ConfigParser import DeployConfigure
from wx.lib.embeddedimage import PyEmbeddedImage
from common.B64data import *
import copy
import csv
import win32file
from threading import Thread
import shutil

wildcard = u"ini files (*.ini)|*.ini|" \
           "txt files (*.txt)|*.txt|" \
           "json files (*.json)|*.json|" \
           "exe files (*.exe)|*.exe|" \
           "pdb files (*.pdb)|*.pdb|" \
           "dll files (*.dll)|*.dll|" \
           "dmp files (*.dmp)|*.dmp|" \
           "All files (*.*)|*.*"


def FindFilter(rootPath, fileter=r'.*((groupserver)|(gameserver))+\.ini'):
    pattern = re.compile(fileter)
    patterndir = re.compile(r'(.*GameServer[\\\d_]+$)|(.*GroupGameServer[\\\d_]+$)+')
    QueueList = list()
    QueueList.append(os.path.normpath(rootPath))
    FindFiles = list()
    while len(QueueList) != 0:
        curPath = QueueList.pop(0)  # 从队列中弹出首个路径

        # 系统文件判断
        if win32file.GetFileAttributesW(curPath) == 22:
            continue
        if os.path.isdir(curPath):  # 判断路径是否为目录
            FileList = os.listdir(os.path.normpath(curPath))  # 若是目录，遍历将里面所有文件入队
            matchdir = patterndir.match(curPath)
            if matchdir:
                targetFile = os.path.join(curPath,
                                          ('groupserver.ini' if 'GroupGameServer' in curPath else 'gameserver.ini' \
                                              if 'MatchGameServer' not in curPath else 'matchserver.ini'))
                if not os.path.isfile(targetFile):
                    FindFiles.append(targetFile)
                    continue
            for f in FileList:
                findPath = os.path.join(curPath, f)
                QueueList.append(findPath)
        else:  # 如果是一个文件，判断是否为目标文件
            if pattern.match(curPath) and os.path.isfile(curPath):
                FindFiles.append(curPath)
    return FindFiles


# TODO: 获得文件编码格式
def code_type(file):
    return chardet.detect(open(file, 'rb').read())["encoding"]


# TODO: 字符串BASE64转码
def get_b64(img):
    f = openFile(img, 'rb', code_type(img))
    b64 = f.read().encode('base64')
    f.close()
    return b64


# TODO: 生成bitmap图标
def GetBitmap(b64):
    return PyEmbeddedImage(b64).GetBitmap()


# TODO: 生成ICON图标
def GetIcon(b64):
    return PyEmbeddedImage(b64).GetIcon()


# TODO: 打开文件
def openFile(targetFile, mode='r', encoding='utf-8'):
    if not os.path.isfile(targetFile) and mode == 'r':
        return ''
    return codecs.open(targetFile, mode=mode, encoding=encoding)


# print get_b64('./img/refresh.png')

# TODO: 保存文件
def SaveFile(targetFile, newText, saveAs=False):
    if not os.path.isfile(targetFile) and not saveAs:
        return
    else:
        # targetFileText = openFile(targetFile, encoding=code_type(targetFile)).readline()
        # if targetFileText == newText:
        #     return True
        with openFile(targetFile, 'w') as f:
            for line in newText.split('\n'):
                f.writelines(line + '\r\n')


# TODO: 另存为
def SaveAsFile(defaultDir='', defaultFile='', parent=None, newText=''):
    if not defaultDir:
        defaultDir = defaultFile
    if not parent:
        return False

    dlg = wx.FileDialog(parent, message=u"另存为",
                        defaultDir=defaultDir,
                        defaultFile=defaultFile,
                        wildcard=wildcard,
                        style=wx.FD_SAVE)
    targetFile = defaultFile
    if dlg.ShowModal() == wx.ID_OK:
        targetFile = dlg.GetPath()
        SaveFile(targetFile, newText, True)
    dlg.Destroy()
    return targetFile


def OpenFileDialog(defaultDir='', defaultFile='', parent=None):
    if not defaultDir:
        defaultDir = defaultFile
    if not parent:
        return False

    dlg = wx.FileDialog(parent, message=u"另存为",
                        defaultDir=defaultDir,
                        defaultFile=defaultFile,
                        wildcard=wildcard,
                        style=wx.FD_OPEN)
    targetFile = defaultFile
    if dlg.ShowModal() == wx.ID_OK:
        targetFile = dlg.GetPath()
    dlg.Destroy()
    return targetFile


def OpenDirDialog(defaultDir='', parent=None):
    if not parent:
        return False

    dlg = wx.DirDialog(parent, message=u"打开路径",
                       defaultPath=defaultDir,
                       style=wx.DD_DEFAULT_STYLE)
    targetDir = defaultDir
    if dlg.ShowModal() == wx.ID_OK:
        targetDir = dlg.GetPath()
    dlg.Destroy()
    return targetDir


# TODO: 系统剪切板缓存
def SaveToClipboard(text):
    text_obj = wx.TextDataObject()
    wx.TheClipboard.Open()
    text_obj.SetText(text)
    wx.TheClipboard.SetData(text_obj)
    wx.TheClipboard.Close()


# TODO: 获取系统剪切板缓存
def GetFromClipboard():
    text_obj = wx.TextDataObject()
    wx.TheClipboard.Open()
    wx.TheClipboard.GetData(text_obj)
    text = text_obj.GetText()
    wx.TheClipboard.Close()
    return text


def get_host_ip():
    return socket.gethostbyname_ex(socket.gethostname())[2][0]


def get_host_ip_ex():
    try:
        url = urllib.urlopen('https://ip.cn/')
        content = url.read()
        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf8')
        return soup.find('div', attrs={'id': 'cf-error-details'}).find('div', attrs={'class': 'cf-error-footer'}).find(
                'p').findAll('span')[2].get_text().split('Your IP:')[1].replace(' ', '')
    except:
        return None


class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent=parent, id=-1)
        self.settings()
        self.initID()
        self.initUI()
        self.initBind()

    def settings(self):
        self.SetTitle(u'配置修改器')
        self.SetSize((840, 640))
        self.Center()
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        # wx.Icon
        self.SetIcon(GetIcon(B64_ICON))
        self.RootPath = r'D:\WR-GameServer\gmserver'
        # self.Filter = '*.ini'
        self.Filter = wildcard
        self.FreeTemplate = os.path.abspath(u'./gameserver.ini')
        self.GroupTemplate = os.path.abspath(u'./groupserver.ini')
        self.RuleJson = os.path.abspath(u'./rule.json')
        self.BackPath = os.path.abspath(u'./backup')
        self.FontStyle = None
        self.FgColourStyle = wx.BLACK

    def initID(self):
        self.ID_SETTINS = wx.NewId()
        self.ID_ADD_TEMPLATE = wx.NewId()
        self.ID_DATE = wx.NewId()
        self.ID_WORD_WRAP = wx.NewId()
        self.ID_AUTO_SAVE = wx.NewId()
        self.ID_AUTO_EDIT = wx.NewId()

        self.ID_TOOLS = wx.NewId()
        self.ID_TOOLBAR = wx.NewId()
        self.ID_STATUS = wx.NewId()
        self.ID_STATUSBAR = wx.NewId()

        self.ID_TEMPLATES = wx.NewId()
        self.ID_GAME_LIST = wx.NewId()

    def initUI(self):
        self.TopMenuBar()
        self.TopToolBar()
        self.BottomStatuBar()
        self.MidWindow()

    def initBind(self):
        self.Bind(wx.EVT_MENU, self.SetBasicMenu, id=self.ID_SETTINS)
        self.Bind(wx.EVT_MENU, self.AddTemplateMenu, id=self.ID_ADD_TEMPLATE)
        self.Bind(wx.EVT_MENU, self.OpenFileMenu, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.CloseFileMenu, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnSetFont, id=wx.ID_SELECT_FONT)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, id=self.ID_TOOLS)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, id=self.ID_STATUS)
        return

    # TODO: 菜单栏
    def TopMenuBar(self):
        MyMenuBar = wx.MenuBar()

        FileMenu = wx.Menu()
        EditMenu = wx.Menu()
        FormatMenu = wx.Menu()
        ViewMenu = wx.Menu()
        HelpMenu = wx.Menu()

        # 文件菜单
        FileMenu.Append(wx.ID_OPEN, u'打开(&O)...\tCtrl+O')
        FileMenu.Append(wx.ID_SAVE, u'保存(&S)\tCtrl+S')
        FileMenu.Append(wx.ID_CLOSE, u'关闭(&C)\tAlt+C')
        FileMenu.Append(wx.ID_SAVEAS, u'另存为(&A)...')
        FileMenu.AppendSeparator()
        FileMenu.Append(self.ID_SETTINS, u'基础设置(&U)')
        FileMenu.Append(self.ID_ADD_TEMPLATE, u'模板添加(&T)')
        FileMenu.AppendSeparator()
        FileMenu.Append(wx.ID_EXIT, u'退出(&X)\tCtrl+Q')

        # 编辑菜单
        EditMenu.Append(wx.ID_REVERT, u'撤销(&U)\t Ctrl+Z', u'撤销')
        EditMenu.AppendSeparator()
        EditMenu.Append(wx.ID_CUT, u'剪切(&T)\t Ctrl+X', u'剪切')
        EditMenu.Append(wx.ID_COPY, u'复制(&C)\t Ctrl+C', u'复制')
        EditMenu.Append(wx.ID_PASTE, u'粘贴(&P)\t Ctrl+V', u'粘贴')
        EditMenu.Append(wx.ID_DELETE, u'删除(&L)\tDel', u'删除')
        EditMenu.AppendSeparator()
        EditMenu.Append(wx.ID_FIND, u'查找(&F)...\t Ctrl+F', u'查找')
        EditMenu.Append(wx.ID_REPLACE, u'替换(&R)...\t Ctrl+H', u'替换')
        EditMenu.Append(wx.ID_PREVIEW_GOTO, u'转到(&G)...\t Ctrl+G', u'转到')
        EditMenu.AppendSeparator()
        EditMenu.Append(wx.ID_SELECTALL, u'全选(&A)\t Ctrl+A', u'全选')
        EditMenu.Append(self.ID_DATE, u'时间/日期(&D)\tF5', u'输出时间/日期')

        # 格式菜单
        self.WordWarpMenu = FormatMenu.Append(self.ID_WORD_WRAP, u'自动换行(&W)', u'自动换行', kind=wx.ITEM_CHECK)
        FormatMenu.Bind(wx.EVT_MENU, self.ToggleWordWarp, id=self.ID_WORD_WRAP)

        FormatMenu.Append(wx.ID_SELECT_FONT, u'字体(&F)...', u'字体设置')

        # 查看菜单
        ViewMenu.Append(self.ID_TEMPLATES, u'查看模板(&T)')
        ViewMenu.Append(self.ID_GAME_LIST, u'游戏列表(&L)')
        ViewMenu.AppendSeparator()
        self.Tools = ViewMenu.Append(self.ID_TOOLS, u'工具栏(&T)', u'工具栏', kind=wx.ITEM_CHECK)
        self.Tools.Check(True)
        self.Status = ViewMenu.Append(self.ID_STATUS, u'状态栏(&S)', u'状态栏', kind=wx.ITEM_CHECK)
        self.Status.Check(True)

        # 帮助菜单
        HelpMenu.Append(wx.ID_HELP, u"说明(&H)", u"工具帮助信息")
        HelpMenu.Append(wx.ID_ABOUT, u"关于(&A)", u"作者@senlian")

        MyMenuBar.Append(FileMenu, u'文件(&F）')
        MyMenuBar.Append(EditMenu, u'编辑(&E）')
        MyMenuBar.Append(FormatMenu, u'格式(&O）')
        MyMenuBar.Append(ViewMenu, u'查看(&V）')
        MyMenuBar.Append(HelpMenu, u'帮助(&H)')
        self.SetMenuBar(MyMenuBar)
        return MyMenuBar

    def ToggleWordWarp(self, e):
        if self.WordWarpMenu.IsChecked():
            self.WordWarp.Toggle(True)
        else:
            self.WordWarp.Toggle(False)
        # wx.ToolBarToolBase.Toggle()
        self.SetTextStyle(self.MainPage.RightText)
        self.GetToolBar().Realize()

    # TODO: 工具栏
    def TopToolBar(self):
        MyToolBar = self.CreateToolBar(id=self.ID_TOOLBAR, style=wx.TB_NODIVIDER | wx.TB_FLAT, name=u'工具栏')
        # MyToolBar.AddTool(wx.ID_SAVE, 'save', wx.Bitmap('./img/save.png'), '保存')
        MyToolBar.AddTool(wx.ID_SAVE, 'save', GetBitmap(B64_SAVE), u'保存')
        MyToolBar.AddTool(wx.ID_SAVEAS, 'saveas', GetBitmap(B64_SAVE_AS), u'另存为')
        MyToolBar.AddTool(wx.ID_CLEAR, 'clear', GetBitmap(B64_CLEAR), u'清空')
        MyToolBar.AddSeparator()
        MyToolBar.AddRadioTool(wx.ID_JUSTIFY_LEFT, 'left', GetBitmap(B64_LEFT), shortHelp=u'左对齐').Toggle(True)
        MyToolBar.AddRadioTool(wx.ID_JUSTIFY_CENTER, 'center', GetBitmap(B64_CENTER), shortHelp=u'居中')
        MyToolBar.AddRadioTool(wx.ID_JUSTIFY_RIGHT, 'right', GetBitmap(B64_RIGHT), shortHelp=u'右对齐')
        MyToolBar.AddSeparator()
        self.WordWarp = MyToolBar.AddTool(self.ID_WORD_WRAP, 'wordwarp', GetBitmap(B64_WORDWARP), shortHelp=u'自动换行')
        self.WordWarp.SetToggle(True)
        MyToolBar.AddSeparator()
        AutoSave = MyToolBar.AddTool(self.ID_AUTO_SAVE, 'autosave', GetBitmap(B64_AUTO_SAVE), shortHelp=u'自动保存')
        AutoSave.SetToggle(True)
        MyToolBar.AddSeparator()
        AutoEdit = MyToolBar.AddTool(self.ID_AUTO_EDIT, 'autoedit', GetBitmap(B64_AUTO_EDIT), shortHelp=u'一键修改')

        # MyToolBar.AddSeparator()
        MyToolBar.Realize()
        return MyToolBar

    # TODO: 主体窗口
    def MidWindow(self):
        self.NoteBook = wx.Notebook(self, -1, name='Main', style=wx.NB_TOP | wx.NB_FIXEDWIDTH | wx.NB_FLAT)
        # 配置修改界面
        self.MainPage = PageOne(self)

        # 游戏列表界面
        self.GameListPage = PageTwo(self)
        self.NoteBook.AddPage(self.MainPage, u'主页')
        self.NoteBook.AddPage(self.GameListPage, u'游戏列表')
        self.NoteBook.Bind(wx.EVT_BOOKCTRL_PAGE_CHANGED, self.BookPageChang)

        return self.NoteBook

    # TODO: 状态栏
    def BottomStatuBar(self):
        self.MyStatuBar = self.CreateStatusBar(id=self.ID_STATUSBAR, number=3, style=65840, name=u'状态栏')
        self.MyStatuBar.SetStatusWidths([-3, -2, -1])
        text = 'ready'
        self.MyStatuBar.SetStatusText(text, 0)
        self.MyStatuBar.Show()
        return self.MyStatuBar

    def BookPageChang(self, e):
        curPage = self.NoteBook.GetCurrentPage()
        ToolBar = self.GetToolBar()
        if (curPage is self.GameListPage):
            self.SetToolEnable(False)
            ToolBar.EnableTool(wx.ID_SAVE, False)
            ToolBar.EnableTool(wx.ID_SAVEAS, False)
            ToolBar.EnableTool(wx.ID_CLEAR, False)
            ToolBar.EnableTool(self.ID_AUTO_SAVE, False)
            ToolBar.EnableTool(self.ID_AUTO_EDIT, False)
            ToolBar.AddTool(wx.ID_REFRESH, 'refresh', GetBitmap(B64_REFRESH), u'刷新')
            self.SetStbText(u'组队场/自由场', self.GetPageName())
        else:
            ToolBar.RemoveTool(wx.ID_REFRESH)
            self.SetToolEnable(True)
            ToolBar.EnableTool(wx.ID_SAVE, True)
            ToolBar.EnableTool(wx.ID_SAVEAS, True)
            ToolBar.EnableTool(wx.ID_CLEAR, True)
            ToolBar.EnableTool(self.ID_AUTO_SAVE, True)
            ToolBar.EnableTool(self.ID_AUTO_EDIT, True)
            curPath = self.MainPage.LeftTree.GetPath() or self.RootPath
            self.SetStbText(curPath, self.GetPageName(curPath))
        ToolBar.Realize()

    def GetPageName(self, filePath=''):
        if filePath:
            pageName = u'主页'
            if 'GameServer' in filePath.split(os.sep):
                pageName = u'自由场'
            if 'GroupGameServer' in filePath.split(os.sep):
                pageName = u'组队场'
            if 'MatchGameServer' in filePath.split(os.sep):
                pageName = u'比赛服'
            if 'DB' in filePath.split(os.sep) or 'DBServer' in filePath.split(os.sep):
                pageName = u'DB服'
            if 'AI' in filePath.split(os.sep) or 'AIServer' in filePath.split(os.sep):
                pageName = u'AI服'
        else:
            pageName = u'游戏列表'
        return pageName

    def SetStbText(self, path, pName):
        if os.path.isfile(path) and os.path.splitext(path)[1].lower() == '.ini':
            self.MyStatuBar.SetStatusText(os.path.dirname(path), 0)
            self.MyStatuBar.SetStatusText(os.path.basename(path), 1)
        else:
            self.MyStatuBar.SetStatusText(path, 0)
            self.MyStatuBar.SetStatusText('', 1)
        self.MyStatuBar.SetStatusText(pName, 2)

    def SetToolEnable(self, enable=True):
        ToolBar = self.GetToolBar()
        ToolBar.EnableTool(wx.ID_JUSTIFY_LEFT, enable)
        ToolBar.EnableTool(wx.ID_JUSTIFY_CENTER, enable)
        ToolBar.EnableTool(wx.ID_JUSTIFY_RIGHT, enable)
        ToolBar.EnableTool(self.ID_WORD_WRAP, enable)
        ToolBar.Realize()

    # TODO: wx.TextCtrl控件设置样式
    def SetTextStyle(self, TextCtrl):
        ToolBar = self.GetToolBar()
        TE_Style = wx.TE_MULTILINE + wx.TE_RICH

        # 以下两行，解决自动换行不刷新的问题
        TextCtrl.SetWindowStyleFlag(wx.TE_MULTILINE + wx.TE_RICH + wx.TE_LEFT)
        TextCtrl.SetWindowStyleFlag(wx.TE_MULTILINE + wx.TE_RICH + wx.TE_RIGHT)

        if ToolBar.FindById(wx.ID_JUSTIFY_LEFT).IsToggled():
            TE_Style += wx.TE_LEFT
        if ToolBar.FindById(wx.ID_JUSTIFY_CENTER).IsToggled():
            TE_Style += wx.TE_CENTER
        if ToolBar.FindById(wx.ID_JUSTIFY_RIGHT).IsToggled():
            TE_Style += wx.TE_RIGHT
        if ToolBar.FindById(self.ID_WORD_WRAP).IsToggled():
            TE_Style += wx.TE_WORDWRAP
            self.WordWarpMenu.Check(True)
        else:
            self.WordWarpMenu.Check(False)
            TE_Style += wx.HSCROLL

        if self.FgColourStyle:
            TextCtrl.SetForegroundColour(self.FgColourStyle)

        if self.FontStyle:
            TextCtrl.SetFont(self.FontStyle)
        TextCtrl.SetWindowStyleFlag(TE_Style)
        return TextCtrl

    def SetBasicMenu(self, e):
        setDialog = SetBasicDialog(self, u'基础设置')
        if setDialog.ShowModal() == wx.ID_OK:
            self.RootPath = setDialog.RootPath
            self.RuleJson = setDialog.RuleJson
            self.BackPath = setDialog.BackPath
        try:
            self.MainPage.LeftTree.CollapseTree()
            self.MainPage.LeftTree.ExpandPath(self.RootPath)
            self.MainPage.LeftTree.Update()
        except Exception as e:
            print(e)
        finally:
            setDialog.Destroy()

    def AddTemplateMenu(self, e):
        addDialog = AddTemplateDialog(self, u'添加模板')
        if addDialog.ShowModal() == wx.ID_OK:
            self.FreeTemplate = addDialog.FreeTemplate
            self.GroupTemplate = addDialog.GroupTemplate
        addDialog.Destroy()

    def OpenFileMenu(self, e):
        newFile = OpenFileDialog(self.RootPath, '', self)
        if os.path.isfile(newFile):
            self.MainPage.LeftTree.CollapseTree()
            self.MainPage.LeftTree.ExpandPath(newFile)
            text = openFile(newFile, encoding=code_type(newFile)).read()
            self.MainPage.RightText.SetLabelText(text)

    def CloseFileMenu(self, e):
        autoSaveTool = self.GetToolBar().FindById(self.ID_AUTO_SAVE)
        if autoSaveTool.IsToggled():
            SaveFile(self.MainPage.LeftTree.GetPath(), self.MainPage.RightText.GetValue())
        self.MainPage.LeftTree.CollapseTree()
        self.MainPage.LeftTree.ExpandPath(self.RootPath)
        self.MainPage.RightText.SetLabelText('')
        self.MainPage.RightText.Enable(False)

    def OnExit(self, e):
        self.Destroy()

    # 点击最小化时，隐藏界面，到托盘
    def OnIconfiy(self, e):
        self.TaskBarIcon = TaskBarIcon(self)
        self.Hide()

    def OnSetFont(self, e):
        myFontDialog = wx.FontDialog(self, wx.FontData())
        if myFontDialog.ShowModal() == wx.ID_OK:
            FontData = myFontDialog.GetFontData()
            self.FontStyle = FontData.GetChosenFont()
            self.FgColourStyle = FontData.GetColour()
            self.SetTextStyle(self.MainPage.RightText)
        myFontDialog.Destroy()

    def ToggleToolBar(self, e):
        ToolBar = self.GetToolBar()
        if self.Tools.IsChecked():
            ToolBar.Show()
        else:
            ToolBar.Hide()
        ToolBar.Realize()
        if e:
            e.Skip()

    def ToggleStatusBar(self, e):
        BtmStatusBar = self.GetStatusBar()
        if self.Status.IsChecked():
            self.BottomStatuBar()
            curPath = self.MainPage.LeftTree.GetPath()
            self.SetStbText(self.MainPage.LeftTree.GetPath(), self.GetPageName(curPath))
        else:
            BtmStatusBar.Destroy()
        if e:
            e.Skip()


# TODO: 模板添加
class SetBasicDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SetBasicDialog, self).__init__(parent, title=title, size=(350, 180))
        self.root = parent
        self.initUI()
        self.GetTemplate()

    def initUI(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        gridBox = wx.FlexGridSizer(3, 3, 15, 5)

        RootPathSTE = wx.StaticText(self, label=u'服务器路径', size=(60, 20))
        self.RootPathTE = wx.TextCtrl(self, size=(200, 20), value=os.path.abspath(self.root.RootPath))
        RootPathBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        RulePathSTE = wx.StaticText(self, label=u'游戏名配置', size=(60, 20))
        self.RulePathTE = wx.TextCtrl(self, size=(200, 20), value=os.path.abspath(self.root.RuleJson))
        RulePathBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        BackPathSTE = wx.StaticText(self, label=u'备份路径', size=(60, 20))
        self.BackPathTE = wx.TextCtrl(self, size=(200, 20), value=os.path.abspath(self.root.BackPath))
        BackPathBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        gridBox.Add(RootPathSTE)
        gridBox.Add(self.RootPathTE, 1, wx.EXPAND)
        gridBox.Add(RootPathBTN)

        gridBox.Add(RulePathSTE)
        gridBox.Add(self.RulePathTE, 1, wx.EXPAND)
        gridBox.Add(RulePathBTN)

        gridBox.Add(BackPathSTE)
        gridBox.Add(self.BackPathTE, 1, wx.EXPAND)
        gridBox.Add(BackPathBTN)

        wx.Button(self, wx.ID_OK, label=u"确认", size=(50, 20), pos=(200, 120))
        wx.Button(self, wx.ID_CANCEL, label=u"取消", size=(50, 20), pos=(260, 120))

        vBox.Add(gridBox, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)
        self.SetSizer(vBox)
        self.Bind(wx.EVT_BUTTON, self.SetRootPath, RootPathBTN)
        self.Bind(wx.EVT_BUTTON, self.SetRulePath, RulePathBTN)
        self.Bind(wx.EVT_BUTTON, self.SetBackPath, BackPathBTN)

    def GetTemplate(self):
        self.RootPath = self.RootPathTE.GetValue()
        self.RuleJson = self.RulePathTE.GetValue()
        self.BackPath = self.BackPathTE.GetValue()

    def SetRootPath(self, e):
        newpath = OpenDirDialog(self.RootPath, self)
        self.RootPathTE.SetValue(newpath)
        self.GetTemplate()

    def SetBackPath(self, e):
        newpath = OpenDirDialog(self.BackPath, self)
        self.BackPathTE.SetValue(newpath)
        self.GetTemplate()

    def SetRulePath(self, e):
        newpath = OpenFileDialog(self.RuleJson, self.RuleJson, self)
        self.RulePathTE.SetValue(newpath)
        self.GetTemplate()


# TODO: 模板添加
class AddTemplateDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(AddTemplateDialog, self).__init__(parent, title=title, size=(350, 140))
        self.root = parent
        self.initUI()
        self.GetTemplate()

    def initUI(self):
        vBox = wx.BoxSizer(wx.VERTICAL)
        gridBox = wx.FlexGridSizer(2, 3, 15, 5)

        FSTE = wx.StaticText(self, label=u'自由场配置', size=(60, 20))
        self.FTE = wx.TextCtrl(self, size=(200, 20), value=os.path.abspath(self.root.FreeTemplate))
        FBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))
        GSTE = wx.StaticText(self, label=u'组队场配置', size=(60, 20))
        self.GTE = wx.TextCtrl(self, size=(200, 20), value=os.path.abspath(self.root.GroupTemplate))
        GBTN = wx.Button(self, wx.ID_ANY, label="...", size=(25, 20))

        gridBox.Add(FSTE)
        gridBox.Add(self.FTE, 1, wx.EXPAND)
        gridBox.Add(FBTN)

        gridBox.Add(GSTE)
        gridBox.Add(self.GTE, 1, wx.EXPAND)
        gridBox.Add(GBTN)

        wx.Button(self, wx.ID_OK, label=u"确认", size=(50, 20), pos=(200, 80))
        wx.Button(self, wx.ID_CANCEL, label=u"取消", size=(50, 20), pos=(260, 80))
        vBox.Add(gridBox, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)
        self.SetSizer(vBox)
        self.Bind(wx.EVT_BUTTON, self.SetFreeTemplate, FBTN)
        self.Bind(wx.EVT_BUTTON, self.SetGroupTemplate, GBTN)

    def GetTemplate(self):
        self.FreeTemplate = self.FTE.GetValue()
        self.GroupTemplate = self.GTE.GetValue()

    def SetFreeTemplate(self, e):
        newpath = OpenFileDialog(self.FreeTemplate, self.FreeTemplate, self)
        self.FTE.SetValue(newpath)
        self.GetTemplate()

    def SetGroupTemplate(self, e):
        newpath = OpenFileDialog(self.GroupTemplate, self.GroupTemplate, self)
        self.GTE.SetValue(newpath)
        self.GetTemplate()


# TODO: 修改界面
class PageOne(wx.SplitterWindow):
    def __init__(self, root):
        self.root = root
        super(PageOne, self).__init__(parent=self.root.NoteBook, style=wx.SP_NOBORDER)
        self.initUI()

    def initUI(self):
        # self.LeftTree = wx.GenericDirCtrl(self, -1, size=(160, 520), style=wx.DIRCTRL_SHOW_FILTERS)
        self.LeftTree = wx.GenericDirCtrl(self, -1, size=(160, 520), style=wx.DIRCTRL_SHOW_FILTERS)
        self.LeftTree.Filter = self.root.Filter
        self.LeftTree.ExpandPath(self.root.RootPath)
        self.focusPath = self.LeftTree.GetPath()

        # self.RightText = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_RICH | wx.TE_LEFT | wx.HSCROLL)
        self.TextStyle = wx.TE_MULTILINE + wx.TE_RICH + wx.TE_LEFT + wx.HSCROLL
        self.RightText = self.CreatTextCtrl()
        # self.RightText = wx.stc.StyledTextCtrl(self, -1, style=wx.stc.STC_STYLE_DEFAULT)
        # self.TreeBind(False)
        self.SetMinimumPaneSize(200)  # 左侧面板大小
        self.SplitVertically(self.LeftTree, self.RightText, 100)  # 分割面板

        self.LeftTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.TreeBind)
        # self.LeftTree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.TreeBind)
        self.root.Bind(wx.EVT_TOOL, self.ToolBarBind)

    def CreatTextCtrl(self):
        ToolBar = self.root.GetToolBar()
        RightText = self.root.SetTextStyle(wx.TextCtrl(self, -1, style=self.TextStyle))
        ToolBar.FindById(wx.ID_SAVE).Enable(True)
        ToolBar.FindById(wx.ID_SAVEAS).Enable(True)
        ToolBar.FindById(wx.ID_CLEAR).Enable(True)
        ToolBar.Realize()
        return RightText

    def TreeBind(self, e):
        if not (type(self.RightText) == wx._core.TextCtrl):
            self.RightText = self.CreatTextCtrl()
        # 自动保存
        ToolBar = self.root.GetToolBar()
        autoSaveTool = ToolBar.FindById(self.root.ID_AUTO_SAVE)
        autoEdit = ToolBar.FindById(self.root.ID_AUTO_EDIT)
        if not autoEdit.IsEnabled():
            autoEdit.Enable(True)
            ToolBar.Realize()

        if autoSaveTool.IsToggled():
            SaveFile(self.focusPath, self.RightText.GetValue())
        # 路径切换
        self.focusPath = self.LeftTree.GetPath()
        self.LeftTree.ExpandPath(self.focusPath)

        if os.path.isfile(self.focusPath) and os.path.splitext(self.focusPath)[1].lower() == '.ini':
            self.RightText.Enable(True)
            if self.RightText.IsEnabled():
                self.root.SetToolEnable(True)
            text = openFile(self.focusPath, encoding=code_type(self.focusPath)).readlines()

            self.RightText.SetLabelText('')
            self.RightText.flush()
            # self.RightText.SetLabelText(text)

            for line in text:
                if re.findall('^\[.*\]', line):
                    self.RightText.SetDefaultStyle(wx.TextAttr(wx.BLUE))
                else:
                    self.RightText.SetDefaultStyle(wx.TextAttr(self.root.FgColourStyle))
                self.RightText.AppendText(line)
                # self.RightText.LoadFile(self.focusPath)
        else:
            if self.RightText.GetValue():
                self.RightText.SetLabelText(self.RightText.GetValue())
                self.RightText.Enable(False)
            if not self.RightText.IsEnabled():
                self.root.SetToolEnable(False)
        pageName = self.root.GetPageName(self.focusPath)
        try:
            self.root.SetStbText(self.focusPath, pageName)
        except Exception as e:
            print(e)
        if e:
            e.Skip()

    def ToolBarBind(self, e):
        curID = e.GetId()
        if curID == wx.ID_CLEAR:
            SaveToClipboard(self.RightText.GetValue())
            self.RightText.SetValue('')

        if curID == wx.ID_REVERT:
            self.RightText.SetValue(GetFromClipboard())

        if curID == wx.ID_SAVE:
            if os.path.isfile(self.focusPath):
                SaveFile(self.focusPath, self.RightText.GetValue())
            else:
                SaveAsFile(self.focusPath, self.focusPath, self.root, self.RightText.GetValue())

        if curID == wx.ID_SAVEAS:
            SaveAsFile(self.focusPath, self.focusPath, self.root, self.RightText.GetValue())

        if curID == self.root.ID_AUTO_EDIT:
            self.FileList = FindFilter(self.focusPath)
            ToolBar = self.root.GetToolBar()
            autoEdit = ToolBar.FindById(self.root.ID_AUTO_EDIT)

            if len(self.FileList) <= 1:
                if autoEdit.IsEnabled():
                    autoEdit.Enable(False)
                    ToolBar.Realize()
                    return
            self.AutoEdit()

        if curID in [wx.ID_JUSTIFY_LEFT, wx.ID_JUSTIFY_CENTER, wx.ID_JUSTIFY_RIGHT, self.root.ID_WORD_WRAP]:
            self.root.SetTextStyle(self.RightText)
            # self.SetStcTextStyle()

        if e:
            e.Skip()

    # TODO: wx.stc.StyledTextCtrl控件设置样式
    def SetStcTextStyle(self):
        ToolBar = self.root.GetToolBar()
        if ToolBar.FindById(wx.ID_JUSTIFY_LEFT).IsToggled():
            self.RightText.SetWrapMode(wx.TE_LEFT)
        if ToolBar.FindById(wx.ID_JUSTIFY_CENTER).IsToggled():
            self.RightText.SetWrapMode(wx.TE_CENTER)
        if ToolBar.FindById(wx.ID_JUSTIFY_RIGHT).IsToggled():
            self.RightText.SetWindowStyle(wx.stc.STC_MARK_LEFTRECT)

        if ToolBar.FindById(self.root.ID_WORD_WRAP).IsToggled():
            self.RightText.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.RightText.SetWrapMode(wx.stc.STC_WRAP_NONE)
        self.RightText.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.RightText.SetMarginWidth(1, 30)

    def AutoEdit(self):
        # 游戏名
        self.ServiceNames = json.loads(
                codecs.open(self.root.RuleJson, "r", encoding='utf-8', errors='ignore').read().replace("\\", "\\\\"))
        # 需要修改的文件
        MyThread(self)


class PageTwo(wx.SplitterWindow):
    def __init__(self, root):
        self.root = root
        super(PageTwo, self).__init__(parent=self.root.NoteBook, style=wx.SP_NOBORDER)
        self.initUI()

    def initUI(self):
        self.GameListFile = os.path.abspath('./GameList.csv')
        self.GroupListFile = os.path.abspath('./GroupList.csv')
        self.LeftGrid = PageTwoGrid(self, self.GameListFile)
        self.RightGrid = PageTwoGrid(self, self.GroupListFile)
        w, h = self.root.NoteBook.GetSize()
        self.SetMinimumPaneSize(w / 2)
        self.SplitVertically(self.RightGrid, self.LeftGrid, 100)
        self.root.Bind(wx.EVT_TOOL, self.RefeshData, id=wx.ID_REFRESH)

    def RefeshData(self, e):
        self.LeftGrid.SetGridValue(self.GameListFile)
        self.RightGrid.SetGridValue(self.GroupListFile)


class PageTwoGrid(wx.grid.Grid):
    def __init__(self, root, filename):
        self.root = root
        super(PageTwoGrid, self).__init__(parent=self.root)
        self.CreateGrid(0, 4)
        for index, data in enumerate(['Dir', 'GameID', 'ServicePort', 'ServerID']):
            self.SetColLabelValue(index, data)
        self.SetRowLabelSize(40)
        self.SetGridValue(filename)

    def SetGridValue(self, filename):
        if not os.path.isfile(filename):
            return
        with codecs.open(filename, 'rb') as csvFile:
            csvFile.seek(0)
            try:
                dialect = csv.Sniffer().sniff(csvFile.read(1024))
            except Exception as e:
                print(e)
                return
            csvFile.seek(0)
            csvreader = list(csv.reader(csvFile, dialect))
            cols = len(csvreader)
            rows = len(csvreader[0])
            if (cols - self.GetNumberRows()) > 1:
                self.InsertRows(self.GetNumberRows(), cols - 1, True)
            # self.CreateGrid(cols - 1, rows)
            for index, data in enumerate(csvreader[0]):
                self.SetColLabelValue(index, data)
            for col in range(1, cols):
                for row in range(rows):
                    self.SetCellValue(col - 1, row, csvreader[col][row])


class MyThread(Thread):
    def __init__(self, parent=None):
        super(MyThread, self).__init__()
        self.LeftTree = parent.LeftTree
        self.RightText = parent.RightText
        self.FileList = parent.FileList
        self.root = parent.root
        self.ServiceNames = parent.ServiceNames
        self.start()

    def run(self):
        csvObj = None
        csvOldF = None
        for curFile in self.FileList:
            self.LeftTree.CollapseTree()
            self.LeftTree.ExpandPath(os.path.abspath(curFile))
            subDir = os.path.basename(os.path.dirname(curFile))
            if not (re.findall(r'^[\d_]+$', subDir)):
                continue
            GameID = subDir.split('_')[0]
            if curFile.endswith(str(os.path.basename(self.root.FreeTemplate))):
                Template = self.root.FreeTemplate
                defaultName = u'[自由]游戏服'
                csvFile = os.path.abspath('./GameList.csv')
            elif curFile.endswith(str(os.path.basename(self.root.GroupTemplate))):
                Template = self.root.GroupTemplate
                defaultName = u'[组队]游戏服'
                csvFile = os.path.abspath('./GroupList.csv')
            else:
                Template = None
                continue

            if not Template:
                return False
            if csvOldF != csvFile:
                if os.path.isfile(csvFile):
                    newFileName = os.path.splitext(os.path.basename(csvFile))[0] + time.strftime('_%Y%m%d%H%M%S') + \
                                  os.path.splitext(os.path.basename(csvFile))[1]
                    if not os.path.isdir(self.root.BackPath):
                        os.makedirs(self.root.BackPath)
                    dstFile = os.path.normpath(os.path.join(self.root.BackPath, newFileName))
                    shutil.move(csvFile, dstFile)
                csvFP = open(csvFile, 'w')
                csvObj = csv.writer(csvFP)
                csvObj.writerow(['Dir', 'GameID', 'ServicePort', 'ServerID'])
                csvOldF = csvFile
            else:
                csvFP = open(csvFile, 'a')
                csvObj = csv.writer(csvFP)

            LocalTemplate = DeployConfigure(Template)
            ServiceName = self.ServiceNames.get(subDir, defaultName)

            for sec in LocalTemplate.sections:
                for opt in LocalTemplate.get_options(sec):
                    value = LocalTemplate.get_value(sec, opt)
                    if re.findall('^GameID$', value, re.IGNORECASE):
                        value = GameID
                    if re.findall('^ServiceName$', value, re.IGNORECASE):
                        value = ServiceName
                    if re.findall('^IP\*$', value, re.IGNORECASE):
                        value = get_host_ip_ex()
                    if re.findall('^IP$', value, re.IGNORECASE):
                        value = get_host_ip()
                    if re.findall('^\d+\+$', value):
                        var = locals().get(sec + '_' + opt, None)
                        if not var:
                            var = int(value[0:-1])
                            locals().update({sec + '_' + opt: var})
                        else:
                            locals().update({sec + '_' + opt: int(var) + 1})
                        var = locals().get(sec + '_' + opt, None)
                        value = str(var)
                    LocalTemplate.set_value(sec, opt, str(value.encode('utf-8')))
            csvObj.writerow([subDir, GameID,
                             locals().get('GroupServer_ServicePort', locals().get('GameServer_ServicePort', 0)),
                             locals().get('GroupServer_ServerID', 0)])
            csvFP.close()
            LocalTemplate.save(curFile)


# TODO: 最小化托盘
class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super(TaskBarIcon, self).__init__()
        self.MainFrame = frame
        self.initID()
        self.initUI()
        self.initBind()

    # 生成组件ID
    def initID(self):
        self.ViewID = wx.NewId()

    # 生成界面
    def initUI(self):
        self.settings()

    # 事件监控
    def initBind(self):
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDclick)
        # 监听菜单栏中的退出选项
        self.Bind(wx.EVT_MENU, self.OnDclick, id=self.ViewID)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

    # 基础设置
    def settings(self):
        from wx.lib.embeddedimage import PyEmbeddedImage
        icon = PyEmbeddedImage(B64_ICON).GetIcon()
        self.MainFrame.Hide()
        self.SetIcon(icon, u'配置修改器')

    # 生成最小化菜单, 默认右键单击调用PopupMenu方法呼出菜单
    def CreatePopupMenu(self):
        self.TaskBarIconMenu = wx.Menu()
        # self.ExitMenu = wx.Menu()

        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(self.ViewID, u"显示主界面(&M)")
        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(wx.ID_EXIT, u"退出(&X)")
        return self.TaskBarIconMenu

    # 单击, 当前没有使用
    def OnClick(self, event):
        print(self.MainFrame.IsIconized())

    # 双击展示主面板
    def OnDclick(self, event):
        # Destroy删除元素，无法恢复创建
        self.Destroy()
        self.MainFrame.Iconize(False)
        self.MainFrame.Restore()

    # 退出
    def OnExit(self, event):
        # 托盘图标销毁
        self.Destroy()
        # 主面板销毁
        self.MainFrame.Destroy()
        # 退出wx进程
        # wx.Exit()


class MyApp(wx.App):
    def OnInit(self):
        window = MyFrame()
        window.Show()
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
