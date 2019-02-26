#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: main.py

@time: 2018/5/13 13:27

@module:python -m pip install 

@desc:
'''

import tkinter as tk
from settings import MainPage
from calculator import Calculator


def main():
    root = tk.Tk()
    root.attributes("-alpha", MainPage.alpha)
    root.geometry('{width}x{height}'.format(width=MainPage.width, height=MainPage.height))
    root.resizable(width=False, height=False)
    Calculator(root)
    root.mainloop()

if __name__ == '__main__':
    main()