    def inputHandler(self, length=5, inputStr=''):
        if self.symbol:
            if not self.outStr.get().startswith('%'):
                self.outStr.set('0')
            if self.symbol == 'e':
                self.eStr.set('')
            self.keyState.set('normal')
            self.keyColor.set('white')
            self.symbol = None

        estrOld = self.eStr.get()
        outStrOld = self.outStr.get()

        print('*' * 20)
        print('estrOld=', estrOld)
        print('symbol=', self.symbol)
        print('outStrOld=', outStrOld)
        print('inputStr=', inputStr)
        print('*' * 20)

        if inputStr in SYBOL_LIST:
            # 获取符号
            mark = SYBOL_LIST[inputStr]
            # 小数点特殊处理
            if mark == '.' and inputStr not in outStrOld:
                self.outStr.set(outStrOld + inputStr)
                return self.outStr.get()
            elif mark == '-':
                # 负号
                if (estrOld + outStrOld) == '0':
                    self.outStr.set(inputStr)
                    return self.outStr.get()
                # 减号
                else:
                    self.eStr.set((estrOld or '') + (
                        ((self.symbol or '') + (outStrOld or '') + mark) if outStrOld != '0' else ''))
                    # 运算符改变
                    self.symbol = mark
                    return
            elif mark == '%':
                # 作为密码开头
                if (estrOld + outStrOld) == '0':
                    self.outStr.set(mark)
                    return self.outStr.get()
                # 取余处理
                else:
                    self.eStr.set((estrOld or '') + (self.symbol or '') + (outStrOld or '') + mark)
                    self.symbol = mark
            elif mark in ['*', '/', '+']:
                self.eStr.set((estrOld or '') + (self.symbol or '') + (outStrOld or '') + inputStr)
                self.symbol = mark
            elif mark == 'clear':
                cmd = mark + '(' + self.outStr.get() + ')'
                self.outStr.set(eval(cmd))
        else:
            self.outStr.set((outStrOld if outStrOld != '0' else '') + inputStr)
        return

    def joinExpression(self, mark, old, new):
        if not old:
            if not new:
                return old
            old = new
            new = ''

        if mark in ['sqrt', 'square', 'cube', 'swith', 'bracket']:
            return mark + '(' + old + ')'
        elif mark == '=':
            return equal(old + ' ' + new)
        else:
            return old + ' ' + new + ' ' + str(mark)
