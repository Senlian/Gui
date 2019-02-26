#!/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: CalculatorPage.py

@time: 2018/5/9 20:00

@module:python -m pip install 

@desc:
'''
import tkinter as tk
from settings import *
import math
import time
from decimal import Decimal


class Calculator(object):
    def __init__(self, master):
        self.root = master
        self.root.title("计算器")
        self.root.geometry('{width}x{height}'.format(width=360, height=int(360 / 0.618)))
        self.root.update()
        self.root.pack_propagate(0)

        # 输入及结果展示
        self.outStr = tk.StringVar()
        # 字符串长度
        self.fontLimiteLen = 18
        # 表达式及错误信息展示
        self.eStr = tk.StringVar()
        self.eStrTemp = ''
        # 真实表达式
        self.tStr = ''
        # 数字键颜色
        self.keyColor = tk.StringVar()
        self.keyColor.set('white')
        # 数字键状态
        self.keyState = tk.StringVar()
        self.keyState.set('normal')
        # 当前符号存储
        self.symbol = ''
        # 上次符号存储
        self.lastSymbol = ''
        # 无键盘事件按钮
        self.no_keybord = ['√', 'χ²', 'χ³']
        self.ifPress = False
        # 计算页面
        self.calculatorPage = self.createPage()

    # TODO： 计算器框架
    def createPage(self):
        keyboardFrame = tk.Frame(self.root)
        keyboardFrame['width'] = self.root.winfo_width()
        keyboardFrame['height'] = self.root.winfo_height()
        keyboardFrame.pack()
        keyboardFrame.update()

        lable1 = self.addScreen(keyboardFrame, 14, self.eStr)
        lable2 = self.addScreen(keyboardFrame, 28, self.outStr)
        self.fontLimiteLen = int(keyboardFrame.winfo_width() / 28 * 2)
        numberFrame = tk.Frame(keyboardFrame)
        numberFrame['borderwidth'] = 9
        numberFrame.focus_set()
        numberFrame.pack()
        numberFrame.update()

        # TODO: 第一行
        for index, symbol in enumerate(['C', '﹪', '√', 'χ²']):
            self.addButton(numberFrame, symbol, 0, index)
        # TODO: 第二行
        for index, symbol in enumerate(['←', '(', ')']):
            self.addButton(numberFrame, symbol, 1, index)
        # TODO: 第四列
        for index, symbol in enumerate(['÷', '×', '-', '+']):
            self.addButton(numberFrame, symbol, index + 1, 3)
        # TODO: 数字键盘
        for number in range(9, -1, -1):
            row = (5 if number == 0 else (2 if (number / 3) > 2 else(3 if (number / 3) > 1 else 4)))
            column = (1 if number == 0 else int((number - 1) % 3))
            self.addButton(numberFrame, number, row, column, bg=self.keyColor.get(), state=self.keyState.get())
        # TODO: 第五行
        self.addButton(numberFrame, '±', 5, 0)
        self.addButton(numberFrame, '.', 5, 2)
        self.addButton(numberFrame, '=', 5, 3)
        # self.addButton(numberFrame, 'π', 6, 0, 1)



        return keyboardFrame

    # TODO: 添加显示屏
    def addScreen(self, father, fontsize=28, msg=None):
        self.outStr.set('0')
        newLable = tk.Label(father)
        newLable['width'] = father.winfo_width()
        newLable['height'] = 2
        newLable['borderwidth'] = 8
        newLable['background'] = '#E0E0E0'
        newLable['foreground'] = 'black'
        newLable['anchor'] = 'se'
        newLable['font'] = ('Times New Roman', fontsize, 'bold')
        newLable['textvariable'] = msg
        newLable['wraplength'] = father.winfo_width()
        newLable['justify'] = 'right'
        newLable.pack()
        return newLable

    # TODO: 添加按钮
    def addButton(self, father, text='0', row=0, column=0, columnspan=1, width=4, bg='#F0F0F0', state='normal'):
        newButton = tk.Button(father)
        newButton['anchor'] = 'center'
        newButton['background'] = bg
        newButton['borderwidth'] = 2
        newButton['width'] = width
        newButton['height'] = 1

        newButton['state'] = state
        newButton['text'] = text
        newButton['padx'] = 1
        newButton['pady'] = 3
        newButton['font'] = ('Times New Roman', '24', 'bold')
        newButton['foreground'] = 'black'
        newButton['activeforeground'] = 'red'

        newButton['command'] = lambda: self.clickPress(father, newButton)
        color = 'lightgray' if bg == 'white' else 'skyblue'

        newButton.bind('<ButtonPress-1>', lambda e: self.keyPress(e, newButton, color))
        newButton.bind('<ButtonRelease-1>', lambda e: self.keyPress(e, newButton, bg))
        bindEvents = SYBOL_LIST.get(text, str(text))
        if (type(bindEvents) == str):
            bindEvents = [bindEvents]
        if text not in self.no_keybord:
            for event in bindEvents:
                pressEvent = '<KeyPress-' + str(event) + '>'
                releaseEvent = '<KeyRelease-' + str(event) + '>'
                # newButton.bind_all(pressEvent, lambda e: self.keyPress(e, newButton, color))
                newButton.bind_all(pressEvent, lambda e: self.keyPress(e, newButton, color) if newButton[
                                                                                                   'text'] != '←' else self.keyRelease(
                        e, newButton, bg))
                newButton.bind_all(releaseEvent, lambda e: self.keyRelease(e, newButton, bg) if newButton[
                                                                                                    'text'] != '←' else self.keyPress(
                        e, newButton, bg))
                # newButton.bind_all(releaseEvent, lambda e: self.keyRelease(e, newButton, bg))
        newButton.grid(row=int(row), column=int(column), columnspan=columnspan)

        return newButton

    # TODO: 释放按键
    def keyRelease(self, event, btn, color):
        code = event.keycode
        char = MARK_LIST.get(str(code), event.char)
        btn['bg'] = color
        self.inputHandler(char)

    # TODO: 键盘按下
    def keyPress(self, event, btn, color):
        btn['bg'] = color
        btn.update()

    # TODO: 鼠标点击
    def clickPress(self, father, btn):
        # length = int(father.winfo_width() / int(btn['font'].split()[3]))
        if str(btn['text']).isdigit():
            inputStr = str(btn['text'])
        else:
            inputStr = MARK_LIST.get(str(btn['text']), str(btn['text']))
        self.inputHandler(inputStr)

    def setOutput(self, inpustr):
        if len(inpustr) > self.fontLimiteLen or (
                    (not inpustr.startswith('%')) and (eval(inpustr) > int('9' * self.fontLimiteLen))):
            self.eStr.set('溢出')
            self.symbol = ''
            self.lastSymbol = ''
            self.tStr = ''
            self.eStrTemp = '0'
            return
        self.outStr.set(inpustr)

    def inputHandler(self, inputStr=''):
        if not inputStr:
            return
        if inputStr in MARK_LIST.values():
            # print(inputStr)
            if inputStr in ['sqrt', 'square', 'swith', 'BackSpace', 'clear', '(', ')', '=', '.']:
                self.markHandler(inputStr)
                return
            else:
                self.mathHandler(inputStr)
            pass
        else:
            # print(inputStr)
            self.numberHandler(inputStr)

    def numberHandler(self, number):
        # print(number, self.symbol)
        outStr = self.outStr.get()
        eStr = self.eStr.get() or '0'
        tStr = self.tStr
        # 还原表达式
        if self.eStrTemp and self.eStrTemp != '0' and self.symbol != 'e':
            self.eStr.set(self.eStrTemp)
            self.eStrTemp = ''
        if self.symbol == 'e':
            self.eStr.set('')
        # 如果没有输入过运算符
        if not (self.symbol or self.lastSymbol):
            self.eStr.set('')
            if outStr.startswith('%'):
                # 非密码开头
                if outStr == '%':
                    outStr = number
                # 密码样式开头
                else:
                    outStr += number
                    self.tStr = ''
                    self.eStr.set('')
            elif outStr == '0':
                outStr = number
            else:
                outStr += number

            self.setOutput(outStr)
            self.lastSymbol = '+'
        # 连续输入非运算符
        elif not self.symbol:
            if outStr in ['0', '%']:
                outStr = str(number)
                self.setOutput(outStr)
            elif outStr == '-' and str(number) == '0':
                return
            else:
                self.setOutput(outStr + str(number))
        else:
            if self.symbol == '÷' and number == '0':
                self.eStrTemp = self.eStr.get()
                self.eStr.set('除数不能为0')
                return
            else:
                self.setOutput(number)

        self.symbol = ''
        self.ifPress = True

    def formateExpression(self, item):
        item = str(item).replace('+', '+')
        item = item.replace('-', '-')
        item = item.replace('×', '*')
        item = item.replace('÷', '/')
        item = item.replace('%', '%')
        item = item.replace('√', 'sqrt')
        item = item.replace('²', '**2')
        print('-' * 30)
        print('item=', item)
        return floatEval(item)

    def mathHandler(self, fake):
        if self.eStrTemp and self.eStrTemp != '0':
            self.eStr.set(self.eStrTemp)
            self.eStrTemp = ''
        outStr = self.outStr.get() if fake == '%' else self.outStr.get()

        eStr = self.eStr.get()
        # 第一次输入
        if not eStr:
            if not self.ifPress:
                # 非密码样式，设置负号
                if not outStr.startswith('%'):
                    if fake in ['-', '%']:
                        self.outStr.set(fake)
                    else:
                        self.outStr.set('0')
                        self.symbol = fake
                    return
                # 密码样式
                else:
                    if outStr == '%' and fake != '%':
                        if fake == '-':
                            self.outStr.set(fake)
                        else:
                            self.outStr.set('0')
                            self.symbol = fake
                    else:
                        self.setOutput(outStr + fake)
                        self.symbol = ''
                    return
            else:
                if outStr.startswith('%'):
                    self.setOutput(outStr + fake)
                    self.symbol = ''
                    return
                else:
                    self.eStr.set(outStr + fake)
                    tStr = outStr
                    self.symbol = fake
        else:
            self.symbol = fake
            # 如果数字没有重新键入
            if not self.ifPress:
                tStr = eStr[0:-1] if self.lastSymbol else eStr
                self.eStr.set(tStr + fake)
            else:
                tStr = (eStr if self.lastSymbol else '') + outStr
                tStr = '(' + tStr + ')' if (fake in ['+', '-'] and self.lastSymbol not in ['+', '-']) else tStr
                self.eStr.set(tStr + fake)
        self.tStr = str(self.formateExpression(tStr))
        self.lastSymbol = fake
        outStr = formate_number(eval(self.tStr)) if self.symbol in ['+', '-'] else outStr
        self.setOutput(outStr)
        self.ifPress = False

    def markHandler(self, mark):
        print(mark)
        if mark == '=':
            self.equal()
        if mark == '.':
            self.period()
        if mark == 'BackSpace':
            self.outStr.set(BackSpace(self.outStr.get()))
        if mark == 'clear':
            self.clear()
        if mark == 'swith':
            self.eStrTemp = swith(self.equal())
            self.outStr.set(self.eStrTemp)
            self.lastSymbol = self.symbol
            self.symbol = ''
        if mark == 'sqrt':
            eStr = self.eStr.get()
            outStr = '√({0})'.format(self.outStr.get())
            self.eStr.set(str(eStr) + str(outStr))
            self.tStr = str(self.eStr.get())
            self.outStr.set(str(eval(self.formateExpression(self.tStr))))
            self.symbol = ''
            self.lastSymbol = ''
        if mark == 'square':
            eStr = self.eStr.get()
            outStr = '({0})²'.format(self.outStr.get())
            self.eStr.set(str(eStr) + str(outStr))
            self.tStr = str(self.eStr.get())
            self.outStr.set(str(eval(self.formateExpression(self.tStr))))
            self.symbol = ''
            self.lastSymbol = ''

    def equal(self):
        # 汇总表达式
        outStr = self.outStr.get()
        if not outStr.startswith('%'):
            tStr = (self.tStr + self.lastSymbol + outStr) if (self.lastSymbol and outStr != '0') else self.tStr or '0'
            tStr = self.formateExpression(tStr)
        else:
            self.eStr.set('错误指令')
            self.symbol = 'e'
            return
        # 计算并输出结果
        print(tStr)
        result = formate_number(eval(tStr))
        self.setOutput(result)

        # 清空提示屏
        self.eStr.set('')
        self.eStrTemp = result
        # 清空符号
        self.lastSymbol = ''
        self.symbol = 'e'
        self.ifPress = False
        # 清空表达式
        self.tStr = ''
        return result

    def period(self):
        outStr = self.outStr.get()
        mark = '.'
        # 还原表达式
        if self.symbol == 'e':
            self.eStr.set('')
        if self.eStrTemp and self.eStrTemp != '0' and self.symbol != 'e':
            self.eStr.set(self.eStrTemp)
            self.eStrTemp = ''
        # 如果没有输入过运算符
        if not (self.symbol or self.lastSymbol):
            self.eStr.set('')
        if self.symbol:
            outStr = '0'

        if outStr.startswith('%'):
            if outStr == '%':
                outStr = '0.'
            else:
                outStr += mark
        else:
            if outStr == '-':
                outStr = '-0.'
            elif mark in outStr:
                return
            else:
                outStr += mark
        self.setOutput(outStr)
        self.symbol = ''

    def clear(self):
        self.outStr.set('0')
        self.eStr.set('')
        self.eStrTemp = ''
        self.ifPress = False
        self.lastSymbol = ''
        self.symbol = 'e'
        self.tStr = ''
