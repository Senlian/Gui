#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: main.py

@time: 2018/5/9 20:00

@module:python -m pip install 

@desc:
'''

import tkinter as tk
from CalculatorPage import Calculator


def main():
    root = tk.Tk()
    root.attributes("-alpha", 0.95)
    Calculator(root)
    # root.bind('<Any-KeyPress>', press)

    root.mainloop()


def press(event):
    # bracketleft
    # bracketright
    print(event.char)
    # print(event.keysym)
    # print(event.keycode)
    # print(event.keysym_num)
    print(event)


if __name__ == '__main__':
    main()
    # import re
    # str = '3+2-5*3+(2+5)+6*9/2+(1%2+6-7)'
    # print(re.findall(r'.*(\(.*\)).*', str))