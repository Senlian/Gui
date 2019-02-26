import wx


class MyFrame3(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(900, 600),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        Sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        Sizer1.SetMinSize(wx.Size(0, 0))
        self.Right_Panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        self.Right_Panel.SetSizer(RightSizer)
        self.Right_Panel.Layout()
        RightSizer.Fit(self.Right_Panel)
        Sizer1.Add(self.Right_Panel, 1, wx.EXPAND | wx.ALL, 5)
        self.Left_Panel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        self.ImportButton = wx.Button(self.Left_Panel, wx.ID_ANY, u"Import CSV File", wx.DefaultPosition,
                                      wx.DefaultSize, 0)
        LeftSizer.Add(self.ImportButton, 0, wx.ALL, 5)
        self.Left_Panel.SetSizer(LeftSizer)
        self.Left_Panel.Layout()
        LeftSizer.Fit(self.Left_Panel)
        Sizer1.Add(self.Left_Panel, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(Sizer1)
        self.Layout()
        self.menubar = wx.MenuBar(0)
        self.fileMenu = wx.Menu()
        self.importMenu = wx.MenuItem(self.fileMenu, wx.ID_ANY, u"Import", wx.EmptyString, wx.ITEM_NORMAL)
        self.fileMenu.Append(self.importMenu)
        self.menubar.Append(self.fileMenu, u"&File")
        self.SetMenuBar(self.menubar)
        self.Centre(wx.BOTH)
        # Connect Events
        self.ImportButton.Bind(wx.EVT_BUTTON, self.ImportFunc)
        self.Bind(wx.EVT_MENU, self.ImportFunc, id=self.importMenu.GetId())


class csv_view(wx.App):
    def OnInit(self):
        self.frame = MyFrame3(None, -1, 'PyStereo', size=(900, 600))
        self.SetTopWindow(self.frame)
        return True
