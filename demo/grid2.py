#!/usr/bin/env python
# encoding: utf8
import wx
import wx.grid as gridlib


# import wx.lib.mixins.grid as mixins

# ---------------------------------------------------------------------------

class SimpleGrid(gridlib.Grid):  ##, mixins.GridAutoEditMixin):
    def __init__(self, parent, log):
        gridlib.Grid.__init__(self, parent, -1)
        ##mixins.GridAutoEditMixin.__init__(self)
        # 打印log信息
        self.log = log
        self.moveTo = None

        self.Bind(wx.EVT_IDLE, self.OnIdle)
        # 创建一个25X25的电子表格
        self.CreateGrid(25, 25)  # , gridlib.Grid.SelectRows)
        ##self.EnableEditing(False)

        # simple cell formatting
        # 设置第index=3列的宽度大小，像素=200
        self.SetColSize(col=3, width=200)
        # 设置第index=4行的高度大小，像素=45
        self.SetRowSize(4, 45)
        # 设置 row=0,col=0,value="First cell"
        self.SetCellValue(0, 0, "First cell")
        # 设置 row=1,col=1,value="Another cell"
        self.SetCellValue(1, 1, "Another cell")
        # 设置 row=2,col=2,value="Yet another cell"
        self.SetCellValue(2, 2, "Yet another cell")
        # 设置 row=3,col=3,value="This cell is read-only"
        self.SetCellValue(3, 3, "This cell is read-only")
        # 设置字体格式
        self.SetCellFont(0, 0, wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        # 设置字体颜色
        self.SetCellTextColour(1, 1, wx.RED)
        # 设置cell背景颜色
        self.SetCellBackgroundColour(2, 2, wx.CYAN)
        # 设置只读属性
        self.SetReadOnly(3, 3, True)
        # 设置 row=5,col=0,数字编辑器
        self.SetCellEditor(5, 0, gridlib.GridCellNumberEditor(1, 1000))
        # 设置 row=5,col=0,value="123"
        self.SetCellValue(5, 0, "123")
        # 设置 row=6,col=0,浮点数
        self.SetCellEditor(6, 0, gridlib.GridCellFloatEditor())
        # 设置 row=6,col=0,value="123.34"
        self.SetCellValue(6, 0, "123.34")
        # 设置
        self.SetCellEditor(7, 0, gridlib.GridCellNumberEditor())
        # 设置 row=6,col=3,value="You can veto editing this cell"
        self.SetCellValue(6, 3, "You can veto editing this cell")

        # self.SetRowLabelSize(0)
        # self.SetColLabelSize(0)

        # attribute objects let you keep a set of formatting values
        # in one spot, and reuse them if needed
        # wx.grid.GridCellAttr

        # 这个类可以用来通过改变它们的默认属性来改变网格在网格中的外观。
        attr = gridlib.GridCellAttr()
        # 字体颜色：黑色
        attr.SetTextColour(wx.BLACK)
        # 设置背景颜色：红色
        attr.SetBackgroundColour(wx.RED)
        # 设置字体格式
        attr.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # you can set cell attributes for the whole row (or column)
        # 设置Row=5,attr
        self.SetRowAttr(5, attr)

        # 设置Col=0,LableValue =Custom
        self.SetColLabelValue(0, "Custom")
        # 设置Col=1,LabelValue = "column"
        self.SetColLabelValue(1, "column")
        # 设置Col=2,LabelValue = labels
        self.SetColLabelValue(2, "labels")
        # 设置列表标签左右以及上下对齐方式：左对齐，下沉
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)

        # self.SetDefaultCellOverflow(False)
        # r = gridlib.GridCellAutoWrapStringRenderer()
        # self.SetCellRenderer(9, 1, r)

        # overflow cells
        self.SetCellValue(9, 1,
                          "This default cell will overflow into neighboring cells, but not if you turn overflow off.");
        # 单元格合并处理：3x3
        self.SetCellSize(11, 1, 3, 3);
        # 设置单元格对齐方式：中间，中间
        self.SetCellAlignment(11, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE);
        # 设置单元格值
        self.SetCellValue(11, 1, "This cell is set to span 3 rows and 3 columns");

        # 设置
        editor = gridlib.GridCellTextEditor()
        # 值长度
        editor.SetParameters('10')
        # 设置格式
        self.SetCellEditor(0, 4, editor)
        # 设置值
        self.SetCellValue(0, 4, "Limited text")

        # 可以用来格式化单元格中的字符串数据。
        renderer = gridlib.GridCellAutoWrapStringRenderer()
        self.SetCellRenderer(15, 0, renderer)
        self.SetCellValue(15, 0, "The text in this cell will be rendered with word-wrapping")

        # test all the events
        # 左单击
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        # 右单击
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        # 左双击
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        # 右双击
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)

        # label 左单击
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        # label 右单击
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        # label 左双击
        self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
        # label 右双击
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)

        self.Bind(gridlib.EVT_GRID_COL_SORT, self.OnGridColSort)

        # 拖动Row大小
        self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
        # 拖动Col大小
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)

        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)

        self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
        self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)

    def OnCellLeftClick(self, evt):
        self.log.write("OnCellLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightClick(self, evt):
        self.log.write("OnCellRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellLeftDClick(self, evt):
        self.log.write("OnCellLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnCellRightDClick(self, evt):
        self.log.write("OnCellRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelRightClick(self, evt):
        self.log.write("OnLabelRightClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelLeftDClick(self, evt):
        self.log.write("OnLabelLeftDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnLabelRightDClick(self, evt):
        self.log.write("OnLabelRightDClick: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnGridColSort(self, evt):
        self.log.write("OnGridColSort: %s %s" % (evt.GetCol(), self.GetSortingColumn()))
        self.SetSortingColumn(evt.GetCol())

    def OnRowSize(self, evt):
        self.log.write("OnRowSize: row %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnColSize(self, evt):
        self.log.write("OnColSize: col %d, %s\n" %
                       (evt.GetRowOrCol(), evt.GetPosition()))
        evt.Skip()

    def OnRangeSelect(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        self.log.write("OnRangeSelect: %s  top-left %s, bottom-right %s\n" %
                       (msg, evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))
        evt.Skip()

    def OnCellChange(self, evt):
        self.log.write("OnCellChange: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Show how to stay in a cell that has bad data.  We can't just
        # call SetGridCursor here since we are nested inside one so it
        # won't have any effect.  Instead, set coordinates to move to in
        # idle time.
        value = self.GetCellValue(evt.GetRow(), evt.GetCol())

        if value == 'no good':
            self.moveTo = evt.GetRow(), evt.GetCol()

    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None

        evt.Skip()

    def OnSelectCell(self, evt):
        if evt.Selecting():
            msg = 'Selected'
        else:
            msg = 'Deselected'
        self.log.write("OnSelectCell: %s (%d,%d) %s\n" %
                       (msg, evt.GetRow(), evt.GetCol(), evt.GetPosition()))

        # Another way to stay in a cell that has a bad value...
        row = self.GetGridCursorRow()
        col = self.GetGridCursorCol()

        if self.IsCellEditControlEnabled():
            self.HideCellEditControl()
            self.DisableCellEditControl()

        value = self.GetCellValue(row, col)

        if value == 'no good 2':
            return  # cancels the cell selection

        evt.Skip()

    def OnEditorShown(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
                        wx.MessageBox("Are you sure you wish to edit this cell?",
                                      "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        self.log.write("OnEditorShown: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnEditorHidden(self, evt):
        if evt.GetRow() == 6 and evt.GetCol() == 3 and \
                        wx.MessageBox("Are you sure you wish to  finish editing this cell?",
                                      "Checking", wx.YES_NO) == wx.NO:
            evt.Veto()
            return

        self.log.write("OnEditorHidden: (%d,%d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
        evt.Skip()

    def OnEditorCreated(self, evt):
        self.log.write("OnEditorCreated: (%d, %d) %s\n" %
                       (evt.GetRow(), evt.GetCol(), evt.GetControl()))


# ---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Simple Grid Demo", size=(640, 640))
        self.grid = SimpleGrid(self, log)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    print("hhh!!!")
    sys.stdout.write("hll" + "\n")
    if (0):  # this section is modified by tony
        from wx.lib.mixins.inspection import InspectableApp

        app = InspectableApp(False)
    else:
        app = wx.App(False)
    frame = TestFrame(None, sys.stdout)
    if (0):  # this section is modified by tony
        print(sys.stdout)
        print(type(sys.stdout))
    frame.Show(True)
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
