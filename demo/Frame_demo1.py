#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: Frame_demo1.py

@time: 2018/6/21 17:08

@module:python -m pip install wxpython

@desc:
'''
import wx


class myFrame(wx.Frame):
    def __init__(self):
        super(myFrame, self).__init__(parent=None, id=-1, title='first wx prj', pos=(0, 0), size=(300, 400),
                                      style=wx.DEFAULT_FRAME_STYLE, name='topFrame')
        self.SetTitle('test')

        self.Center()
        self.SetSize(300, 400)
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        self.SetName('topFrame')

        self.SetFont(wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL))


if __name__ == '__main__':
    app = wx.App()
    windows = myFrame()
    windows.Show()
    app.MainLoop()
