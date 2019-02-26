#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: settings.py

@time: 2018/5/8 21:58

@module:python -m pip install

@desc:
'''
# TODO:主窗体信息
WINDOW_TITLE = "隐私相册"

# TODO:主窗体尺寸设置
# 宽度
WINDOW_X = 420
# 是否可调节宽度
RESIZE_X = True
# 可调节最大宽度
WINDOW_MAX_X = int(WINDOW_X * 2)
# 可调节最小宽度
WINDOW_MIN_X = int(WINDOW_X * 0.5)

# 高度
WINDOW_Y = int(WINDOW_X / 0.618)
# 是否可调节高度
RESIZE_Y = True
# 最大高度
WINDOW_MAX_Y = int(WINDOW_MAX_X / 0.618)
# 最小高度
WINDOW_MIN_Y = int(WINDOW_MIN_X / 0.618)
MARK_LIST = {
    '8': 'BackSpace',
    '13': '=',
    '32': '=',
    '46': 'clear',
    '67': 'clear',
    '110': '.',
    '111': '÷',
    '187': '=',
    '190': '.',
    '191': '÷',
    '192': 'swith',
    '106': '×',
    '219': '(',
    '220': '%',
    '221': ')',
    '+': '+',
    '-': '-',
    '×': '×',
    '÷': '÷',
    '﹪': '%',
    '.': '.',
    '=': '=',
    '√': 'sqrt',
    'χ²': 'square',
    'χ³': 'cube',
    '±': 'swith',
    '←': 'BackSpace',
    'C': 'clear',
    '(': '(',
    ')': ')'
}

SYBOL_LIST = {
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

import re
import math
from decimal import Decimal
pattern = re.compile('^[-+]?\d+[\.\d]*$')
patternExpression = re.compile('^[\+\-\*\/\.\(\)(sqrt)(cube)(square)(swith)0123456789]+$')


# 数字格式化
def formate_number(item):
    if item == '-':
        return str(0)
    item = str(re.sub(r"^([\+\-]*)0*([1-9][0-9]*|0)$", r"\1\2", str(item)))

    itemSplit = item.split('.')

    if len(itemSplit) == 2 and itemSplit[1] and int(eval(formate_number(itemSplit[1]))) == 0:
        return str(itemSplit[0])
    try:
        return str(eval(item))
    except:
        return str(0)


# ±，正负转换
def swith(item):
    item = pre_eval(item)
    if pattern.findall(item):
        item = formate_number(item)
        if eval(item) > 0:
            return formate_number(eval('-' + str(item)))
        else:
            return formate_number(item[1:])
    else:
        return item


# χ²，平方
def square(item):
    item = pre_eval(item)
    if pattern.findall(item):
        item = formate_number(item)
        return formate_number(str(math.pow(eval(item), 2)))
    else:
        return item


# χ³，立方
def cube(item):
    item = pre_eval(item)
    if pattern.findall(item):
        item = formate_number(item)
        return formate_number(str(math.pow(eval(item), 3)))
    else:
        return item


# 根号
def sqrt(item):
    item = pre_eval(item)
    if pattern.findall(item):
        item = formate_number(item)
        if eval(item) < 0:
            return formate_number(item)
        return str(formate_number(math.sqrt(eval(item))))
    else:
        return str(item)



def BackSpace(item):
    return str(item)[0:-1] or '0'


def bracket(item):
    pass


# 表达式计算
def pre_eval(item):
    item = str(item)
    if patternExpression.findall(item):
        return formate_number(eval(item))
    else:
        return item

def remath(pattern):
    s = pattern.group(r'float')
    return "Decimal('{0}')".format(s)

def floatEval(item):
    item = str(re.sub(r'(?P<float>(\d+\.\d+))', remath, str(item)))
    return str(eval(item))


