# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui

###########################################################################
## Class MyFrame2
###########################################################################

class MyFrame2 ( wx.Frame ):

	def __init__( self, parent=None ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 819,474 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menu11 = wx.Menu()
		self.m_menuItem1 = wx.MenuItem( self.m_menu11, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu11.AppendItem( self.m_menuItem1 )

		self.m_menu1.AppendSubMenu( self.m_menu11, u"MyMenu" )

		self.m_menu21 = wx.Menu()
		self.m_menuItem2 = wx.MenuItem( self.m_menu21, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu21.AppendItem( self.m_menuItem2 )

		self.m_menu1.AppendSubMenu( self.m_menu21, u"MyMenu" )

		self.m_menubar1.Append( self.m_menu1, u"文件(&F)" )

		self.m_menu2 = wx.Menu()
		self.m_menubar1.Append( self.m_menu2, u"编辑(&E)" )

		self.m_menu3 = wx.Menu()
		self.m_menubar1.Append( self.m_menu3, u"格式(&O)" )

		self.m_menu4 = wx.Menu()
		self.m_menubar1.Append( self.m_menu4, u"查看(&V)" )

		self.m_menu5 = wx.Menu()
		self.m_menubar1.Append( self.m_menu5, u"帮助(&H)" )

		self.SetMenuBar( self.m_menubar1 )

		gbSizer1 = wx.GridBagSizer( 0, 0 )
		gbSizer1.SetFlexibleDirection( wx.BOTH )
		gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_auiToolBar2 = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT )
		self.m_tool6 = self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"../save_16.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_tool7 = self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"../clear.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_tool8 = self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"../left.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_tool9 = self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"../center.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_tool10 = self.m_auiToolBar2.AddTool( wx.ID_ANY, u"tool", wx.Bitmap( u"../right.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_auiToolBar2.Realize()

		gbSizer1.Add( self.m_auiToolBar2, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )


		self.SetSizer( gbSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


# TODO: App创建
class NewApp(wx.App):
    def OnInit(self):
        window = MyFrame2()
        window.Show()
        # 返回 False则退出
        return True


if __name__ == '__main__':
    app = NewApp()
    app.MainLoop()