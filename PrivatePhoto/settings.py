#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: settings.py

@time: 2018/5/13 13:36

@module:python -m pip install 

@desc:
'''


class Public():
    pass


class MainPage():
    width = 360
    height = int(width / 0.618)

    alpha = 0.95


class KeyBoar():
    KeyTable = {
        # 0043,+
        '+': 'plus',
        # 0045,-
        '-': 'minus',
        # 41409,*
        '×': 'asterisk',
        # 41410,/
        '÷': 'slash',
        # 43399,\
        '﹪': 'backslash',
        # 0046
        '.': 'period',
        # 0061
        '=': ['equal', 'Return', 'space'],
        # 41420
        '√': 'sqrt',
        # 42710 178
        'χ²': 'square',
        # 42170 179
        'χ³': 'cube',
        # 41408,~
        '±': 'quoteleft',
        # 41467
        '←': 'BackSpace',
        # clear, C
        'C': ['Delete', 'C', 'c'],
        # 40
        '(': 'bracketleft',
        # 41
        ')': 'bracketright'
    }

    markTable = {
        '+': '+',
        '-': '-',
        '×': '*',
        '÷': '/',
        '﹪': '%',
        '.': '.',
        '=': '=',
        '√': 'sqrt',
        'χ²': 'square',
        'χ³': 'cube',
        '±': 'switch',
        '←': 'BackSpace',
        'C': 'clear',
        '(': '(',
        ')': ')'
    }
import math
def sqrt(item):
    return math.sqrt(item)