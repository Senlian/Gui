#!/usr/bin/python
# -*- coding: utf-8 -*-
import wx
import os
import numpy as np
import sys, csv
import wx.grid
from csvdemo1 import MyFrame3, csv_view


class MyFrame(MyFrame3):
    def __init__(self, parent, size=wx.Size(900, 600)):
        super(MyFrame,self).__init__(parent)
        self.dirname = os.getcwd()

    # Import/Open CSV
    def ImportFunc(self, event):
        '''THIS IMPORTED CSV WILL NEVER EXPAND TO FIT INTO THE FRAME, PLEASE HELP?'''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', 'CSV files (*.csv)|*.csv|All files(*.*)|*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetDirectory()
        self.filename = os.path.join(self.dirname, dlg.GetFilename())
        self.file = file(self.filename, 'r')
        # check for file format with sniffer
        dialect = csv.Sniffer().sniff(self.file.read(1024))
        self.file.seek(0)
        csvfile = csv.reader(self.file, dialect)
        filedata = []  # put contents of csvfile into a list
        filedata.extend(csvfile)
        self.file.seek(0)
        # grab a sample and see if there is a header
        sample = self.file.read(2048)
        self.file.seek(0)
        if csv.Sniffer().has_header(sample):  # if there is a header
            colnames = csvfile.next()  # label columns from first line
            datalist = []  # create a list without the header
            datalist.extend(filedata[1:len(filedata)])  # append data without header
        else:
            row1 = csvfile.next()  # if there is NO header
            colnames = []
            for i in range(len(row1)):
                colnames.append('col_%d' % i)  # label columns as col_1, col_2, etc
        self.file.seek(0)
        datalist = filedata  # append data to datalist
        self.file.close()
        self.createGrid(datalist, colnames)

    # create the grid
    def createGrid(self, datalist, colnames):
        if getattr(self, 'grid', 0):
            self.grid.Destroy()
        self.grid = wx.grid.Grid(self, -1)
        self.grid.CreateGrid(len(datalist), len(colnames))  # create grid, same size as file (rows, cols)
        # fill in headings
        for i in range(len(colnames)):
            self.grid.SetColLabelValue(i, colnames[i])
        # populate the grid
        for row in range(len(datalist)):
            for col in range(len(colnames)):
                try:
                    self.grid.SetCellValue(row, col, datalist[row][col])
                except:
                    pass
        self.grid.AutoSizeColumns(False)  # size columns to data (from cvsomatic.py)
        self.twiddle()

    def twiddle(self):  # from http://www.velocityreviews.com/forums/t330788-how-to-update-window-after-wxgrid-is-updated.html
        x, y = self.GetSize()
        self.SetSize((x, y + 1))
        self.SetSize((x, y))

    def Exit(self, event):
        if getattr(self, 'file', 0):
            self.file.close()
            self.Close(True)


# class csv_view(wx.App):
# def OnInit(self):
# self.frame=MyFrame(None, -1, 'show CSV', size=(900,600))
# self.SetTopWindow(self.frame)
# return True
# app=csv_view()
# app.MainLoop()
app = wx.App(0)
Frame_02 = MyFrame(None)
Frame_02.Show()
app.MainLoop()
