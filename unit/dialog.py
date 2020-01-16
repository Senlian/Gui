#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
from config import settings


# TODO: 消息对话框
class DialogBox(wx.MessageDialog):
    def __init__(self, parent=None):
        self.parent = parent

    def info(self, msg="页面加载中...", style=wx.ICON_INFORMATION, **kwargs):
        super(DialogBox, self).__init__(parent=self.parent, message=msg,
                                        caption=kwargs.get('caption') or "提示", style=style)
        return self.ShowModal()

    def warn(self, msg="确认要继续操作吗?", style=wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION, **kwargs):
        super(DialogBox, self).__init__(parent=self.parent, message=msg,
                                        caption=kwargs.get('caption') or "警告", style=style)
        return self.ShowModal()

    def error(self, msg="操作失败,请排查原因！", style=wx.OK | wx.CANCEL | wx.ICON_ERROR, **kwargs):
        super(DialogBox, self).__init__(parent=self.parent, message=msg,
                                        caption=kwargs.get('caption') or "错误", style=style)
        return self.ShowModal()

    def danger(self, msg="操作存在风险，请谨慎操作!", style=wx.OK | wx.CANCEL | wx.ICON_AUTH_NEEDED, **kwargs):
        super(DialogBox, self).__init__(parent=self.parent, message=msg,
                                        caption=kwargs.get('caption') or "危险", style=style)
        return self.ShowModal()

    def msg(self, msg=None, style=wx.OK | wx.ICON_NONE, **kwargs):
        if not msg:
            msg = "          作者：SenLian\n    当前版本：20200116.1\nPython版本：3.7.5"
        super(DialogBox, self).__init__(parent=self.parent, message=msg,
                                        caption=kwargs.get('caption') or "版本信息", style=style)
        return self.ShowModal()


# TODO: 获取文件夹路径
def DirDialog(parent=None, message=u"打开路径", defaultPath=None):
    if not parent:
        return
    dl = wx.DirDialog(parent=parent, message=message, defaultPath=defaultPath, style=wx.DD_DEFAULT_STYLE)
    targetPath = defaultPath if dl.ShowModal() != wx.ID_OK else dl.GetPath()
    dl.Destroy()
    return targetPath


# TODO: 获取文件路径
def FileDialog(parent=None, message=u"另存为", defaultDir=None, defaultFile=None, wildcard=None):
    if not parent:
        return
    if not defaultDir:
        defaultDir = defaultFile
    wildcard = wildcard if wildcard else settings.WILDCARD
    dl = wx.FileDialog(parent=parent, message=message, defaultDir=defaultDir, defaultFile=defaultFile,
                       wildcard=wildcard, style=wx.FD_OPEN)
    targetFile = defaultFile if dl.ShowModal() != wx.ID_OK else dl.GetPath()
    dl.Destroy()
    return targetFile


if __name__ == '__main__':
    pass
