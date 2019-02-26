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
import wx.aui


# TODO: 主体结构
class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent=parent, id=-1)
        self.auiManager = wx.aui.AuiManager()
        self.auiManager.SetManagedWindow(self)

        self.initID()
        self.initUI()
        self.initBind()

    # 生成组件ID
    def initID(self):
        # 文件
        self.NewID = wx.NewId()
        self.OpenID = wx.NewId()
        self.SaveID = wx.NewId()
        self.SaveAsID = wx.NewId()
        self.SetDirID = wx.NewId()
        self.AddTemplateID = wx.NewId()

        # 编辑
        self.RepealID = wx.NewId()
        self.CutID = wx.NewId()
        self.CopyID = wx.NewId()
        self.PasteID = wx.NewId()
        self.DeleteID = wx.NewId()
        self.FindID = wx.NewId()
        self.ReplaceID = wx.NewId()
        self.GotoID = wx.NewId()
        self.DataID = wx.NewId()

        # 格式
        self.WordWrapID = wx.NewId()
        self.FontID = wx.NewId()

        # 查看
        self.LookOverID = wx.NewId()
        self.GameListID = wx.NewId()
        self.ToolBarID = wx.NewId()
        self.StatusBarID = wx.NewId()

        # 帮助
        self.DirectionID = wx.NewId()

    # 生成界面
    def initUI(self):
        self.settings()
        self.TopMenuBar()
        self.ToolBar = self.TopToolBar()
        self.auiManager.AddPane(self.ToolBar, wx.aui.AuiPaneInfo().Name("toolbar").Caption(
                "Toolbar Demo").Top().LeftDockable(False).RightDockable(False).MaximizeButton(True).MinimizeButton(
            True).TopDockable().Resizable())
        panle = self.MainPanel()
        self.BtmStatusBar = self.BottomStatusBar()
        self.auiManager.AddPane(panle, wx.aui.AuiPaneInfo().Center().CloseButton(False))
        self.auiManager.Update()

    # 事件监控
    def initBind(self):
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, id=self.ToolBarID)
        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, id=self.StatusBarID)
        self.Bind(wx.EVT_MENU, self.SelectALL, id=wx.ID_SELECTALL)

    # 主界面设置
    def settings(self):
        self.SetTitle('配置修改器')
        # self.Position = (800, 300)
        self.Centre()
        self.SetSize(360, 420)
        # self.SetMinSize(360, 420)
        # self.SetMaxSize((480, 720))
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        self.SetName('topFrame')
        self.SetIcon(wx.Icon('./icon/favicon.ico'))

    # 点击关闭时，隐藏界面，到托盘
    def OnClose(self, event):
        # 此处监听到最小化事件，执行self.OnIconfiy
        self.Iconize(True)

    # 点击最小化时，隐藏界面，到托盘
    def OnIconfiy(self, e):
        self.TaskBarIcon = TaskBarIcon(self)
        self.Hide()
        if e:
            e.Skip()

    # 退出
    def OnExit(self, e):
        self.Destroy()
        if e:
            e.Skip()

    # 窗口还原
    def Restore(self, e):
        # 消除最小化
        if self.IsIconized():
            self.Iconize(False)
        # 面板展示
        if not self.IsShown():
            self.Show()
        # 至于窗口最上方
        self.Raise()
        if e:
            e.Skip()

    # 菜单栏
    def TopMenuBar(self):
        topMenuBar = wx.MenuBar()
        # 文件菜单
        FileMenu = wx.Menu()
        NewItem = wx.MenuItem(FileMenu, self.NewID, text='新建(&N)\tCtrl+N')
        OpenItem = wx.MenuItem(FileMenu, self.OpenID, text='打开(&O)...\tCtrl+O')
        SaveItem = wx.MenuItem(FileMenu, self.SaveID, text='保存(&S)\tCtrl+S')
        SaveAsItem = wx.MenuItem(FileMenu, self.SaveAsID, text='另存为(&A)...')

        SetDirItem = wx.MenuItem(FileMenu, self.SetDirID, text='基础设置(&U)')
        # SetDir.SetBitmap(wx.Bitmap('./icon/favicon.ico'))
        AddTemplateItem = wx.MenuItem(FileMenu, self.AddTemplateID, text='模板添加(&T)')

        QuitItem = wx.MenuItem(FileMenu, wx.ID_EXIT, text='退出(&X)\tCtrl+Q')

        FileMenu.Append(NewItem)
        FileMenu.Append(OpenItem)
        FileMenu.Append(SaveItem)
        FileMenu.Append(SaveAsItem)

        FileMenu.AppendSeparator()
        FileMenu.Append(SetDirItem)

        FileMenu.Append(AddTemplateItem)
        FileMenu.AppendSeparator()
        FileMenu.Append(QuitItem)

        # 编辑菜单
        EditMenu = wx.Menu()
        EditMenu.Append(self.RepealID, '撤销(&U)\tCtrl+Z', '撤销')
        EditMenu.AppendSeparator()
        EditMenu.Append(self.CutID, '剪切(&T)\tCtrl+X', '剪切')
        EditMenu.Append(self.CopyID, '复制(&C)\tCtrl+C', '复制')
        EditMenu.Append(self.PasteID, '粘贴(&P)\tCtrl+V', '粘贴')
        EditMenu.Append(self.DeleteID, '删除(&L)\tDel', '删除')
        EditMenu.AppendSeparator()
        EditMenu.Append(self.FindID, '查找(&F)...\tCtrl+F', '查找')
        EditMenu.Append(self.ReplaceID, '替换(&R)...\tCtrl+H', '替换')
        EditMenu.Append(self.GotoID, '转到(&G)...\tCtrl+G', '转到')
        EditMenu.AppendSeparator()
        EditMenu.Append(wx.ID_SELECTALL, '全选(&A)\tCtrl+A', '全选')
        EditMenu.Append(self.DataID, '时间/日期(&D)\tF5', '输出时间/日期')

        # 格式菜单
        FormatMenu = wx.Menu()
        FormatMenu.Append(self.WordWrapID, '自动换行(&W)', '自动换行')
        FormatMenu.Append(self.FontID, '字体(&F)...', '字体设置')

        # 查看菜单
        ViewMenu = wx.Menu()
        ViewMenu.Append(self.LookOverID, '查看模板(&T)')
        ViewMenu.Append(self.GameListID, '游戏列表(&L)')
        ViewMenu.AppendSeparator()
        self.ToolBarShow = ViewMenu.Append(self.ToolBarID, '工具栏(&T)', '工具栏', kind=wx.ITEM_CHECK)
        self.ToolBarShow.Check(True)
        self.StatusBarShow = ViewMenu.Append(self.StatusBarID, '状态栏(&S)', '状态栏', kind=wx.ITEM_CHECK)
        self.StatusBarShow.Check(True)
        # 帮助菜单
        HelpMenu = wx.Menu()
        HelpMenu.Append(self.DirectionID, "说明(&H)", "工具帮助信息")
        HelpMenu.Append(wx.ID_ABOUT, "关于(&A)", "作者@senlian")

        topMenuBar.Append(FileMenu, '文件(&F）')
        topMenuBar.Append(EditMenu, '编辑(&E）')
        topMenuBar.Append(FormatMenu, '格式(&O）')
        topMenuBar.Append(ViewMenu, '查看(&V）')
        topMenuBar.Append(HelpMenu, '帮助(&H)')
        self.SetMenuBar(topMenuBar)

    # 工具栏
    def TopToolBar(self):
        ToolBar = self.CreateToolBar(style=wx.TB_NODIVIDER | wx.TB_FLAT)
        save = wx.Bitmap('save_16.png')
        clear = wx.Bitmap('clear.png')
        left = wx.Bitmap('left.png')
        center = wx.Bitmap('center.png')
        right = wx.Bitmap('right.png')
        # bitmap.SetSize((32, 32))

        # ToolBar.AddSeparator()
        ToolBar.AddTool(wx.NewId(), 'save', save, '保存')
        ToolBar.AddTool(wx.NewId(), 'clear', clear, '清空')
        ToolBar.AddSeparator()
        ToolBar.AddRadioTool(wx.NewId(), 'left', left, shortHelp='左对齐')
        ToolBar.AddRadioTool(wx.NewId(), 'center', center, shortHelp='居中')
        ToolBar.AddRadioTool(wx.NewId(), 'right', right, shortHelp='右对齐')
        ToolBar.AddSeparator()
        ToolBar.Realize()
        return ToolBar

    def ToggleToolBar(self, event):
        if self.ToolBarShow.IsChecked():
            self.ToolBar.Show()
        else:
            self.ToolBar.Hide()
        self.ToolBar.Realize()

    def BottomStatusBar(self):
        StatusBar = self.CreateStatusBar()
        StatusBar.SetStatusText('ready')
        StatusBar.Show()
        return StatusBar

    def ToggleStatusBar(self, event):
        if self.StatusBarShow.IsChecked():
            self.BtmStatusBar = self.BottomStatusBar()
        else:
            self.BtmStatusBar.Destroy()

    def SelectALL(self, evnet):
        self.FindFocus()

    def MainPanel(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('white')
        # loadButton = wx.Button(panel, label='Open')
        # saveButton = wx.Button(panel, label='Save')

        contents = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_RICH | wx.HSCROLL)
        f = open(r'E:\\SVN\\src_code\\config\\gameserver.ini', 'r', encoding='utf-8')
        content = f.read()
        contents.LabelText = content
        print(contents.LabelText)

        hbox = wx.BoxSizer()
        # hbox.Add(combo, proportion=1, flag=wx.EXPAND)
        # hbox.Add(loadButton, proportion=0, flag=wx.Left, border=5)
        # hbox.Add(saveButton, proportion=0, flag=wx.Left, border=5)

        vbox = wx.BoxSizer()
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(contents, proportion=1, flag=wx.EXPAND | wx.Left | wx.Bottom | wx.RIGHT, border=5)

        panel.SetSizer(vbox)
        return panel


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
        self.MainFrame.Hide()
        self.SetIcon(wx.Icon('./icon/favicon.ico', wx.BITMAP_TYPE_ICO), '配置修改器')

    # 生成最小化菜单, 默认右键单击调用PopupMenu方法呼出菜单
    def CreatePopupMenu(self):
        self.TaskBarIconMenu = wx.Menu()
        # self.ExitMenu = wx.Menu()

        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(self.ViewID, "显示主界面(&M)")
        self.TaskBarIconMenu.AppendSeparator()
        self.TaskBarIconMenu.Append(wx.ID_EXIT, "退出(&X)")
        return self.TaskBarIconMenu

    # 单击, 当前没有使用
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
