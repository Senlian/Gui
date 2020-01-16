#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import wx
from unit import id as uid


# TODO: 状态栏
class StatusBar(wx.StatusBar):
    def __init__(self, parent=None, id=uid.STATUSBAR):
        super(StatusBar, self).__init__(parent=parent, id=id, style=65840, name=u'状态栏')
        self.SetFieldsCount(3)
        self.SetStatusWidths([-2, -2, -1])
        self.Show()




if __name__ == '__main__':
    pass
