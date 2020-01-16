#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
from unit import id as uid


class ClientUpdatePageSW(wx.SplitterWindow):
    def __init__(self, parent=None):
        super(ClientUpdatePageSW, self).__init__(parent=parent, id=uid.CLIENT_UPDATE_PAGE_SW, style=wx.SP_NOBORDER,
                                            size=parent.GetSize())
        self.parent = parent

    # TODO: 添加子界面
    def __settings__(self):
        pass


if __name__ == '__main__':
    pass
