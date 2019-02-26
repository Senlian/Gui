import wx
from win32com.shell import shell, shellcon
from win32con import FILE_ATTRIBUTE_NORMAL
def extension_to_bitmap(extension):
    """dot is mandatory in extension"""
 
    flags = shellcon.SHGFI_SMALLICON | \
            shellcon.SHGFI_ICON | \
            shellcon.SHGFI_USEFILEATTRIBUTES
    retval, info = shell.SHGetFileInfo(extension,
                             FILE_ATTRIBUTE_NORMAL,
                             flags)
    # non-zero on success
    assert retval
    hicon, iicon, attr, display_name, type_name = info
    # Get the bitmap
    icon = wx.EmptyIcon()
    icon.SetHandle(hicon)
    return wx.BitmapFromIcon(icon)

extension_to_bitmap('./img/close.png')