# !/usr/bin/env python
# encoding: utf-8

'''

@author: senlian

@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.

@file: calculator.py

@time: 2018/5/13 13:29

@module:python -m pip install 

@desc:
'''
import tkinter as tk
import re
from decimal import Decimal
from settings import Public, MainPage, KeyBoar,sqrt

# 数字
reNumber = re.compile('[\d\.]+')
# +-*/%
reOperator = re.compile('(?P<operator>([(χ²)(±)\+\-×÷﹪√\(\)]))')


class Calculator(object):
    def __init__(self, master):
        self.root = master
        self.root.title('计算器')
        self.root.update()
        # 大小固定
        self.root.pack_propagate(0)

        # 副显示屏
        self.subLCD = tk.StringVar()
        self.subLCD.set('')
        # 主显示屏
        self.mainLCD = tk.StringVar()
        self.mainLCD.set(0)

        # digitBtn,数字形态,0-9, .
        self.digitColor = tk.StringVar()
        self.digitState = tk.StringVar()
        # operatorBtn,运算符号形态, +, -, *, /, %, √, χ², (, ), ±
        self.operatorColor = tk.StringVar()
        self.operatorState = tk.StringVar()
        # symbolBtn,功能符号形态, C, ←, =
        self.symbolColor = tk.StringVar()
        self.symbolState = tk.StringVar()
        # 左括号，用于记录括号是否成对
        self.bracketleftVar = tk.StringVar()
        self.bracketleftVar.set('(')

        # 存入元素
        self.digitBtn = []
        self.operatorBtn = []
        self.symbolBtn = []

        # 运算符号记录
        self.operatorOld = True
        self.operatorNow = True
        # 括号记录
        self.bracketleft = 0

        # 标记按钮是否按下
        self.digitPress = False
        self.operatorPress = True
        self.symbolPress = False

        # TODO: 计算器界面
        self.calculator()

    def calculator(self):
        calculatorFrame = tk.Frame(self.root, width=MainPage.width, height=MainPage.height)
        calculatorFrame.pack()
        calculatorFrame.update()
        # 显示器
        scrennFrame = self.screen(calculatorFrame)
        # 按键
        self.keyboardFrame = self.keyboard(calculatorFrame)
        return calculatorFrame

    # TODO: 屏幕定义
    def screen(self, father):
        scrennFrame = tk.Frame(father, width=MainPage.width, height=MainPage.height)
        scrennFrame.pack()
        scrennFrame.update()

        self.addLable(scrennFrame, 14, self.subLCD)
        self.addLable(scrennFrame, 28, self.mainLCD)
        self.addLable(scrennFrame, 1, None, bg=None, bw=0)
        return scrennFrame

    def addLable(self, father, fontsize=28, content='', bg='#E0E0E0', bw=8):
        newLable = tk.Label(father, width=MainPage.width)
        newLable['height'] = 2
        newLable['borderwidth'] = bw
        newLable['bg'] = bg
        newLable['fg'] = 'black'
        newLable['anchor'] = 'se'
        newLable['font'] = ('Times New Roman', fontsize, 'bold')
        newLable['textvariable'] = content
        # 达到限制长度换行
        newLable['wraplength'] = MainPage.width
        # 换行对齐方式
        newLable['justify'] = 'right'
        newLable.pack()
        newLable.update()

        return newLable

    # TODO: 按键定义
    def keyboard(self, father):
        keyboardFrame = tk.Frame(father, width=MainPage.width)
        keyboardFrame.pack()
        keyboardFrame.focus_set()
        keyboardFrame.update()
        # TODO: 初始状态设定
        self.symbolColor.set('#F0F0F0')
        self.operatorColor.set('#F0F0F0')
        self.digitColor.set('white')

        self.symbolState.set('normal')
        self.operatorState.set('normal')
        self.digitState.set('normal')

        # TODO: 功能型按钮
        for index, mark in enumerate(['C', '←']):
            btn = self.addButton(keyboardFrame, text=mark, row=index, col=0, colspan=1, width=4,
                                 bg=self.symbolColor.get(),
                                 state=self.symbolState.get())

            self.symbolBtn.append(btn)

        # TODO: 运算符
        for index, mark in enumerate(['﹪', '√', 'χ²']):
            btn = self.addButton(keyboardFrame, text=mark, row=0, col=index + 1, colspan=1, width=4,
                                 bg=self.operatorColor.get(),
                                 state=self.operatorState.get())
            self.operatorBtn.append(btn)

        for index, mark in enumerate(['(', ')']):
            btn = self.addButton(keyboardFrame, text=mark, row=1, col=index + 1, colspan=1, width=4,
                                 bg=self.operatorColor.get(),
                                 state=self.operatorState.get())
            self.operatorBtn.append(btn)

        for index, mark in enumerate(['÷', '×', '-', '+']):
            btn = self.addButton(keyboardFrame, text=mark, row=index + 1, col=3, colspan=1, width=4,
                                 bg=self.operatorColor.get(),
                                 state=self.operatorState.get())
            self.operatorBtn.append(btn)

        # TODO: 数字键盘
        for number in range(9, -1, -1):
            row = (5 if number == 0 else (2 if (number / 3) > 2 else(3 if (number / 3) > 1 else 4)))
            column = (1 if number == 0 else int((number - 1) % 3))
            btn = self.addButton(keyboardFrame, text=number, row=row, col=column, colspan=1, width=4,
                                 bg=self.digitColor.get(),
                                 state=self.digitState.get())
            self.digitBtn.append(btn)

        for index, mark in enumerate(['±', '.', '=']):
            column = (index + 1) if index != 0 else 0
            color = self.operatorColor.get() if index == '±' else self.symbolColor.get()
            state = self.operatorState.get() if index == '±' else self.symbolState.get()

            btn = self.addButton(keyboardFrame, text=mark, row=5, col=column, colspan=1, width=4, bg=color,
                                 state=state)
            if mark == '±':
                self.operatorBtn.append(btn)
            elif mark == '.':
                self.digitBtn.append(btn)
            else:
                self.symbolBtn.append(btn)
        return keyboardFrame

    def addButton(self, father, text='0', row=0, col=0, colspan=1, width=4, bg='#F0F0F0', state='normal', fsize=24):
        newButton = tk.Button(father)
        newButton['width'] = int(width)
        newButton['height'] = 1
        newButton['borderwidth'] = 1
        newButton['background'] = bg

        newButton['state'] = state
        newButton['anchor'] = 'center'
        newButton['text'] = str(text)
        if str(text) == '(':
            newButton['textvariable'] = self.bracketleftVar
        newButton['foreground'] = 'black'
        newButton['activeforeground'] = 'red'
        newButton['font'] = ('Times New Roman', int(fsize), 'bold')
        newButton.grid(row=int(row), column=int(col), columnspan=int(colspan), padx=1, pady=3)

        color = 'lightgray' if bg == 'white' else 'skyblue'
        funcPress = self.keyRelease if text == '←' else self.switchColor
        funcRelease = self.switchColor if text == '←' else self.keyRelease
        # TODO: 鼠标事件
        # 鼠标进入
        newButton.bind('<Enter>', lambda e: self.switchColor(e, newButton, color))
        # 鼠标离开
        newButton.bind('<Leave>', lambda e: self.switchColor(e, newButton, bg))
        # 鼠标点击
        newButton.bind('<ButtonPress-1>', lambda e: funcPress(e, newButton, color))
        # 鼠标释放
        newButton.bind('<ButtonRelease-1>', lambda e: funcRelease(e, newButton, bg))

        # TODO： 键盘事件，绑定键盘按键
        KeyEvents = KeyBoar.KeyTable.get(text, text)
        KeyEvents = KeyEvents if type(KeyEvents) == list else [KeyEvents]
        for key in KeyEvents:
            KeyPress = '<KeyPress-{key}>'.format(key=key)
            KeyRelease = '<KeyRelease-{key}>'.format(key=key)
            try:
                newButton.bind_all(KeyPress, lambda e: funcPress(e, newButton, color))
                newButton.bind_all(KeyRelease, lambda e: funcRelease(e, newButton, bg))
            except:
                # print(text, key)
                pass
        return newButton

    # TODO: 颜色切换
    def switchColor(self, e, btn, color):
        btn['bg'] = color
        btn.update()

    # TODO: 键盘或鼠标激活按钮
    def keyRelease(self, e, btn, color):
        text = btn['text'] or '='
        # 特殊处理左括号
        text = '(' if '(' in text else text
        # 设置按钮按下后的颜色
        btn['background'] = color
        btn.update()
        self.response(text)

    # TODO: 激活事件效应
    def response(self, request):
        # TODO: 数字或者小数点
        if reNumber.findall(request):
            self.digitHandler(request)
        # TODO: 运算符
        elif reOperator.findall(request):
            self.operatorHandler(request)
        # TODO: 功能符号
        else:
            print(request)
            return
            # 等号处理
            oldText = self.subLCD.get()
            if self.digitPress or not oldText:
                oldText += self.mainLCD.get()
            oldText = oldText[:-1] if reOperator.findall(oldText[-1]) else oldText
            self.setMainLCD(self.doEval(oldText))
            self.setSubLCD('')
            self.symbolPress = True
            self.digitPress = False
            self.operatorColor = False
            self.symbolNow = True
            self.symbolOld = True
            self.bracketleft = 0
            self.resetBracketBtn()

    # TODO: 数字或小数点处理
    def digitHandler(self, digit):
        # 有运算符操作，则重置数字输入
        if self.operatorPress:
            self.setMainLCD(digit)
        else:
            if self.operatorOld:
                oldText = self.mainLCD.get()
            else:
                # 清空旧表达式
                self.setSubLCD('')
                oldText = '0'
                # 重置符号，保证数字连续输入
                self.operatorOld = True

            oldText = oldText if (oldText != '0' or digit == '.') else ''
            # 重复输入小数点不做处理
            if digit == '.' and (digit in oldText):
                return oldText
            newText = oldText + digit
            self.setMainLCD(newText)

        # 数字键标记为输入状态
        self.digitPress = True
        # 运算符重置
        self.operatorPress = False
        self.operatorNow = ''
        # 功能符重置
        self.symbolPress = False

    # TODO: 运算符处理, re.compile('(?P<operator>([(χ²)(±)\+\-×÷﹪√\(\)]))')
    def operatorHandler(self, mark):
        # 旧的表达式
        oldText = self.subLCD.get() or ''
        text = oldText
        # 新的输入
        newText = self.mainLCD.get() or '0'
        if re.findall('[\+\-×÷﹪]', mark):
            text, newText = self.operatorGeneral(mark, oldText, newText, text)
        elif mark == '(':
            text, newText = self.operatorBracketLeft(mark, oldText, newText, text)
        elif mark == ')':
            text, newText = self.operatorBracketRight(mark, oldText, newText, text)
        elif mark == '√':
            text, newText = self.operatorSqrt(mark, oldText, newText, text)
        elif mark == 'χ²':
            text, newText = self.operatorSquaret(mark, oldText, newText, text)
        else:
            text, newText = self.operatorSwitch(mark, oldText, newText, text)

        self.setSubLCD(text)
        self.setMainLCD(newText)

    # TODO: +-*/﹪运算符处理
    def operatorGeneral(self, mark, oldText, newText, text):
        self.operatorNow = mark
        if self.digitPress:
            text = oldText + newText + mark
            newText = self.doEval(oldText + newText)
        else:
            if oldText:
                # 判断旧的表达式是否以运算符结尾
                oldText = oldText[:-1] if self.operatorOld else oldText
                text = oldText + mark
                newText = self.doEval(oldText)
            else:
                text = newText + mark
        self.operatorOld = mark
        self.operatorPress = True
        self.digitPress = False
        self.symbolPress = False
        return text, newText

    # TODO: 左括号(处理
    def operatorBracketLeft(self, mark, oldText, newText, text):
        # 没有进行过计算或没有数字键输入，重值主屏显示内容
        if not self.digitPress and self.operatorOld:
            newText = '0'
        if not oldText or (not re.findall('[0123456789\)]', oldText[-1])):
            self.operatorNow = mark
            text = oldText + mark
            self.bracketleft += 1
            self.resetBracketLeftBtn()
            # 标记数字按键需要重新输入
            self.operatorPress = True
            # 标记运算符需要加上mainCLD
            self.digitPress = True
            # 功能符标记为空
            self.symbolPress = False
            # TODO: 运算符标记，表示表达式可以继续添加
            self.operatorOld = True

        return text, newText

    # TODO: 右括号)处理
    def operatorBracketRight(self, mark, oldText, newText, text):
        # 必须有左括号存在
        if self.bracketleft > 0:
            # if (oldText and oldText[-1].isdigit()) or (mark == self.symbolNow):
            # 前边只能是数字或者右括号)
            if (self.digitPress and self.operatorNow != '(') or (mark == self.operatorNow) or self.operatorOld:
                self.operatorNow = mark
                if self.digitPress:
                    text = oldText + newText + mark
                elif self.operatorOld:
                    text = oldText[:-1] + mark
                else:
                    text = oldText + mark
                self.bracketleft -= 1
                self.resetBracketLeftBtn()
                newText = self.doEval(text)
                # 标记数字按键需要重新输入
                self.operatorPress = True
                self.digitPress = False
                self.symbolPress = False
                # TODO: 运算符为空
                self.operatorOld = False

        return text, newText

    # TODO: 根号√处理
    def operatorSqrt(self, mark, oldText, newText, text):
        if not self.operatorOld:
            return
        self.operatorNow=mark
        text = oldText + mark + '('
        self.bracketleft += 1
        self.resetBracketLeftBtn()
        self.operatorOld = mark

        self.digitPress = False
        self.operatorPress = True
        self.symbolPress = False
        return text, newText

    # TODO: 平方χ²处理
    def operatorSquaret(self, mark, oldText, newText, text):
        return text, newText

    # TODO: 正负转换处理
    def operatorSwitch(self, mark, oldText, newText, text):
        return text, newText

    # TODO: 更改左括号按钮显示符号
    def resetBracketLeftBtn(self):
        for btn in self.operatorBtn:
            if re.findall('[\(\+]+', btn['text']):
                if self.bracketleft > 0:
                    # ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
                    number = str(self.bracketleft).replace('0', '₀')
                    number = number.replace('1', '₁')
                    number = number.replace('2', '₂')
                    number = number.replace('3', '₃')
                    number = number.replace('4', '₄')
                    number = number.replace('5', '₅')
                    number = number.replace('6', '₆')
                    number = number.replace('7', '₇')
                    number = number.replace('8', '₈')
                    number = number.replace('9', '₉')
                    btn['fg'] = 'blue'
                    return self.bracketleftVar.set('(' + number)
                else:
                    btn['fg'] = 'black'
                    btn['state'] = 'normal'
                    return self.bracketleftVar.set('(')

    # TODO: 设置主屏显示内容
    def setMainLCD(self, text):
        self.mainLCD.set(text)

    # TODO: 设置主屏显示内容
    def setSubLCD(self, text):
        self.subLCD.set(text)

    # TODO: 计算表达式
    def doEval(self, expression):
        expression = self.preEval(expression)
        print(expression)
        try:
            result = eval(expression)
            return str(result if result != 0 else 0)
        except Exception as e:
            print(e)
            return self.mainLCD.get() or '0'

    # TODO: 格式化表达式
    def preEval(self, expression):
        decimalRule = r'(?P<decimal>(\d+\.\d+))'
        expression = re.sub(decimalRule, self.decimalHandler, str(expression))
        expression = reOperator.sub(self.operatorGet, expression)
        return expression

    # TODO: 小数处理，解决浮点数运算错误问题
    def decimalHandler(self, rule):
        decimalNum = rule.group(r'decimal')
        return "Decimal('{item}')".format(item=decimalNum)

    # TODO: 获得正确的计算符号
    def operatorGet(self, rule):
        operator = rule.group(r'operator')
        return KeyBoar.markTable.get(operator, operator)
