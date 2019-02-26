# -*- coding: utf-8 -*-
import hashlib
import os
import wx
#编辑器主类
"""
记录：menu：Menu
Dialog: MessageDialog,MultiChoiceDialog,NumberEntryDialog,PasswordEntryDialog,PrintDialog,ProgressDialog,SingleChoiceDialog,TextEntryDialog,
FileDialog,FindReplaceDialog,FontDialog
StaticText
 设置style=wx.TE_PASSWORD，可以让wx.TextCtrl变成密码输入框。
 设置style=wx.TE_READONLY，可以让wx.TextCtrl变成只读输入框。
 如果文字过长，wx.TE_DONTWRAP设置强制不换行，wx.TE_LINEWRAP以字符为界断行，wx.TE_WORDWRAP以单词为界断行。
 wx.TextCtrl可以响应wx.EVT_TEXT事件，当输入的内容有变化时即可触发此事件。无论是用户输入引起的变化，还是通过setValue()引起的变化都会触发


 在wxPython中加速器是一个更加典型的键盘快捷方式，它意味能够随时调用的按键组合，这些按键组合直接触发菜单项。加速器可以用两种方法创建。最简单的方法是，在菜单或菜单项的显示文本中包括加速器按键组合（当菜单或菜单项被添加到其父中时）。实现的方法是，在你的菜单项的文本后放置一个\t。在\t之后定义组合键。组合键的第一部分是一个或多个Alt, Ctrl, 或Shift，由一个+或一个-分隔，随后是实际的加速器按键。例如：New\tctrl-n, SaveAs\tctrl-shift-s。即使在第一部分你只有一个专用的键，你仍可使用+或-来将该部分与实际的按键分隔。这不区分按键组合的大小写。

实际的键可以是任何数字、字母或功能键（如F1~F12），还有表10.6所列出的专用词。

wxPython的方法在通过名字查找一个菜单或菜单项时忽略助记符和加速器。换句话说，对menubar.FindMenuItem("File", "SaveAs")的调用将仍匹配Save as菜单项，即使菜单项的显示名是以Save \tctrl-shift-s形式输入的。

加速器也可能使用加速器表被直接创建，加速器表是类wx.AccleratorTable的一个实例。一个加速器表由wx.AccelratorEntry对象的一个列表组成。wx.AcceleratorTable的构造函数要求一个加速器项的列表，或不带参数。在例10.6中，我们利用了wxPython将隐式使用参数(wx.ACCEL_CTRL, od('Q')，exit.GetId())调用wx.AcceleratorEntry构造函数的事实。wx.AcceleratorEntry的构造函数如下：

wx.AcceleratorEntry(flags, keyCode, cmd)

flags参数是一个使用了一个或多个下列常量的位掩码：wx.ACCEL_ALT, wx.ACCEL_CTRL, wxACCEL_NORMAL , 或wx.ACCEL_SHIFT。该参数表明哪个控制键需要被按下来触发该加速器。keyCode参数代表按下来触发加速器的常规键，它是对应于一个字符的ASCII数字，或在wxWidgets文本中的Keycodes下的一个专用字符。cmd参数是菜单项的wxPython标识符，该菜单项当加速器被调用时触发其命令事件。正如你从例10.6所能看到的，使用这种方法声明一个加速器，不会在这个带菜单项显示名的菜单上列出组合键。你仍需要单独实现它。
"""
'''''
    @Author xiaoshuang
    @Date 2012-05-10
    @Version 0.1
'''
class NotBookMainFrame(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title)

        self.tb = self.CreateToolBar()
        self.control = wx.TextCtrl(self,style=wx.TE_MULTILINE,size=(300,500))

        #Alt
        #self.control.Bind(wx.EVT_CHAR, self.OnKeyDown)

        # 创建一个状态bar，在window的最下端
        self.sbar = self.CreateStatusBar()
        # 创建菜单栏
        menuB  = self.createMenuBar()
        # set menuBar of app
        self.SetMenuBar(menuB)

        #Ctrl
        acceltbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('Q'), self.selectA.GetId())])
        self.SetAcceleratorTable(acceltbl)

        #frame show
        self.Show(True)

    def createMenuBar(self):
        #Menu
        #Append(self, id, text, help, kind)
        fileM = wx.Menu()
        newF = fileM.Append(wx.NewId(),"新建(N)\tCtrl+N","打开一个已存在的文件.")
        fmitem = fileM.Append(wx.NewId(),"打开(O)\tCtrl+O","打开一个已存在的文件.")
        save = fileM.Append(wx.NewId(),  "保存(S)\tCtrl+S","保存当前的文件.")
        toSave = fileM.Append(wx.NewId(),"另存为(A)..","保存当前的文件.")
        fileM.AppendSeparator()
        fileM.Append(wx.NewId(),"页面设置(U)..","设置页面格式.")
        printL = fileM.Append(wx.NewId(),"打印(P)\tCtrl+P","打印页面.")
        fileM.AppendSeparator()
        qit = fileM.Append(wx.NewId(),"退出(X)","关闭所有打开的文件.")

        #Bind(self,id,event function,obj)
        self.Bind(wx.EVT_MENU, self.OnNewFile, newF)
        self.Bind(wx.EVT_MENU, self.OnOpen, fmitem)
        self.Bind(wx.EVT_MENU, self.OnSave, save)
        self.Bind(wx.EVT_MENU, self.OnQuit, qit)


        #编辑
        editM = wx.Menu()
        editM.Append(wx.NewId(),"撤消(U)\tCtrl+Z","撤销最后的操作.")
        editM.AppendSeparator()
        editM.Append(wx.NewId(),"剪切(U)\tCtrl+X","剪切.")
        editM.Append(wx.NewId(),"复制(T)\tCtrl+C","复制.")
        editM.Append(wx.NewId(),"粘贴(C)\tCtrl+V","粘贴.")
        editM.Append(wx.NewId(),"删除(P)\tDel","删除.")
        editM.AppendSeparator()
        editM.Append(wx.NewId(),"查找(F)\tCtrl+F","查找.")
        editM.Append(wx.NewId(),"查找下一个(N)\tF3","查找下一个.")
        editM.Append(wx.NewId(),"删除(P)\tDel","删除.")
        editM.Append(wx.NewId(),"替换(R)\tCtrl+H","替换.")
        editM.Append(wx.NewId(),"转到(G)\tCtrl+G","转到.")
        editM.AppendSeparator()
        self.selectA = editM.Append(wx.NewId(),"全选(A)\tCtrl+A","全选.")

        self.Bind(wx.EVT_MENU, self.OnSelectAll, self.selectA)

        editM.Append(wx.NewId(),"时间/日期(D)\tF5","时间.")
        #格式[O]
        posM = wx.Menu()
        self.autoCutoverLine = self.newline = posM.Append(wx.NewId(),"自动换行(W)","自动换行.",kind=wx.ITEM_CHECK)

        self.Bind(wx.EVT_MENU, self.autoCutoverL, self.autoCutoverLine)

        self.showToolStatus = 0;
        posM.Append(wx.NewId(),"字体(F)..","设置字体.")
        #查看[V]
        viewM = wx.Menu()
        viewM.Append(wx.NewId(),"状态栏","状态栏.")
        self.tool=viewM.Append(wx.NewId(),"工具栏","工具栏",kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, self.tool)
        #帮助[H]
        helpM = wx.Menu()
        helpM.Append(wx.NewId(),"查看帮助(H)","查看帮助.")
        about = helpM.Append(wx.NewId(),"关于记事本(A)","关于记事本.")
        self.Bind(wx.EVT_MENU, self.OnAbout, about)
        #create a menuBar
        menuB = wx.MenuBar()
        # append a menu
        menuB.Append(fileM,"文件(F)")
        menuB.Append(editM,"编辑(E)")
        menuB.Append(posM,"格式[O]")
        menuB.Append(viewM,"查看[V]")
        menuB.Append(helpM,"帮助[H]")
        return menuB

    def autoCutoverL(self,event):
        print "hell"
        #设置字体颜色
        #self.control.SetForegroundColour("#F0FFF0")
        self.control.SetStyle(-1,-1,wx.TextAttr("wx.TE_WORDWRAP"))

    def OnSelectAll(self,event):
            self.control.SelectAll()

    def OnKeyDown(self,event):
        #按键时相应代码
        # Alt + F
        key = event.GetKeyCode();
        if key == ord('f'):
            self.fileM.Show()
        else:
            self.control.AppendText(chr(key))

    #是否显示工具栏
    def ToggleToolBar(self,event):
        self.showToolStatus+=1;
        #if self.newline.IsChecked():
        if self.showToolStatus % 2 == 1:
            print 1111
            self.control.SetInsertionPoint(50)
            self.tb.Show()
        else:
            print 2222
            self.tb.Hide()


    #新建文件
    def OnNewFile(self,event):
        if self.control.IsEmpty() <> True:
            dlg = wx.MessageDialog(self, "是否将更改保存到无标题?","记事本",wx.YES_NO | wx.ICON_QUESTION | wx.CANCEL)
            retCode = dlg.ShowModal()
            if retCode == wx.ID_YES:
                # 保存
                self.OnSave(event)
                # 保存完后，创建新文件
                self.control.SetValue("")
            elif retCode == wx.ID_NO:
                # 清空
                self.control.SetValue("")
            else:
                # 取消
                dlg.Close();

            dlg.Destroy()

    #保存
    def OnSave(self,event):
        #判断是否有内容
        if self.control.IsEmpty():
            return;
        self.dirname=''
        """ wx.FD_OPEN
            wx.FD_SAVE
            wx.FD_OVERWRITE_PROMPT
            wx.FD_MULTIPLE
            wx.FD_CHANGE_DIR """
        dlg = wx.FileDialog(self,"choose a file",self.dirname,"","*.*",wx.FD_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'w')
            f.write(self.control.GetValue());
            f.close()
        dlg.Destroy()
        # 重新设置记事本的Title
        self.Title  = self.filename + " - 记事本"

    #打开选择文件的dialog
    def OnOpen(self,event):
        print self.control.GetValue()
        self.dirname=''
        self.dirname=''
        """ wx.FD_OPEN
            wx.FD_SAVE
            wx.FD_OVERWRITE_PROMPT
            wx.FD_MULTIPLE
            wx.FD_CHANGE_DIR """
        dlg = wx.FileDialog(self,"choose a file",self.dirname,"","*.*",wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()
        self.control.SetFocus()
        wx.StaticText(self.sbar, label=self.filename + ","+ str(self.control.GetNumberOfLines()) + " 行",pos=(0,1))

    # 退出
    def OnQuit(self,event):
        self.Close()

    # 关于
    def OnAbout(self,event):
        dlg = wx.MessageDialog(self, "hello,baby","title is a baby",wx.OK)
        dlg.ShowModal()
        self.control.SelectAll();
        dlg.Destroy()

    def OnHello(self, event):
        pass

    #创建按钮
    def createButtonBar(self, panel, yPos = 10):
            xPos = 0
            for eachLabel, eachHandler in self.buttonData():
                    pos = (xPos, yPos)
                    button = self.buildOneButton(panel, eachLabel,eachHandler, pos)
                    xPos += button.GetSize().width

    def buildOneButton(self, parent, label, handler, pos=(0,0)):
        button = wx.Button(parent, -1, label, pos)
        self.Bind(wx.EVT_BUTTON, handler, button)
        return button

    #get md5
    @staticmethod
    def GetMd5(content):
        #md5 = hashlib.md5() #创建一个MD5加密对象
        #md5.update(content)  #更新要加密的数据
        #return md5.digest();  #加密后的结果（二进制）
        #print md5.hexdigest() #加密后的结果，用十六进制字符串表示。
        return hashlib.new("md5", content).hexdigest()

if __name__=="__main__":
    app = wx.App(False)
    frame = NotBookMainFrame(None,"无标题 - 记事本")
    app.MainLoop()